"""Spotkania, tożsamość sztywnych i powstawanie zmarłych.

Rules.md: *Spotkania*, *Wątpliwość*, *Powstawanie zmarłych*, *Etap sztywnych*.
Wszystko tutaj dzieje się samo po upływie czasu (after). MG tego nie
wywołuje i nie wybiera wyników.
"""

import datetime as dt

from . import actions, body, fight as F, rules, world
from .core import GameError, load_json, rng

DAY_ZERO = dt.datetime(1990, 3, 22, 0, 0)

# Udział świeżaków w dniu apokalipsy według źródła sztywnych w węźle.
SOURCE_FRESH = {"szpital": 0.95, "mieszkania": 0.85, "mieszane": 0.6,
                "cmentarz": 0.2}
FRESH_FLOOR = 0.15          # nowe śmierci zawsze dają świeżaki
FRESH_DECAY_DAYS = 10       # Rules.md: świeżak do 10 dni rozkładu
AMBUSH_CHANCE = 30          # % że świeżak czeka w ukryciu (rzut zapieczętowany)
NOTICE_BONUS = 3            # Rules.md: test Czujności z +3 krokami
LURK_PENALTY = -3
KNOWN_CHANCE = 25           # % że sztywny w węźle to ktoś znajomy
MAX_ENCOUNTER_CHANCE = 90
RISE_MINUTES = (10, 60)
SLEEP_PENALTY = -3


def d100():
    return rng().randint(1, 100)


def now(state):
    return world.parse(state["czas"])


# --- etap i liczebność --------------------------------------------------------

def decay_factor(temp):
    if temp < 0:
        return 0.25
    if temp < 10:
        return 0.5
    if temp < 20:
        return 1.0
    return 2.0


def decay_days(state, since=DAY_ZERO):
    days = max(0.0, (now(state) - since).total_seconds() / 86400)
    return days * decay_factor(state.get("pogoda", {}).get("temperatura", 4))


def fresh_chance(state, node):
    base = SOURCE_FRESH.get((node or {}).get("zrodlo", "mieszane"), 0.6)
    d = decay_days(state)
    keep = rules.clamp(1 - (d - FRESH_DECAY_DAYS / 2) / FRESH_DECAY_DAYS, 0, 1)
    return FRESH_FLOOR + (base - FRESH_FLOOR) * keep


def encounter_size(attention):
    if attention >= 16:
        return rng().randint(6, 12), "strumień"
    if attention >= 8:
        return rng().randint(2, 4), "grupa"
    if attention >= 4:
        return rng().randint(1, 2), None
    return 1, None


def start_zone(state, kind):
    if kind == "strumień":
        return 1
    light = world.light(state)
    u = d100()
    if light == "dzien":
        return 1 if u <= 60 else 2
    if light == "polmrok":
        return 2 if u <= 70 else 3
    return 2 if u <= 50 else 3


# --- tożsamość ---------------------------------------------------------------

def identity(state, node_id, stage, used_known):
    """Opis sztywnego i ewentualne powiązanie (znajomy, ciało)."""
    node = state["wezly"].get(node_id, {})
    # Najpierw ciała, które wstały w tym węźle.
    risen = node.get("wstali", [])
    if risen:
        body_id = risen.pop(0)
        body = body_by_id(state, body_id)
        stage = body_stage(state, body)
        return stage, body["opis"], {"cialo": body_id,
                                     "znany": body.get("znany", False)}
    # Potem znajomi przypisani do węzła w scenariuszu.
    known = [k for k in state.get("znajomi", [])
             if k.get("wezel") == node_id and k.get("los") in ("martwy", "nieznany")
             and k["id"] not in used_known]
    if known and d100() <= KNOWN_CHANCE:
        k = known[0]
        k["los"] = "sztywny"
        used_known.add(k["id"])
        return stage, k["opis"], {"znajomy": k["id"], "znany": True}
    people = load_json("people.json")
    source = node.get("zrodlo", "mieszane")
    pool = list(people["kto"]["ogolne"])
    if source in people["kto"]:
        pool = people["kto"][source] * 2 + pool
    # Bez powtórek w jednym spotkaniu.
    for _ in range(10):
        who = rng().choice(pool)
        detail = rng().choice(people["szczegoly"][stage])
        desc = f"{who}; {detail}"
        if desc not in used_known:
            break
    used_known.add(desc)
    return stage, desc, {}


