"""Czas, światło, hałas i to, co dzieje się z upływem czasu."""

import datetime as dt
import math

from . import noisy, rules
from .core import d100

WARSAW_LAT = 52.23
WARSAW_LON = 21.01

# Czas letni w PRL/RP w 1990 roku: 25 marca 2:00 – 30 września 3:00.
DST_START = dt.datetime(1990, 3, 25, 2, 0)
DST_END = dt.datetime(1990, 9, 30, 3, 0)


def parse(t):
    return dt.datetime.fromisoformat(t)


def fmt(t):
    return t.isoformat(timespec="minutes")


def human(t):
    return t.strftime("%d.%m.%Y %H:%M")


def utc_offset(local):
    return 2 if DST_START <= local < DST_END else 1


def _sun_event_utc_minutes(date, zenith):
    """Minuty UTC wschodu i zachodu dla podanego zenitu (algorytm NOAA)."""
    n = date.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g)
                       - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g)
                       - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g)
            - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
            - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    lat = math.radians(WARSAW_LAT)
    cos_ha = (math.cos(math.radians(zenith)) / (math.cos(lat) * math.cos(decl))
              - math.tan(lat) * math.tan(decl))
    ha = math.degrees(math.acos(rules.clamp(cos_ha, -1, 1)))
    rise = 720 - 4 * (WARSAW_LON + ha) - eqtime
    set_ = 720 - 4 * (WARSAW_LON - ha) - eqtime
    return rise, set_


def sun_times(date):
    """Lokalny świt cywilny, wschód, zachód i zmierzch cywilny."""
    base = dt.datetime(date.year, date.month, date.day)
    off = utc_offset(base + dt.timedelta(hours=12)) * 60
    sunrise, sunset = _sun_event_utc_minutes(date, 90.833)
    dawn, dusk = _sun_event_utc_minutes(date, 96.0)
    to_local = lambda m: base + dt.timedelta(minutes=m + off)
    return {
        "swit": to_local(dawn), "wschod": to_local(sunrise),
        "zachod": to_local(sunset), "zmierzch": to_local(dusk),
    }


def ambient_light(t):
    s = sun_times(t.date())
    if s["wschod"] <= t < s["zachod"]:
        return "dzien"
    if s["swit"] <= t < s["wschod"] or s["zachod"] <= t < s["zmierzch"]:
        return "polmrok"
    return "ciemnosc"


def current_node(state):
    node_id = state["lokacja"].get("wezel")
    return state["wezly"].get(node_id) if node_id else None


def light(state):
    """Światło w miejscu postaci, z uwzględnieniem jej latarki."""
    node = current_node(state)
    level = (node or {}).get("swiatlo") or ambient_light(parse(state["czas"]))
    char = state.get("postac") or {}
    if char.get("swiatlo"):
        level = {"ciemnosc": "polmrok", "polmrok": "dzien"}.get(level, level)
    return level


def is_night(state):
    return ambient_light(parse(state["czas"])) == "ciemnosc"


# --- hałas -----------------------------------------------------------------------

def make_noise(state, level):
    """Dodaje uwagę za hałas na poziomie 0–5. Zwraca listę zdarzeń."""
    level = rules.clamp(level, 0, 5)
    points = rules.NOISE_POINTS[level]
    node = current_node(state)
    if not node or points == 0:
        return []
    node["uwaga"] = node.get("uwaga", 0) + points
    node["ostatni_halas"] = max(node.get("ostatni_halas", 0), level)
    if level == 5 and node.get("sasiedzi"):
        for nid in node["sasiedzi"]:
            nb = state["wezly"][nid]
            nb["uwaga"] = nb.get("uwaga", 0) + rules.SHOT_NEIGHBOR_POINTS
        return [("czas", f"Strzał słychać w sąsiednich węzłach "
                         f"(uwaga +{rules.SHOT_NEIGHBOR_POINTS}).")]
    return []


