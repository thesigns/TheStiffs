"""Silnik walki i pościgu (Rules.md: *Walka*, *Pościg*).

Starcie to state["starcie"]. Jedna komenda gracza = jedna wymiana:
najpierw akcja postaci (test), potem ruch sztywnych. Przy złym wyniku
i dostępnym Farcie wymiana czeka na decyzję gracza.

Strefy: 1 daleko, 2 blisko, 3 na wyciągnięcie ręki, 4 uchwycony.
Strefa 0 oznacza, że sztywny zgubił postać.
"""

import math

from . import actions, rules, world
from .core import GameError, load_json, rng

ZONES = {0: "zgubiony", 1: "daleko", 2: "blisko", 3: "na wyciągnięcie ręki",
         4: "TRZYMA"}
STAGES = {"swiezak": "świeżak", "gnilec": "gnilec"}

# Skalibrowane w sim.py (zestaw E, 2026-11-03). Cele: Rules.md, *Otwarte kwestie*.
MOVE_CHANCE = {"swiezak": 100, "gnilec": 50}     # % na wymianę
GRAB_CHANCE = {"swiezak": 75, "gnilec": 50}
BITE_CHANCE = {"swiezak": 50, "gnilec": 35}
BITE_ON_GRAB = {"swiezak": 60, "gnilec": 30}   # ugryzienie od razu przy chwycie
CRIPPLED_MOVE = 0.5
CRIPPLED_GRAB = -15
TEAR_APART_HOLDERS = 3
TEAR_APART_CHANCE = 25
ATTACK_STAGE_STEPS = {"swiezak": -2, "gnilec": 1}
EYES_STEPS = 1           # oczy łatwiej trafić niż mózg, ale to nie rozstrzyga starcia
BLIND_MOVE = 0.5         # ślepy idzie tylko za dźwiękiem
BLIND_GRAB = -25
BITE_PLACES = [("reka", 45), ("tulow", 20), ("noga", 20), ("glowa", 15)]
SECONDS_PER_EXCHANGE = 6

# Akcje gracza: nazwa komendy → identyfikator w katalogu akcji.
TESTED = {"atak": "atak", "strzal": "strzal", "odepchnij": "odepchniecie",
          "wyrwij": "wyrwanie", "biegnij": "bieg", "zgub": "zgubienie",
          "drzwi": "zamkniecie_drzwi", "wspinaj": "ucieczka_w_gore"}
FREE = {"czekaj", "przeladuj", "bron", "wyciagnij"}


def weapons():
    return {k: v for k, v in load_json("weapons.json").items()
            if not k.startswith("_")}


def d100():
    return rng().randint(1, 100)


# --- dostęp do starcia --------------------------------------------------------

def current(state):
    fight = state.get("starcie")
    if not fight:
        raise GameError("Nie trwa żadne starcie.")
    return fight


def alive_stiffs(fight):
    return [s for s in fight["sztywni"] if s["strefa"] > 0]


def holders(fight):
    return [s for s in fight["sztywni"] if s["strefa"] == 4]


def find(fight, sid):
    for s in fight["sztywni"]:
        if s["id"] == sid and s["strefa"] > 0:
            return s
    raise GameError(f"Nie ma w starciu sztywnego #{sid}.")


def weapon_item(state, fight):
    wid = fight.get("bron", "piesci")
    if wid == "piesci":
        return None
    for item in state["ekwipunek"]:
        if wid in item.get("daje", []) and actions.reachable(state, item):
            return item
    return None


def weapon_spec(state, fight, melee=True):
    wid = fight.get("bron", "piesci")
    specs = weapons()
    if fight.get("zaklinowana") or (wid != "piesci"
                                    and not weapon_item(state, fight)):
        return "piesci", specs["piesci"]
    spec = specs[wid]
    if melee and spec.get("palna"):
        return "kolba", specs["kolba"]
    return wid, spec


# --- start ---------------------------------------------------------------------