def to_log(state, event, **data):
    """Zdarzenia do zapisania w rolls.log przez skrypt, który je wywołał."""
    state.setdefault("_do_logu", []).append({"zdarzenie": event, **data})


# --- spotkania ------------------------------------------------------------------

def build_stiffs(state, count, kind):
    node_id = state["lokacja"].get("wezel")
    node = state["wezly"].get(node_id, {})
    p_fresh = fresh_chance(state, node)
    used = set()
    stiffs = []
    for _ in range(count):
        stage = "swiezak" if rng().random() < p_fresh else "gnilec"
        stage, desc, extra = identity(state, node_id, stage, used)
        stiffs.append({"etap": stage, "opis": desc, **extra})
    return stiffs


def trigger(state, count=None, zone=None, kind=None, reason="spotkanie",
            stiffs=None):
    """Spotkanie w bieżącym węźle. Zwraca linie do wypisania.

    stiffs: gotowa lista sztywnych (np. ze scenariusza) zamiast losowej."""
    node = world.current_node(state) or {}
    if stiffs is None:
        if count is None:
            count, kind = encounter_size(node.get("uwaga", 0))
        stiffs = build_stiffs(state, count, kind)
    zone = zone or start_zone(state, kind)
    out = [("alarm", f"Spotkanie ({reason})" + (f": {kind}!" if kind else "."))]

    # Zapieczętowany rzut na zasadzkę każdego świeżaka.
    lurking = any(s["etap"] == "swiezak" and d100() <= AMBUSH_CHANCE
                  for s in stiffs) and zone >= 2 and kind != "strumień"

    # Kto zauważył pierwszy: test Czujności z +3 krokami.
    cat = actions.catalog()
    extra = [("pierwsze spojrzenie", NOTICE_BONUS)]
    if lurking:
        extra.append(("ktoś czeka w ukryciu", LURK_PENALTY))
    if state["postac"].get("spi"):
        extra.append(("postać śpi", SLEEP_PENALTY))
    q = actions.build_quote(state, cat, "obserwacja", extra_steps=extra)
    u = d100()
    g = rules.grade(u, q["szansa"])
    noticed = g in ("czysty", "koszt")
    sealed = {"zasadzka": lurking, "szansa": q["szansa"], "wynik": u,
              "stopien": g}
    to_log(state, "spotkanie", powod=reason, rodzaj=kind, strefa=zone,
           sztywni=[{"etap": s["etap"], "opis": s["opis"]} for s in stiffs],
           zapieczetowane=sealed)

    out += known_shock(state, stiffs)
    if noticed:
        state["spotkanie"] = {"sztywni": stiffs, "strefa": zone,
                              "rodzaj": kind, "zapieczetowane": sealed}
        out.append(("info", "Postać zauważa ich pierwsza."))
        out += describe(stiffs, zone)
        out.append(("info", "Do wyboru: encounter.py unik (próba przemknięcia "
                            "niezauważenie) albo encounter.py walcz."))
    else:
        out.append(("alarm", "Zauważyli ją pierwsi."))
        out += describe(stiffs, zone)
        out += begin_fight(state, stiffs, 3 if lurking else zone,
                           ambush=lurking)
    return out, sealed


def known_shock(state, stiffs):
    out = []
    char = state["postac"]
    for s in stiffs:
        if s.get("znany"):
            char["nerwy"] = rules.clamp(char["nerwy"] + 2, 0, 10)
            out.append(("cialo", f"To ktoś znajomy: {s['opis']}. Nerwy +2."))
    return out


def describe(stiffs, zone):
    out = []
    for s in stiffs:
        out.append(("info", f"  {F.STAGES[s['etap']]}: {s['opis']} "
                            f"({F.ZONES[zone]})"))
    return out


def held_weapon(state):
    wid = (state.get("postac") or {}).get("bron", "piesci")
    if wid != "piesci" and wid not in actions.provided(state):
        return "piesci"
    return wid