def pass_time(state, minutes, noise):
    """Hałas na miejscu, potem upływ czasu. Zwraca listę zdarzeń."""
    node = current_node(state)
    before = node.get("uwaga", 0) if node else None
    old = state["czas"]
    noise = rules.clamp(noise, 0, 5)
    events = make_noise(state, noise)
    later = advance(state, minutes)
    out = [("czas", f"Czas: {human(parse(old))} → {human(parse(state['czas']))}"
                    f" (+{minutes} min). Hałas: {noise}.")]
    if node:
        out.append(("czas", f"Uwaga w „{node['nazwa']}”: {before} → "
                            f"{node.get('uwaga', 0)}."))
    return out + events + later


# --- upływ czasu -------------------------------------------------------------

def advance(state, minutes):
    """Przesuwa zegar gry. Zwraca listę zdarzeń (rodzaj, tekst).

    Czas płynie odcinkami do pełnych 10 minut. Na końcu każdej jednostki
    opada uwaga, liczy się światło w nocy i rzut na śmierć w stanie
    krytycznym.
    """
    events = []
    if minutes <= 0:
        return events
    start = parse(state["czas"])
    end = start + dt.timedelta(minutes=minutes)
    char = state.get("postac")

    t = start
    while t < end:
        to_tick = 10 - (t.minute % 10)
        step = min(to_tick, int((end - t).total_seconds() // 60))
        t += dt.timedelta(minutes=step)
        alive = char and not char.get("martwy")
        if alive:
            events += _body_segment(char, step)
        if t.minute % 10 == 0:
            events += _tick(state, char, t)

    # Świt: trzeba rozliczyć dobę.
    day = start.date()
    while day <= end.date():
        sunrise = sun_times(day)["wschod"]
        if start < sunrise <= end:
            state["czeka_swit"] = True
            events.append(("swit", f"Świt ({sunrise:%H:%M}). Doba do "
                                    "rozliczenia skryptem dawn.py."))
        day += dt.timedelta(days=1)

    state["czas"] = fmt(end)
    return events


def _noisy_tick(state, char, t):
    """Rzuty na nieświadomych hałasujących (raz na jednostkę czasu)."""
    node = current_node(state)
    if not node or not char or char.get("martwy"):
        return []
    events = []
    log = state.setdefault("_do_logu", [])
    node_id = state["lokacja"].get("wezel")
    loud = node.get("ostatni_halas", 0) >= rules.NOISY_LOUD_LEVEL
    exposed = bool(state.get("ukrycie")) or node.get("uwaga", 0) > 0
    for h in state.get("halasujacy", []):
        with_char = h.get("wezel") is None
        if with_char and not exposed:
            continue
        if not with_char and h["wezel"] != node_id:
            continue
        chance = noisy.chance(h, loud=loud and with_char)
        if chance <= 0:
            continue
        u = d100()
        hit = u <= chance
        log.append({"zdarzenie": "halasujacy_rzut", "nr": h["id"],
                    "opis": h["opis"], "szansa": chance, "wynik": u,
                    "halas": hit})
        if hit:
            events.append(("alarm", f"{t:%H:%M} {h['opis']} "
                                    f"{noisy.HIT_TEXT[h['rodzaj']]}. "
                                    f"Hałas {noisy.level(h)}."))
            events += make_noise(state, noisy.level(h))
    if (node.get("typ") in rules.AMBIENT_NODE_TYPES and not char.get("spi")):
        u = d100()
        hit = u <= rules.AMBIENT_NOISE_CHANCE
        entry = {"zdarzenie": "halas_okolicy", "wezel": node_id,
                 "szansa": rules.AMBIENT_NOISE_CHANCE, "wynik": u,
                 "halas": hit}
        if hit:
            kind = "pies" if d100() <= 50 else "dziecko"
            entry["rodzaj"] = kind
            text = ("gdzieś w pobliżu szczeka pies" if kind == "pies"
                    else "gdzieś w pobliżu płacze dziecko")
            events.append(("alarm", f"{t:%H:%M} {text.capitalize()}. "
                                    f"Hałas {rules.AMBIENT_NOISE_LEVEL}."))
            events += make_noise(state, rules.AMBIENT_NOISE_LEVEL)
        log.append(entry)
    return events


def _tick(state, char, t):
    events = _noisy_tick(state, char, t)
    for node in state["wezly"].values():
        node.pop("ostatni_halas", None)
        if node.get("uwaga", 0) > 0:
            node["uwaga"] -= 1
    if char and char.get("swiatlo") and ambient_light(t) == "ciemnosc":
        node = current_node(state)
        if node:
            node["uwaga"] = node.get("uwaga", 0) + rules.NIGHT_LIGHT_POINTS
    if char and char.get("krytyczny") and not char.get("martwy"):
        u = d100()
        if u <= rules.CRITICAL_DEATH_CHANCE:
            char["martwy"] = True
            char["zgon"] = fmt(t)
            events.append(("alarm", f"{t:%H:%M} Rzut na śmierć: {u} ≤ "
                                    f"{rules.CRITICAL_DEATH_CHANCE}. "
                                    "POSTAĆ NIE ŻYJE."))
        else:
            events.append(("cialo", f"{t:%H:%M} Rzut na śmierć: {u} > "
                                    f"{rules.CRITICAL_DEATH_CHANCE}, "
                                    "postać żyje."))
    return events


def _body_segment(char, minutes):
    events = []
    # Zmęczenie od aktywności: +1 za każde 6 godzin (sen się nie liczy).
    if char.get("spi"):
        minutes = 0
    char["aktywnosc_min"] = char.get("aktywnosc_min", 0) + minutes
    if char["aktywnosc_min"] >= 360:
        char["aktywnosc_min"] -= 360
        char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 1, 0, 5)
        events.append(("cialo", f"Zmęczenie rośnie do {char['zmeczenie']} "
                                "(6 godzin na nogach)."))

    # Krwawienie jako zegar.
    for w in char["rany"]:
        if not w.get("krwawienie") or w.get("opatrzona"):
            continue
        w["licznik_krwawienia"] = w.get("licznik_krwawienia", 0) + minutes
        if (w["krwawienie"] == "lekkie"
                and w["licznik_krwawienia"] >= rules.BLEED_LIMIT["lekkie"]):
            w["krwawienie"] = "silne"
            if w["ciezkosc"] == "powazna":
                w["ciezkosc"] = "krytyczna"
            w["licznik_krwawienia"] = 0
            char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 2, 0, 5)
            events.append(("cialo", f"Rana #{w['id']} "
                                    f"({rules.PLACE_NAMES[w['miejsce']]}) "
                                    "krwawi coraz mocniej: krytyczna, "
                                    "zmęczenie +2."))
        if (w["krwawienie"] == "silne"
                and w["licznik_krwawienia"] >= rules.BLEED_LIMIT["silne"]
                and not char.get("krytyczny")):
            char["krytyczny"] = True
            events.append(("alarm", "STAN KRYTYCZNY: silne krwawienie bez "
                                    "opatrunku. Co jednostkę rzut na śmierć."))
    return events


