"""Przeszukiwanie: łup i zdarzenia (Rules.md, *Przeszukiwanie*)."""

import datetime as dt

from . import encounter, inventory, rules, world
from .core import GameError, load_json, rng

ROLLS = {"czysty": 3, "koszt": 2, "porazka": 1, "katastrofa": 0}
PLUNDER_PER_DAY = 3
PLUNDER_PER_SEARCH = 25
PLUNDER_MAX = 95
EVENT_BASE = 15
EVENT_PER_ATTENTION = 2
EVENT_MAX = 50

EVENTS = [
    ("sztywny", 35), ("zwloki", 20), ("halas", 15), ("glowa", 10),
    ("szklo", 10), ("notatka", 10),
]
NOTES = [
    "Kartka na lodówce: „Mamo, poszliśmy do babci na Pragę. Czekaj tu.”",
    "Na lustrze szminką: „ONI WSTAJĄ. NIE OTWIERAĆ”.",
    "Niedokończony list do kogoś w RFN, z prośbą o paczkę.",
    "Kalendarz ścienny z PKO, kratki skreślone do 21 marca.",
    "Kartka przybita do drzwi: „Zbiórka w kościele o 12. Ks. proboszcz”.",
    "Zeszyt szkolny z wypracowaniem o wiośnie i Marzannie.",
]


def table_for(state):
    node = world.current_node(state)
    if not node:
        raise GameError("Postać nie jest w żadnym węźle mapy.")
    tables = {k: v for k, v in load_json("loot.json").items()
              if not k.startswith("_")}
    if node.get("typ") not in tables:
        raise GameError(f"Brak tabeli łupu dla typu miejsca "
                        f"„{node.get('typ')}”. Typy: {', '.join(tables)}.")
    return node, tables[node["typ"]]


def plunder(state, node, table):
    days = max(0, (world.parse(state["czas"]) - encounter.DAY_ZERO).days)
    return min(PLUNDER_MAX, table["splądrowanie"] + PLUNDER_PER_DAY * days
               + PLUNDER_PER_SEARCH * node.get("przeszukania", 0))


def search(state, grade):
    """Skutek przeszukania dla danego stopnia. Zwraca linie."""
    node, table = table_for(state)
    p = plunder(state, node, table)
    out = [("info", f"Splądrowanie miejsca: {p}%.")]
    found = []
    for _ in range(ROLLS[grade]):
        if rng().randint(1, 100) <= p:
            continue
        total = sum(e["waga"] for e in table["lup"])
        u = rng().uniform(0, total)
        for e in table["lup"]:
            u -= e["waga"]
            if u <= 0:
                break
        qty = rng().randint(*e["ilosc"])
        item = inventory.add(state, e["przedmiot"], qty)
        found.append(f"{item['nazwa']}" + (f" × {qty}" if qty != 1 else ""))
    node["przeszukania"] = node.get("przeszukania", 0) + 1
    if found:
        out.append(("sukces", "Znalezione: " + ", ".join(found) + "."))
    else:
        out.append(("porazka", "Nic, co by się przydało."))
    encounter.to_log(state, "lup", splądrowanie=p, znalezione=found)
    out += event(state, node)
    return out


def event(state, node):
    chance = min(EVENT_MAX, EVENT_BASE
                 + EVENT_PER_ATTENTION * node.get("uwaga", 0))
    if rng().randint(1, 100) > chance:
        return []
    total = sum(w for _, w in EVENTS)
    u = rng().uniform(0, total)
    for kind, w in EVENTS:
        u -= w
        if u <= 0:
            break
    encounter.to_log(state, "zdarzenie_przeszukania", rodzaj=kind)
    char = state["postac"]
    if kind == "sztywny":
        lines, _ = encounter.trigger(state, count=1, zone=3,
                                     reason="w trakcie przeszukania coś się "
                                            "porusza")
        return lines
    if kind == "zwloki":
        people = load_json("people.json")
        who = rng().choice(people["kto"]["ogolne"])
        ago = rng().randint(0, 50)
        zgon = world.fmt(world.parse(state["czas"]) - dt.timedelta(minutes=ago))
        body = encounter.add_body(state, who, zgon=zgon)
        return [("alarm", f"Zwłoki: {who}. Wyglądają na świeże. "
                          f"(ciało #{body['id']}, rise.py)")]
    if kind == "halas":
        world.make_noise(state, 3)
        return [("koszt", "Coś spada z łoskotem. Hałas 3.")]
    if kind == "glowa":
        char["nerwy"] = rules.clamp(char["nerwy"] + 1, 0, 10)
        return [("cialo", "W wannie leży odcięta głowa. Kłapie zębami. "
                          "Nerwy +1.")]
    if kind == "szklo":
        w = world.add_wound(state, "reka", "drasniecie")
        return [("cialo", f"Skaleczenie o szkło. Rana #{w['id']}: "
                          f"{rules.wound_name(w)}.")]
    return [("info", rng().choice(NOTES))]
