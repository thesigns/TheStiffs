"""Ciało i doba: jedzenie, woda, sen, zakażenia, choroby, rozliczenie świtu.

Wartości liczbowe opisuje Manual/Rules.md (*Ciało*, *Rozliczenie doby*).
"""

import datetime as dt

from . import rules, world
from .core import d100, rng

# --- stałe ------------------------------------------------------------------

MEALS_PER_DAY = 2            # najwyżej tyle posiłków obniża głód w dobie
WATER_NEED = 2               # litry na dobę
WATER_NEED_SICK = 3          # przy chorobie
PARTIAL_DAY_HOURS = 12       # krótsza doba (start, nowa postać) bez kar

SLEEP_FULL = 360             # minuty: pełny sen
SLEEP_SOME = 180             # minuty: sen, który chroni przed „nocą bez snu”

SMOKE_COOLDOWN = 60          # papieros obniża nerwy najwyżej raz na godzinę
VODKA_MINUTES = 120          # kara −1 krok po wódce

RAW_WATER_SICK = 20          # % szansy na chorobę po surowej wodzie
DISEASES = [("czerwonka", 70), ("dur brzuszny", 30)]
DISEASE_WORSEN = 30
DISEASE_IMPROVE = 30
DISEASE_IMPROVE_WATER = 15   # wypił pełną normę czystej wody
DISEASE_IMPROVE_ANTIBIOTIC = 40
DAILY_DEATH_CHANCE = 15      # stan krytyczny od choroby, sepsy, pragnienia

# Zakażenie rany: dzienne szanse pogorszenia i poprawy.
INFECTION_BASE = 10
INFECTION_BITE = 15
INFECTION_UNDRESSED = 15
INFECTION_SEVERITY = {"drasniecie": 0, "powazna": 5, "krytyczna": 10}
INFECTION_CLEANED = -10
INFECTION_IMPROVE = 20
INFECTION_IMPROVE_DRESSED = 15
INFECTION_IMPROVE_CLEANED = 10
ANTIBIOTIC_INFECTION = 2

# Gojenie: tyle dni opatrzonej rany z zakażeniem najwyżej 1.
HEAL_DAYS = {"drasniecie": 3, "powazna": 10, "krytyczna": 10}
HEAL_INTO = {"drasniecie": None, "powazna": "drasniecie",
             "krytyczna": "powazna"}

FROST_UNTIL = (4, 15)        # przymrozki do połowy kwietnia
FROST_CHANCE = 35
FROST_ENDS_HOUR = 9
WEATHER = [
    ("pochmurno i wietrznie", 30), ("szaro, mżawka", 20), ("deszcz", 15),
    ("przejaśnienia", 20), ("słonecznie, chłodny wiatr", 15),
]
DAY_ZERO = dt.date(1990, 3, 22)


def _pick(table):
    total = sum(w for _, w in table)
    r = rng().randint(1, total)
    for name, w in table:
        r -= w
        if r <= 0:
            return name
    return table[-1][0]


def day(char, state):
    """Liczniki bieżącej doby postaci. Tworzy je przy pierwszym użyciu."""
    d = char.get("doba")
    if d is None:
        d = char["doba"] = {"od": state["czas"], "posilki": 0, "woda_l": 0,
                            "woda_surowa_l": 0, "sen_min": 0,
                            "antybiotyk": False, "pelna": False}
    return d


# --- przedmioty zużywane porcjami --------------------------------------------

def find(state, tag):
    """Przedmiot z tagiem pod ręką: najpierw przy sobie, potem w węźle."""
    from .actions import reachable
    found = [i for i in state["ekwipunek"]
             if tag in i.get("daje", []) and i.get("ilosc", 1) > 0
             and reachable(state, i)]
    found.sort(key=lambda i: i.get("gdzie") != "przy_sobie")
    return found[0] if found else None


def consume(state, item):
    """Zużywa jedną porcję przedmiotu. Zwraca opis tego, co zostało."""
    from .core import load_json
    spec = load_json("items.json").get(item["id"], {})
    portions = spec.get("porcje", 1)
    if portions > 1:
        left = item.get("napoczete", portions) - 1
        if left > 0:
            item["napoczete"] = left
            return f"{item['nazwa']}: napoczęte, zostało {left}/{portions}"
        item.pop("napoczete", None)
    item["ilosc"] = item.get("ilosc", 1) - 1
    rest = item["ilosc"]
    state["ekwipunek"] = [i for i in state["ekwipunek"]
                          if i.get("ilosc", 1) > 0]
    return f"{item['nazwa']}: zostało {rest}"