def start(state, swiezaki, gnilce, zone, weapon="piesci", descriptions=None,
          ambush=False):
    if state.get("starcie"):
        raise GameError("Starcie już trwa.")
    actions.living_character(state)
    state["ukrycie"] = False
    if swiezaki + gnilce < 1:
        raise GameError("Starcie wymaga co najmniej jednego sztywnego.")
    if zone not in (1, 2, 3, 4):
        raise GameError("Strefa startowa: 1–4.")
    descriptions = list(descriptions or [])
    stiffs = []
    for i, stage in enumerate(["swiezak"] * swiezaki + ["gnilec"] * gnilce):
        stiffs.append({
            "id": i + 1, "etap": stage, "strefa": zone,
            "opis": descriptions[i] if i < len(descriptions) else "",
            "okaleczony": False, "blokada": 0,
        })
    fight = {"wymiana": 0, "sztywni": stiffs, "bron": "piesci",
             "zaklinowana": False, "czeka": None, "pokonani": 0,
             "zgubieni": 0, "za_drzwiami": 0}
    state["starcie"] = fight
    if weapon != "piesci":
        set_weapon(state, fight, weapon)
    out = []
    if ambush:
        # Zasadzka: sztywni mają wolną wymianę, zanim postać zareaguje.
        out.append(("alarm", "Zasadzka! Sztywni są szybsi."))
        out += stiffs_phase(state, fight, moved=False, pushed=set())
        out += end_check(state)
    return out


def add_stiff(state, spec, zone):
    """Nowy sztywny dołącza do trwającego starcia."""
    fight = current(state)
    new_id = max((s["id"] for s in fight["sztywni"]), default=0) + 1
    stiff = {"id": new_id, "etap": spec["etap"], "strefa": zone,
             "opis": spec.get("opis", ""), "okaleczony": False, "blokada": 0}
    for key in ("cialo", "znajomy", "znany"):
        if key in spec:
            stiff[key] = spec[key]
    fight["sztywni"].append(stiff)
    return stiff


def status_lines(state):
    """Położenie sztywnych i możliwości gracza (do wypisania)."""
    fight = state.get("starcie")
    if not fight:
        return []
    out = [("info", "")]
    wid, spec = weapon_spec(state, fight, melee=False)
    weapon = spec["nazwa"]
    if fight.get("zaklinowana"):
        weapon += " (zaklinowana/zacięta!)"
    if spec.get("palna"):
        item = weapon_item(state, fight)
        weapon += f", w komorze: {item.get('zaladowane', 0)}"
    char = state["postac"]
    out.append(("czas", f"W ręku: {weapon}. Zmęczenie {char['zmeczenie']}, "
                        f"nerwy {char['nerwy']}, Fart {char['fart']}."))
    for s in alive_stiffs(fight):
        flags = []
        if s["okaleczony"]:
            flags.append("okaleczony")
        if s.get("slepy"):
            flags.append("ślepy")
        if s["blokada"]:
            flags.append("za drzwiami")
        desc = f" – {s['opis']}" if s["opis"] else ""
        out.append(("zagrozenie" if s["strefa"] >= 3 else "info",
                    f"#{s['id']} {STAGES[s['etap']]}: {ZONES[s['strefa']]}"
                    + (f" ({', '.join(flags)})" if flags else "") + desc))
    if fight.get("czeka"):
        out.append(("fart", "Czeka na decyzję: fight.py fart albo przyjmij."))
        return out
    out.append(("naglowek", "Możliwości (fight.py):"))
    for cmd, label, chance in options(state):
        out.append(("info", f"  {cmd.ljust(14)} {label}"
                            + (f": {chance}% ({rules.label(chance)})"
                               if chance else "")))
    return out


def set_weapon(state, fight, wid):
    specs = weapons()
    if wid not in specs or wid == "kolba":
        raise GameError(f"Nieznana broń „{wid}”. Znane: "
                        + ", ".join(k for k in specs if k != "kolba") + ".")
    if wid != "piesci" and wid not in actions.provided(state):
        raise GameError(f"Postać nie ma pod ręką: {specs[wid]['nazwa']}.")
    fight["bron"] = wid
    fight["zaklinowana"] = False