def begin_fight(state, stiffs, zone, ambush=False):
    order = ([s for s in stiffs if s["etap"] == "swiezak"]
             + [s for s in stiffs if s["etap"] == "gnilec"])
    n_fresh = sum(s["etap"] == "swiezak" for s in order)
    lines = F.start(state, n_fresh, len(order) - n_fresh, zone,
                    held_weapon(state), [s["opis"] for s in order],
                    ambush=False)
    for fs, s in zip(state["starcie"]["sztywni"], order):
        for key in ("cialo", "znajomy", "znany"):
            if key in s:
                fs[key] = s[key]
    if ambush:
        lines = [("alarm", "Zasadzka! Świeżak czekał w ukryciu.")]
        lines += F.stiffs_phase(state, state["starcie"], moved=False,
                                pushed=set())
        lines += F.end_check(state)
    return [("alarm", "Starcie! Dalej: fight.py.")] + lines


def avoid(state):
    enc = state.get("spotkanie")
    if not enc:
        raise GameError("Nie ma spotkania do uniknięcia.")
    cat = actions.catalog()
    extra = []
    if any(s["etap"] == "swiezak" for s in enc["sztywni"]):
        extra.append(("świeżak dobrze widzi", -1))
    extra.append({1: ("są daleko", 1), 2: ("są blisko", 0),
                  3: ("są tuż obok", -1)}[enc["strefa"]])
    q = actions.build_quote(state, cat, "przekradanie", extra_steps=extra)
    u = d100()
    g = rules.grade(u, q["szansa"])
    steps = ", ".join(f"{s} {rules.signed(v)}" for s, v in q["kroki"])
    to_log(state, "unik", szansa=q["szansa"], wynik=u, stopien=g)
    out = [("info", f"Unik (Skradanie): {q['szansa']}% ({steps}), wypadło {u}"
                    f" → {rules.GRADE_NAMES[g]}")]
    if q["szansa"] <= rules.MARK_THRESHOLD:
        actions.add_mark(state["postac"], "skradanie")
    state["spotkanie"] = None
    if g in ("czysty", "koszt"):
        out.append(("sukces", "Postać przemyka niezauważona."))
        state["ukrycie"] = True
        out += world.pass_time(state, 10 if g == "czysty" else 20, 1)
    else:
        zone = min(3, enc["strefa"] + (1 if g == "katastrofa" else 0))
        out.append(("porazka", "Zauważyli ją."))
        out += begin_fight(state, enc["sztywni"], zone)
    return out, {"szansa": q["szansa"], "wynik": u, "stopien": g}


def engage(state):
    enc = state.get("spotkanie")
    if not enc:
        raise GameError("Nie ma spotkania.")
    state["spotkanie"] = None
    return begin_fight(state, enc["sztywni"], enc["strefa"])


# --- ciała -------------------------------------------------------------------

def body_by_id(state, body_id):
    for b in state.get("ciala", []):
        if b["id"] == body_id:
            return b
    raise GameError(f"Nie ma ciała #{body_id}.")


def body_stage(state, body):
    d = decay_days(state, world.parse(body["zgon"]))
    return "swiezak" if d < FRESH_DECAY_DAYS else "gnilec"


def add_body(state, opis, node_id=None, znany=False, postac=False,
             zgon=None, bez_mozgu=False):
    """Rejestruje śmierć i losuje, kiedy ciało wstanie (10–60 minut).

    bez_mozgu: sama śmierć zniszczyła mózg, ciało nie wstanie."""
    state.setdefault("ciala", [])
    state["liczniki"].setdefault("cialo", 0)
    state["liczniki"]["cialo"] += 1
    minutes = rng().randint(*RISE_MINUTES)
    death = world.parse(zgon or state["czas"])
    body = {"id": state["liczniki"]["cialo"], "opis": opis,
            "wezel": node_id or state["lokacja"].get("wezel"),
            "zgon": world.fmt(death),
            "wstaje": world.fmt(death + dt.timedelta(minutes=minutes)),
            "stan": "zniszczony" if bez_mozgu else "lezy",
            "znany": znany, "postac": postac}
    state["ciala"].append(body)
    to_log(state, "cialo", **body)
    return body