# --- modyfikatory z terminem ----------------------------------------------

def add_timed_modifier(state, char, source, steps, minutes):
    until = world.parse(state["czas"]) + dt.timedelta(minutes=minutes)
    char.setdefault("modyfikatory", []).append({
        "zrodlo": source, "kroki": steps, "wszystko": True,
        "do": world.fmt(until)})


def prune_modifiers(state, char):
    now = state["czas"]
    char["modyfikatory"] = [m for m in char.get("modyfikatory", [])
                            if not m.get("do") or m["do"] > now]


# --- sen ------------------------------------------------------------------------

def safe_place(state):
    node = world.current_node(state) or {}
    return bool(node.get("kryjowka") or not node.get("gestosc", 10))


def wake(state, char, minutes, safe):
    """Skutki snu przy pobudce. Zwraca linie.

    Minuty snu do licznika doby dolicza na bieżąco act.py spij."""
    out = []
    h = f"{minutes // 60} h {minutes % 60:02d} min"
    if minutes >= SLEEP_FULL:
        char["aktywnosc_min"] = 0
        if safe:
            char["zmeczenie"] = 0
            before = char["nerwy"]
            char["nerwy"] = rules.clamp(before - 2, 0, 10)
            out.append(("cialo", f"Pełny sen w bezpiecznym miejscu ({h}): "
                                 f"zmęczenie 0, nerwy {before} → "
                                 f"{char['nerwy']}."))
            out += develop(char)
        else:
            char["zmeczenie"] = rules.clamp(char["zmeczenie"] - 2, 0, 5)
            out.append(("cialo", f"Sen w niepewnym miejscu ({h}): zmęczenie "
                                 f"−2, teraz {char['zmeczenie']}. Bez "
                                 "rozwoju i bez ulgi dla nerwów."))
    elif minutes >= SLEEP_SOME:
        char["zmeczenie"] = rules.clamp(char["zmeczenie"] - 1, 0, 5)
        out.append(("cialo", f"Krótki sen ({h}): zmęczenie −1, teraz "
                             f"{char['zmeczenie']}."))
    else:
        out.append(("cialo", f"Drzemka ({h}) nic nie daje."))
    return out


def develop(char):
    out = []
    marks = char.setdefault("znaczniki", {})
    for skill, level in char["umiejetnosci"].items():
        need = 3 * level
        if level < rules.SKILL_MAX and marks.get(skill, 0) >= need:
            char["umiejetnosci"][skill] = level + 1
            marks[skill] = 0
            out.append(("sukces", f"Rozwój: {rules.SKILLS[skill]} "
                                  f"{level} → {level + 1}."))
    return out


# --- świt ------------------------------------------------------------------------

def settle_dawn(state):
    """Rozlicza minioną dobę. Zwraca linie i dane do logu."""
    state["czeka_swit"] = False
    now = world.parse(state["czas"])
    out = [("swit", f"ROZLICZENIE DOBY ({world.human(now)})")]
    log = {}
    out += weather(state, now, log)
    out += tick_clocks(state, log)
    char = state.get("postac")
    if char and not char.get("martwy"):
        out += _settle_character(state, char, now, log)
        if now.weekday() == 6 and char.get("fart", 0) < 2:
            char["fart"] += 1
            out.append(("fart", f"Niedziela: Fart +1, teraz {char['fart']}."))
    return out, log


def weather(state, now, log):
    date = now.date()
    days = (date - DAY_ZERO).days
    temp = round(3 + 0.15 * days + rng().uniform(-4, 4))
    frost_season = (date.month, date.day) <= FROST_UNTIL
    frost = frost_season and d100() <= FROST_CHANCE
    sky = _pick(WEATHER)
    pog = {"temperatura": temp, "niebo": sky, "przymrozek_do": None}
    if frost:
        until = dt.datetime(date.year, date.month, date.day, FROST_ENDS_HOUR)
        pog["przymrozek_do"] = world.fmt(until)
    state["pogoda"] = pog
    log["pogoda"] = pog
    text = f"Pogoda: {sky}, średnio {temp}°C."
    if frost:
        text += (f" Przymrozek do {FROST_ENDS_HOUR}:00: sztywni są ospali, "
                 "spotkań jest o połowę mniej.")
    return [("stan", text)]


CLOCK_TICK = 50              # % szansy, że zegar zagrożenia ruszy o świcie