# --- wyceny akcji w walce ----------------------------------------------------

def default_target(fight, kind):
    hs = holders(fight)
    if hs:
        return hs[0]
    near = sorted(alive_stiffs(fight), key=lambda s: -s["strefa"])
    if not near:
        return None
    if kind == "strzal":
        return near[0]
    return near[0] if near[0]["strefa"] == 3 else None


def quote(state, cmd, target_id=None, burst=False, eyes=False):
    """Zwraca (wycena, cel) albo zgłasza GameError, gdy akcja niemożliwa."""
    fight = current(state)
    cat = actions.catalog()
    extra = []
    target = None
    grabbed = bool(holders(fight))
    node = world.current_node(state) or {}
    if eyes and cmd not in ("atak", "strzal"):
        raise GameError("W oczy można tylko uderzyć albo strzelić.")

    if cmd in ("atak", "strzal", "odepchnij"):
        target = (find(fight, target_id) if target_id
                  else default_target(fight, cmd))
        if not target:
            raise GameError("Nie ma celu w zasięgu.")
        if grabbed and target["strefa"] != 4 and cmd != "strzal":
            raise GameError("Postać jest trzymana; może atakować tylko "
                            "trzymającego, wyrwać się albo strzelać.")
        if cmd != "odepchnij":
            extra.append((f"cel: {STAGES[target['etap']]}",
                          ATTACK_STAGE_STEPS[target["etap"]]))
        if eyes:
            if target.get("slepy"):
                raise GameError(f"#{target['id']} już nic nie widzi.")
            extra.append(("cel: oczy", EYES_STEPS))

    if cmd == "atak":
        wid, spec = weapon_spec(state, fight, melee=True)
        if target["strefa"] not in spec["strefy"] and target["strefa"] != 4:
            raise GameError(f"{spec['nazwa']}: cel poza zasięgiem.")
        extra.append((f"broń: {spec['nazwa']}", spec["mozg"]
                      + spec.get("mozg_strefa", {}).get(str(target["strefa"]), 0)))
        if target["strefa"] == 4 and not spec.get("krotka"):
            extra.append(("długa broń w zwarciu", -2))
    elif cmd == "strzal":
        wid, spec = weapon_spec(state, fight, melee=False)
        if not spec.get("palna"):
            raise GameError("Postać nie trzyma broni palnej.")
        item = weapon_item(state, fight)
        need = 3 if burst else 1
        if burst and not spec.get("seria"):
            raise GameError(f"{spec['nazwa']} nie strzela serią.")
        if item.get("zaladowane", 0) < need:
            raise GameError(f"{spec['nazwa']}: brak nabojów w komorze. "
                            "Przeładuj.")
        if target["strefa"] not in spec["strefy"] + [4]:
            raise GameError(f"{spec['nazwa']}: cel poza zasięgiem.")
        extra.append((f"broń: {spec['nazwa']}", spec["mozg"]
                      + spec.get("mozg_strefa", {}).get(str(target["strefa"]), 0)))
        if burst:
            extra.append(("seria", 1))
        if grabbed and not spec.get("krotka"):
            extra.append(("długa broń w zwarciu", -2))
    elif cmd == "odepchnij":
        if target["strefa"] != 3:
            raise GameError("Odepchnąć można sztywnego na wyciągnięcie ręki.")
        if target["etap"] == "swiezak":
            extra.append(("świeżak", -1))
    elif cmd == "wyrwij":
        if not grabbed:
            raise GameError("Nikt nie trzyma postaci.")
        more = len(holders(fight)) - 1
        if more:
            extra.append((f"trzyma jeszcze {more}", -more))
    elif cmd in ("biegnij", "zgub", "drzwi", "wspinaj"):
        if grabbed:
            raise GameError("Postać jest trzymana. Najpierw trzeba się "
                            "wyrwać.")
        if cmd == "zgub":
            if any(s["strefa"] >= 3 for s in alive_stiffs(fight)):
                raise GameError("Sztywny jest za blisko, żeby go zgubić.")
            if not node.get("kryjowki", True):
                raise GameError("Tu nie ma gdzie się ukryć.")
            if any(s["strefa"] == 2 and not s.get("slepy")
                   for s in alive_stiffs(fight)):
                extra.append(("pościg blisko", -2))
        if cmd == "drzwi" and node.get("drzwi", "zwykle") == "brak":
            raise GameError("Tu nie ma drzwi do zatrzaśnięcia.")
    else:
        raise GameError(f"Nieznana akcja walki „{cmd}”.")

    approach = "szybko" if cmd == "drzwi" else "normalnie"
    q = actions.build_quote(state, cat, TESTED[cmd], approach,
                            extra_steps=extra)
    return q, target