def rise_due(state):
    out = []
    t = now(state)
    here = state["lokacja"].get("wezel")
    char = state.get("postac") or {}
    for b in state.get("ciala", []):
        if b["stan"] not in ("lezy", "zwiazany") or world.parse(b["wstaje"]) > t:
            continue
        if b["stan"] == "zwiazany":
            b["stan"] = "wstal_zwiazany"
            to_log(state, "cialo_wstaje", cialo=b["id"], wezel=b["wezel"],
                   zwiazany=True)
            if b["wezel"] == here:
                out.append(("alarm", f"Ciało #{b['id']} ({b['opis']}) wstaje, "
                                      "ale szarpie się w więzach."))
            continue
        b["stan"] = "wstal"
        to_log(state, "cialo_wstaje", cialo=b["id"], wezel=b["wezel"])
        if b["wezel"] != here or char.get("martwy") or not char:
            node = state["wezly"].get(b["wezel"])
            if node is not None:
                node.setdefault("wstali", []).append(b["id"])
            continue
        out.append(("alarm", f"Ciało #{b['id']} ({b['opis']}) wstaje!"))
        stiff = {"etap": "swiezak", "opis": b["opis"], "cialo": b["id"],
                 "znany": b.get("znany", False)}
        out += known_shock(state, [stiff])
        if state.get("starcie"):
            F.add_stiff(state, stiff, 3)
        elif state.get("spotkanie"):
            state["spotkanie"]["sztywni"].append(stiff)
        else:
            out += begin_fight(state, [stiff], 3)
    return out


def register_dead_character(state):
    char = state.get("postac")
    if not char or not char.get("martwy") or char.get("cialo"):
        return []
    no_brain = bool(char.get("mozg_zniszczony"))
    body = add_body(state, f"{char['imie']} (postać gracza)", znany=True,
                    postac=True, zgon=char.get("zgon"), bez_mozgu=no_brain)
    char["cialo"] = body["id"]
    if no_brain:
        return [("alarm", f"{char['imie']} nie żyje. Śmierć zniszczyła mózg: "
                          f"ciało #{body['id']} nie wstanie.")]
    return [("alarm", f"{char['imie']} nie żyje. Ciało #{body['id']} wstanie "
                      "jako świeżak w ciągu godziny.")]


# --- po upływie czasu -----------------------------------------------------------

def after(state, old_time):
    """Wywoływane przez każdy skrypt po komendzie. Zwraca linie.

    Spotkania liczą się od znacznika state["sprawdzone_do"], więc żadna
    jednostka czasu nie przepada, gdy sprawdzanie musi poczekać (starcie,
    spotkanie, decyzja o Farcie).
    """
    out = register_dead_character(state)
    out += rise_due(state)
    since = state.get("sprawdzone_do") or old_time
    char = state.get("postac")
    if state.get("starcie") or state.get("spotkanie") or state.get("czeka_fart"):
        state["sprawdzone_do"] = since
        return out
    state["sprawdzone_do"] = state["czas"]
    node = world.current_node(state)
    # Sztywni ustawieni w scenariuszu czekają w węźle na postać.
    if node and node.get("czeka") and char and not char.get("martwy"):
        placed = node.pop("czeka")
        lines, _sealed = trigger(state, reason="sztywni ze scenariusza",
                                 stiffs=placed)
        return out + lines
    if (not char or char.get("martwy") or not node or node.get("kryjowka")
            or not node.get("gestosc", 10)):
        return out
    start, end = world.parse(since), now(state)
    epoch = dt.datetime(1990, 1, 1)
    tick = lambda x: int((x - epoch).total_seconds() // 600)
    for _ in range(max(0, tick(end) - tick(start))):
        chance = min(MAX_ENCOUNTER_CHANCE,
                     node.get("gestosc", 10) + 5 * node.get("uwaga", 0))
        if body.frost_now(state):
            chance //= 2
        if d100() <= chance:
            lines, _sealed = trigger(state, reason=f"szansa {chance}%")
            out += lines
            break
    return out