def update_critical(char):
    char["krytyczny"] = any(
        w.get("krwawienie") == "silne" and not w.get("opatrzona")
        and w.get("licznik_krwawienia", 0) >= rules.BLEED_LIMIT["silne"]
        for w in char["rany"])


HEAD_GUARD_DOWN = {"krytyczna": "powazna", "powazna": "drasniecie",
                   "drasniecie": "drasniecie"}


def worn(state, tag):
    """Założony przedmiot z danym „daje” (Rules.md, *Odzież*)."""
    for i in state.get("ekwipunek", []):
        if (i.get("zalozony") and tag in i.get("daje", [])
                and i.get("gdzie") == "przy_sobie" and i.get("ilosc", 1) > 0):
            return i
    return None


def has_head_guard(state):
    """Założony ochraniacz na głowę (Rules.md, *Rany*)."""
    return worn(state, "ochrona_glowy") is not None


def add_wound(state, miejsce, ciezkosc, ugryzienie=False):
    if miejsce == "glowa" and has_head_guard(state):
        ciezkosc = HEAD_GUARD_DOWN[ciezkosc]
    state["liczniki"]["rana"] += 1
    wound = {
        "id": state["liczniki"]["rana"],
        "miejsce": miejsce,
        "ciezkosc": ciezkosc,
        "krwawienie": rules.DEFAULT_BLEEDING[ciezkosc],
        "opatrzona": False,
        "zakazenie": 0,
        "ugryzienie": ugryzienie,
        "licznik_krwawienia": 0,
        "od": state["czas"],
    }
    state["postac"]["rany"].append(wound)
    return wound