def options(state):
    """Lista (komenda, opis, szansa albo None) dla bieżącej wymiany."""
    fight = current(state)
    out = []
    for cmd in TESTED:
        try:
            q, target = quote(state, cmd)
        except GameError:
            continue
        label = q["nazwa"] + (f" → #{target['id']}" if target else "")
        out.append((cmd, label, q["szansa"]))
    for cmd in ("atak", "strzal"):
        try:
            q, target = quote(state, cmd, eyes=True)
        except GameError:
            continue
        out.append((cmd + " --oczy", q["nazwa"] + f" w oczy → #{target['id']}",
                    q["szansa"]))
    out.append(("czekaj", "Nic nie rób", None))
    wid, spec = weapon_spec(state, fight, melee=False)
    if spec.get("palna"):
        item = weapon_item(state, fight)
        if item and item.get("zaladowane", 0) < spec["magazynek"]:
            out.append(("przeladuj", "Przeładuj broń", None))
    if fight.get("zaklinowana"):
        out.append(("wyciagnij", "Wyciągnij zaklinowaną broń", None))
    out.append(("bron <rodzaj>", "Zmień broń", None))
    return out


# --- wymiana -----------------------------------------------------------------

def act(state, cmd, target_id=None, burst=False, arg=None, eyes=False):
    """Wykonuje akcję gracza. Zwraca listę (rodzaj, tekst)."""
    fight = current(state)
    out = []
    if fight.get("czeka"):
        out += accept(state, use_fart=False)
        if not state.get("starcie"):
            return out
    char = actions.living_character(state)
    fight["wymiana"] += 1
    out.append(("naglowek", f"Wymiana {fight['wymiana']}"))

    if cmd in FREE:
        out += free_action(state, fight, cmd, arg)
        out += stiffs_phase(state, fight, moved=False, pushed=set())
        return out + end_check(state)

    q, target = quote(state, cmd, target_id, burst, eyes)
    u = d100()
    g = rules.grade(u, q["szansa"], q["podejscie"])
    if q["szansa"] >= 95:
        u = None
    pending = {"cmd": cmd, "akcja": q["akcja"], "szansa": q["szansa"],
               "u": u, "stopien": g, "cel": target["id"] if target else None,
               "seria": burst, "oczy": eyes, "x": d100(), "y": d100(),
               "umiejetnosc": q["umiejetnosc"]}
    steps = ", ".join(f"{s} {rules.signed(v)}" for s, v in q["kroki"])
    roll_text = "bez rzutu" if u is None else f"wypadło {u}"
    out.append(("info", f"{q['nazwa']}: {q['szansa']}% "
                        f"({steps or 'bez modyfikatorów'}), {roll_text} → "
                        f"{rules.GRADE_NAMES[g]}"))
    if q["szansa"] <= rules.MARK_THRESHOLD:
        actions.add_mark(char, q["umiejetnosc"])
    if g != "czysty" and char.get("fart", 0) > 0:
        fight["czeka"] = pending
        out.append(("fart", f"Fart: {char['fart']}. Gracz może zmienić wynik "
                            f"na {rules.GRADE_NAMES[rules.grade_up(g)]} "
                            "(fart) albo przyjąć (przyjmij / następna akcja)."))
        return out
    return out + resolve(state, fight, pending, g)