def tick_clocks(state, log):
    out = []
    rolls = []
    for z in state.get("zegary", []):
        if z["stan"] >= z["segmenty"]:
            continue
        u = d100()
        moved = u <= CLOCK_TICK
        if moved:
            z["stan"] += 1
        rolls.append({"zegar": z["id"], "wynik": u, "ruszyl": moved})
    # Bez nazw: zegary są tajne, a gracz widzi terminal.
    moved = sum(r["ruszyl"] for r in rolls)
    if moved:
        out.append(("zagrozenie", f"Zegary zagrożeń: ruszyło {moved}. MG "
                                  "sprawdza w state.json (Read) i wprowadza "
                                  "segmenty ze scenariusza."))
    if rolls:
        log["zegary"] = rolls
    return out


def frost_now(state):
    until = state.get("pogoda", {}).get("przymrozek_do")
    return bool(until and state["czas"] < until)


def _settle_character(state, char, now, log):
    out = []
    d = day(char, state)
    hours = (now - world.parse(d["od"])).total_seconds() / 3600
    partial = hours < PARTIAL_DAY_HOURS
    sick = char.get("choroba")
    entry = {"doba": dict(d), "niepelna": partial}

    if partial:
        out.append(("info", f"Doba niepełna ({hours:.0f} h): bez kar za sen, "
                            "jedzenie i wodę."))
    else:
        # Sen.
        if d["sen_min"] < SLEEP_SOME:
            char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 2, 0, 5)
            char["nerwy"] = rules.clamp(char["nerwy"] + 1, 0, 10)
            out.append(("cialo", f"Noc bez snu: zmęczenie +2 "
                                 f"({char['zmeczenie']}), nerwy +1 "
                                 f"({char['nerwy']})."))
        # Jedzenie.
        if d["posilki"] == 0:
            char["glod"] = rules.clamp(char["glod"] + 1, 0, 5)
            out.append(("cialo", f"Doba bez jedzenia: głód +1, teraz "
                                 f"{char['glod']}."))
        # Woda.
        need = WATER_NEED_SICK if sick and sick["poziom"] > 0 else WATER_NEED
        water = d["woda_l"] + d["woda_surowa_l"]
        if water < 1:
            char["dni_bez_wody"] = char.get("dni_bez_wody", 0) + 1
            char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 2, 0, 5)
            out.append(("cialo", f"Doba bez wody "
                                 f"({char['dni_bez_wody']}. z rzędu): "
                                 f"zmęczenie +2, teraz {char['zmeczenie']}."))
        elif water < need:
            char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 1, 0, 5)
            out.append(("cialo", f"Za mało wody ({water} z {need} l): "
                                 f"zmęczenie +1, teraz {char['zmeczenie']}."))
        else:
            char["dni_bez_wody"] = 0

    out += _infections(state, char, entry)
    out += _disease(char, d, entry)

    # Stan krytyczny liczony raz na dobę.
    reasons = []
    if any(w.get("zakazenie", 0) >= 3 for w in char["rany"]):
        reasons.append("sepsa")
    if char.get("choroba") and char["choroba"]["poziom"] >= 2:
        reasons.append(char["choroba"]["nazwa"])
    if char.get("dni_bez_wody", 0) >= 3:
        reasons.append("pragnienie")
    if any(w.get("zakazenie", 0) >= 4 for w in char["rany"]):
        char["martwy"] = True
        char["zgon"] = state["czas"]
        out.append(("alarm", "Zakażenie doszło do końca. POSTAĆ NIE ŻYJE."))
    elif reasons:
        u = d100()
        entry["rzut_na_smierc"] = {"powody": reasons, "wynik": u,
                                   "szansa": DAILY_DEATH_CHANCE}
        if u <= DAILY_DEATH_CHANCE:
            char["martwy"] = True
            char["zgon"] = state["czas"]
            out.append(("alarm", f"Stan krytyczny ({', '.join(reasons)}). "
                                 f"Rzut na śmierć: {u} ≤ {DAILY_DEATH_CHANCE}."
                                 " POSTAĆ NIE ŻYJE."))
        else:
            out.append(("cialo", f"Stan krytyczny ({', '.join(reasons)}). "
                                 f"Rzut na śmierć: {u} > "
                                 f"{DAILY_DEATH_CHANCE}, postać żyje."))

    char["doba"] = None
    sunrise = world.sun_times(now.date())["wschod"]
    if sunrise > now:
        sunrise = world.sun_times(now.date() - dt.timedelta(days=1))["wschod"]
    day(char, state)["od"] = world.fmt(sunrise)
    log["postac"] = entry
    return out