def accept(state, use_fart):
    fight = current(state)
    pending = fight.get("czeka")
    if not pending:
        raise GameError("Żaden wynik nie czeka na decyzję.")
    g = pending["stopien"]
    out = []
    if use_fart:
        new = rules.grade_up(g)
        state["postac"]["fart"] -= 1
        out.append(("fart", f"Fart: {rules.GRADE_NAMES[g]} → "
                            f"{rules.GRADE_NAMES[new]}."))
        g = new
    fight["czeka"] = None
    pending["stopien_koncowy"] = g
    return out + resolve(state, fight, pending, g)


def resolve(state, fight, p, g):
    """Skutek akcji gracza, potem ruch sztywnych."""
    out = []
    char = state["postac"]
    cmd = p["cmd"]
    ok = g in ("czysty", "koszt")
    target = None
    if p["cel"]:
        target = next(s for s in fight["sztywni"] if s["id"] == p["cel"])
    moved = False       # gracz zmienił dystans (bieg, wspinaczka)
    pushed = set()      # sztywni, którzy w tej wymianie nie chwytają

    if cmd in ("atak", "strzal"):
        melee = cmd == "atak"
        aim = "oczy" if p.get("oczy") else "mózg"
        wid, spec = weapon_spec(state, fight, melee=melee)
        out += noise(state, spec["halas"])
        if not melee:
            item = weapon_item(state, fight)
            item["zaladowane"] -= 3 if p["seria"] else 1
        if ok:
            if p.get("oczy"):
                target["slepy"] = True
                out.append(("sukces", f"#{target['id']}: oczy zniszczone. "
                                      "Idzie dalej, ale już nic nie widzi."))
            else:
                target["strefa"] = 0
                target["zniszczony"] = True
                fight["pokonani"] += 1
                for body in state.get("ciala", []):
                    if body["id"] == target.get("cialo"):
                        body["stan"] = "zniszczony"
                out.append(("sukces", f"#{target['id']}: mózg zniszczony. "
                                      "Pada i już nie wstanie."))
                pushed.add(target["id"])
            if g == "koszt":
                if melee and p["x"] <= spec.get("klinowanie", 0):
                    fight["zaklinowana"] = True
                    out.append(("koszt", f"{spec['nazwa'].capitalize()} "
                                         "utkwiła w czaszce."))
                elif melee:
                    out += noise(state, spec["halas"] + 1)
                    out.append(("koszt", "Cios był głośniejszy, niż trzeba."))
                else:
                    item = weapon_item(state, fight)
                    if item.get("zaladowane", 0) > 0:
                        item["zaladowane"] -= 1
                    out.append(("koszt", "Poszedł jeszcze jeden nabój."))
        elif g == "porazka":
            if (melee and not spec.get("krotka") and wid != "kolba"
                    and target["strefa"] == 3):
                # Długa broń: nawet chybiony cios odrzuca na dystans.
                target["strefa"] = 2
                pushed.add(target["id"])
                out.append(("porazka", f"#{target['id']}: cios poza {aim}, "
                                       "ale odrzuca go na dystans."))
            elif p["x"] <= 50:
                target["okaleczony"] = True
                out.append(("porazka", f"#{target['id']}: trafienie poza {aim}."
                                       " Okaleczony, ale idzie dalej."))
            else:
                out.append(("porazka", f"#{target['id']}: chybienie albo "
                                       "trafienie bez skutku."))
        else:
            if not melee:
                fight["zaklinowana"] = True
                out.append(("katastrofa", "Zacięcie broni."))
            elif p["x"] <= 50 and wid not in ("piesci", "kolba"):
                item = weapon_item(state, fight)
                item["gdzie"] = state["lokacja"].get("wezel")
                fight["bron"] = "piesci"
                out.append(("katastrofa", f"{spec['nazwa'].capitalize()} "
                                          "wypada z rąk."))
            else:
                target["strefa"] = 4
                out.append(("katastrofa", f"#{target['id']} chwyta postać."))

    elif cmd == "odepchnij":
        if ok:
            target["strefa"] = 2
            pushed.add(target["id"])
            out.append(("sukces", f"#{target['id']} odepchnięty."))
            if g == "koszt":
                out += tire(char, 1)
        elif g == "katastrofa":
            target["strefa"] = 4
            out.append(("katastrofa", f"#{target['id']} chwyta postać."))
        else:
            out.append(("porazka", "Nie udaje się go odepchnąć."))
        out += noise(state, 2)

    elif cmd == "wyrwij":
        if ok:
            for s in holders(fight):
                s["strefa"] = 3
                pushed.add(s["id"])
            out.append(("sukces", "Postać wyrywa się z uchwytu."))
            if g == "koszt":
                out += tire(char, 1)
        else:
            out.append(("porazka", "Nie udaje się wyrwać."))
            if g == "katastrofa":
                out += bite(state, holders(fight)[0], auto=True)
        out += noise(state, 2)

    elif cmd == "biegnij":
        moved = True
        out += tire(char, 1)
        out += noise(state, 1)
        for s in alive_stiffs(fight):
            if s["blokada"]:
                continue
            gain = (g == "czysty" or (ok and (s["etap"] == "gnilec"
                                              or s.get("slepy"))))
            if g == "katastrofa":
                s["strefa"] = min(3, s["strefa"] + 1)
            elif gain:
                s["strefa"] -= 1
        if g == "katastrofa":
            out.append(("katastrofa", "Upadek. Pościg się zbliża."))
            out += wound(state, "noga", "drasniecie")
        else:
            out.append(("info", "Bieg: " + ", ".join(
                f"#{s['id']} {ZONES[s['strefa']]}" for s in fight["sztywni"]
                if not s.get("zniszczony"))))
        for s in fight["sztywni"]:
            if s["strefa"] == 0 and not s.get("zniszczony") \
                    and not s.get("liczony"):
                s["liczony"] = True
                fight["zgubieni"] += 1

    elif cmd == "zgub":
        if ok:
            for s in alive_stiffs(fight):
                s["strefa"] = 0
                s["liczony"] = True
                fight["zgubieni"] += 1
            out.append(("sukces", "Postać znika im z oczu."))
            state["ukrycie"] = True
            if g == "koszt":
                out.append(("koszt", "Długo trzeba było siedzieć bez ruchu."))
                fight["dodatkowe_minuty"] = fight.get("dodatkowe_minuty", 0) + 10
        else:
            out.append(("porazka", "Nadal idą jej śladem."))
            if g == "katastrofa":
                s = max(alive_stiffs(fight), key=lambda s: s["strefa"])
                s["strefa"] = min(3, s["strefa"] + 1)
                out += noise(state, 3)
                out.append(("katastrofa", "Hałas zdradza kryjówkę."))

    elif cmd == "drzwi":
        node = world.current_node(state) or {}
        lock = node.get("drzwi", "zwykle") == "zamek"
        out += noise(state, 3)
        if ok:
            for s in alive_stiffs(fight):
                if s["etap"] == "swiezak" and not lock:
                    s["blokada"] = 1
                    s["strefa"] = 3
                else:
                    s["strefa"] = 0
                    s["liczony"] = True
                    fight["za_drzwiami"] += 1
            out.append(("sukces", "Drzwi zatrzaśnięte"
                                  + (" na zamek." if lock else ".")))
            if any(s["blokada"] for s in alive_stiffs(fight)):
                out.append(("info", "Świeżak umie nacisnąć klamkę. "
                                    "Zatrzyma go to na chwilę."))
        else:
            out.append(("porazka", "Nie zdąża zamknąć drzwi."))
            if g == "katastrofa":
                near = [s for s in alive_stiffs(fight) if s["strefa"] == 3]
                if near:
                    near[0]["strefa"] = 4
                    out.append(("katastrofa", f"#{near[0]['id']} chwyta "
                                              "postać w drzwiach."))

    elif cmd == "wspinaj":
        out += noise(state, 2)
        if ok:
            moved = True
            for s in alive_stiffs(fight):
                if s["etap"] == "gnilec":
                    s["strefa"] = 0
                    s["liczony"] = True
                    fight["zgubieni"] += 1
            out.append(("sukces", "Postać jest wyżej. Gnilce nie wejdą."))
            fresh = [s for s in alive_stiffs(fight) if s["etap"] == "swiezak"]
            for s in fresh:
                s["strefa"] = max(1, s["strefa"] - 1)
                pushed.add(s["id"])
            if fresh:
                out.append(("info", "Świeżak wspina się za nią, ale musi "
                                    "nadrobić dystans."))
        else:
            out.append(("porazka", "Nie udaje się wspiąć."))
            if g == "katastrofa":
                out += wound(state, "noga", "powazna")

    out += stiffs_phase(state, fight, moved, pushed)
    return out + end_check(state)


def free_action(state, fight, cmd, arg):
    out = []
    if cmd == "czekaj":
        out.append(("info", "Postać czeka."))
    elif cmd == "bron":
        set_weapon(state, fight, arg or "piesci")
        out.append(("info", f"W ręku: {weapons()[fight['bron']]['nazwa']}."))
    elif cmd == "wyciagnij":
        if not fight.get("zaklinowana"):
            raise GameError("Broń nie jest zaklinowana.")
        fight["zaklinowana"] = False
        out.append(("info", "Broń znów jest gotowa."))
    elif cmd == "przeladuj":
        wid, spec = weapon_spec(state, fight, melee=False)
        if not spec.get("palna"):
            raise GameError("Postać nie trzyma broni palnej.")
        item = weapon_item(state, fight)
        ammo = [i for i in state["ekwipunek"]
                if spec["amunicja"] in i.get("daje", [])
                and actions.reachable(state, i) and i.get("ilosc", 0) > 0]
        room = spec["magazynek"] - item.get("zaladowane", 0)
        if not ammo or room <= 0:
            raise GameError("Nie ma czym albo nie ma potrzeby przeładować.")
        n = min(room, ammo[0]["ilosc"])
        ammo[0]["ilosc"] -= n
        item["zaladowane"] = item.get("zaladowane", 0) + n
        state["ekwipunek"] = [i for i in state["ekwipunek"]
                              if i.get("ilosc", 1) > 0]
        out.append(("info", f"Załadowano {n}. W broni: {item['zaladowane']}."))
    return out