def _infections(state, char, entry):
    out = []
    rolls = []
    healed = []
    for w in char["rany"]:
        level = w.get("zakazenie", 0)
        worsen = (INFECTION_BASE + INFECTION_SEVERITY[w["ciezkosc"]]
                  + (INFECTION_BITE if w.get("ugryzienie") else 0)
                  + (0 if w.get("opatrzona") else INFECTION_UNDRESSED)
                  + (INFECTION_CLEANED if w.get("odkazona") else 0))
        worsen = rules.clamp(worsen, 3, 60)
        improve = 0
        if level > 0:
            improve = (INFECTION_IMPROVE
                       + (INFECTION_IMPROVE_DRESSED if w.get("opatrzona") else 0)
                       + (INFECTION_IMPROVE_CLEANED if w.get("odkazona") else 0))
        u = d100()
        if u <= worsen:
            w["zakazenie"] = level + 1
            change = "+1"
        elif improve and u > 100 - improve:
            w["zakazenie"] = level - 1
            change = "−1"
        else:
            change = "0"
        rolls.append({"rana": w["id"], "pogorszenie": worsen,
                      "poprawa": improve, "wynik": u, "zmiana": change})
        w["odkazona"] = False
        name = f"Rana #{w['id']} ({rules.wound_name(w)})"
        if change == "+1":
            out.append(("cialo", f"{name}: zakażenie rośnie do "
                                 f"{w['zakazenie']} "
                                 f"({INFECTION_NAMES[w['zakazenie']]})."))
        elif change == "−1":
            out.append(("sukces", f"{name}: zakażenie cofa się do "
                                  f"{w['zakazenie']}."))
        # Gojenie.
        if w.get("opatrzona") and w.get("zakazenie", 0) <= 1:
            w["gojenie"] = w.get("gojenie", 0) + 1
            if w["gojenie"] >= HEAL_DAYS[w["ciezkosc"]]:
                into = HEAL_INTO[w["ciezkosc"]]
                if into is None:
                    healed.append(w)
                    out.append(("sukces", f"{name}: zagojona."))
                else:
                    w["ciezkosc"] = into
                    w["gojenie"] = 0
                    out.append(("sukces", f"Rana #{w['id']} goi się: teraz "
                                          f"{rules.wound_name(w)}."))
    char["rany"] = [w for w in char["rany"] if w not in healed]
    entry["zakazenia"] = rolls
    return out


INFECTION_NAMES = {0: "czysta", 1: "zaczerwienienie", 2: "gorączka",
                   3: "sepsa", 4: "śmierć"}


def _disease(char, d, entry):
    sick = char.get("choroba")
    if not sick:
        return []
    out = []
    if sick["poziom"] == 0:
        sick["poziom"] = 1
        out.append(("cialo", f"Choroba: {sick['nazwa']}. Biegunka, gorączka, "
                             "słabość: −1 krok do wszystkiego, potrzeba 3 l "
                             "wody na dobę."))
        entry["choroba"] = {"nazwa": sick["nazwa"], "zmiana": "objawy"}
        return out
    improve = DISEASE_IMPROVE
    if d["woda_l"] >= WATER_NEED_SICK:
        improve += DISEASE_IMPROVE_WATER
    if d["antybiotyk"]:
        improve += DISEASE_IMPROVE_ANTIBIOTIC
    u = d100()
    if u <= DISEASE_WORSEN:
        sick["poziom"] = min(2, sick["poziom"] + 1)
        change = "+1"
    elif u > 100 - improve:
        sick["poziom"] -= 1
        change = "−1"
    else:
        change = "0"
    char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 1, 0, 5)
    entry["choroba"] = {"nazwa": sick["nazwa"], "pogorszenie": DISEASE_WORSEN,
                        "poprawa": improve, "wynik": u, "zmiana": change}
    if sick["poziom"] <= 0:
        char["choroba"] = None
        out.append(("sukces", f"{sick['nazwa'].capitalize()} mija."))
    elif change == "+1":
        out.append(("cialo", f"{sick['nazwa'].capitalize()} się pogarsza "
                             f"(poziom {sick['poziom']}), zmęczenie +1."))
    else:
        out.append(("cialo", f"{sick['nazwa'].capitalize()} trwa (poziom "
                             f"{sick['poziom']}), zmęczenie +1."))
    return out


def catch_disease(char):
    """Rzut zapieczętowany po surowej wodzie. Objawy przy następnym świcie."""
    u = d100()
    if u <= RAW_WATER_SICK and not char.get("choroba"):
        char["choroba"] = {"nazwa": _pick(DISEASES), "poziom": 0}
        return u, True
    return u, False


def disease_steps(char):
    sick = char.get("choroba")
    if sick and sick["poziom"] >= 1:
        return [(sick["nazwa"], -sick["poziom"])]
    return []