def stiffs_phase(state, fight, moved, pushed):
    out = []
    # Kto trzymał i kto był blisko na początku tej fazy.
    was_holding = [s for s in holders(fight)]
    was_near = [s for s in alive_stiffs(fight)
                if s["strefa"] == 3 and s["id"] not in pushed
                and not s["blokada"]]
    for s in alive_stiffs(fight):
        if s["blokada"]:
            s["blokada"] -= 1
            if not s["blokada"]:
                out.append(("zagrozenie", f"#{s['id']} otwiera drzwi."))
            continue
        if s["strefa"] < 3 and not moved:
            chance = MOVE_CHANCE[s["etap"]]
            if s["okaleczony"]:
                chance *= CRIPPLED_MOVE
            if s.get("slepy"):
                chance *= BLIND_MOVE
            if d100() <= chance:
                s["strefa"] += 1
                out.append(("zagrozenie", f"#{s['id']} zbliża się: "
                                          f"{ZONES[s['strefa']]}."))
    for s in was_near:
        if s["strefa"] != 3:
            continue
        chance = GRAB_CHANCE[s["etap"]] + (CRIPPLED_GRAB if s["okaleczony"] else 0)
        if s.get("slepy"):
            chance += BLIND_GRAB
        if d100() <= chance:
            s["strefa"] = 4
            out.append(("alarm", f"#{s['id']} chwyta postać!"))
            if d100() <= BITE_ON_GRAB[s["etap"]]:
                out += bite(state, s)
    for s in was_holding:
        if s["strefa"] == 4 and d100() <= BITE_CHANCE[s["etap"]]:
            out += bite(state, s)
    if len(holders(fight)) >= TEAR_APART_HOLDERS and not state["postac"]["martwy"]:
        u = d100()
        if u <= TEAR_APART_CHANCE:
            state["postac"]["martwy"] = True
            state["postac"]["zgon"] = state["czas"]
            out.append(("alarm", f"Rozszarpanie: {u} ≤ {TEAR_APART_CHANCE}. "
                                 "POSTAĆ NIE ŻYJE."))
        else:
            out.append(("alarm", f"Rozszarpanie: {u} > {TEAR_APART_CHANCE}. "
                                 "Jeszcze żyje."))
    return out


def bite(state, stiff, auto=False):
    u = d100()
    total = 0
    place = BITE_PLACES[-1][0]
    for p, w in BITE_PLACES:
        total += w
        if u <= total:
            place = p
            break
    severity = "krytyczna" if place == "glowa" else "powazna"
    char = state["postac"]
    jacket = world.worn(state, "ochrona_tulowia")
    if place in ("reka", "tulow") and jacket:
        u_guard = d100()
        if u_guard <= rules.BODY_GUARD_CHANCE:
            char["nerwy"] = rules.clamp(char["nerwy"] + 1, 0, 10)
            return [("sukces", f"#{stiff['id']} gryzie, ale zęby nie przebijają "
                               f"materiału ({jacket['nazwa']}): "
                               f"{u_guard} ≤ {rules.BODY_GUARD_CHANCE}. "
                               "Nerwy +1.")]
    w = world.add_wound(state, place, severity, ugryzienie=True)
    char["nerwy"] = rules.clamp(char["nerwy"] + 1, 0, 10)
    where = "twarz albo szyja" if place == "glowa" else rules.PLACE_NAMES[place]
    return [("alarm", f"#{stiff['id']} gryzie: {where}. Rana #{w['id']} "
                      f"({rules.SEVERITY_NAMES[w['ciezkosc']]}). Nerwy +1.")]


def wound(state, place, severity):
    w = world.add_wound(state, place, severity)
    return [("cialo", f"Rana #{w['id']}: {rules.wound_name(w)}.")]


def tire(char, n):
    char["zmeczenie"] = rules.clamp(char["zmeczenie"] + n, 0, 5)
    return [("cialo", f"Zmęczenie: {char['zmeczenie']}.")]


def noise(state, level):
    world.make_noise(state, level)
    return []


def end_check(state):
    fight = state["starcie"]
    char = state["postac"]
    if char.get("martwy") or not alive_stiffs(fight):
        return finish(state)
    return []


def finish(state):
    fight = state["starcie"]
    seconds = fight["wymiana"] * SECONDS_PER_EXCHANGE
    minutes = max(1, math.ceil(seconds / 60)) + fight.get("dodatkowe_minuty", 0)
    node = world.current_node(state)
    if node and fight["za_drzwiami"]:
        node["za_drzwiami"] = node.get("za_drzwiami", 0) + fight["za_drzwiami"]
    out = [("naglowek", "Koniec starcia"),
           ("info", f"Pokonani: {fight['pokonani']}, zgubieni: "
                    f"{fight['zgubieni']}, za drzwiami: {fight['za_drzwiami']}."
                    f" Wymian: {fight['wymiana']}.")]
    state["ostatnie_starcie"] = {k: fight[k] for k in
                                 ("wymiana", "pokonani", "zgubieni",
                                  "za_drzwiami")}
    state["starcie"] = None
    if state["postac"].get("martwy"):
        out.append(("alarm", "Postać nie żyje. Pozostaje rise.py."))
        return out
    out += world.pass_time(state, minutes, 0)
    return out
