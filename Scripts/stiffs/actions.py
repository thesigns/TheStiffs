"""Katalog akcji, wycena szansy i stosowanie skutków."""

from . import rules, world
from .core import GameError, load_json, rng


def catalog():
    return load_json("actions.json")


def get_action(cat, action_id):
    if action_id not in cat:
        known = ", ".join(sorted(cat))
        raise GameError(f"Nie ma akcji „{action_id}”. Znane akcje: {known}.")
    return cat[action_id]


def living_character(state):
    char = state.get("postac")
    if not char:
        raise GameError("Kampania nie ma jeszcze postaci.")
    if char.get("martwy"):
        raise GameError("Postać nie żyje. Pozostaje rise.py.")
    return char


def reachable(state, item):
    """Przedmiot jest pod ręką: przy postaci albo w węźle, w którym jest."""
    where = item.get("gdzie", "przy_sobie")
    return where == "przy_sobie" or where == state["lokacja"].get("wezel")


def provided(state):
    """Mapa: co daje ekwipunek pod ręką (np. „lom”) → nazwa przedmiotu."""
    out = {}
    for item in state["ekwipunek"]:
        if item.get("ilosc", 1) <= 0 or not reachable(state, item):
            continue
        for tag in item.get("daje", []):
            out.setdefault(tag, item["nazwa"])
    return out


def modifier_applies(state, char, m, action_id, act, have):
    """Czy stały modyfikator postaci (np. słabość) działa przy tej akcji."""
    if not m.get("aktywny", True):
        return False
    if m.get("do") and state["czas"] >= m["do"]:
        return False
    # Warunki.
    if m.get("gdy_brak") and m["gdy_brak"] in have:
        return False
    if m.get("min_zmeczenie") and char.get("zmeczenie", 0) < m["min_zmeczenie"]:
        return False
    if m.get("w_ciemnosci") and world.light(state) != "ciemnosc":
        return False
    # Zakres.
    return bool(m.get("wszystko")
                or act["umiejetnosc"] in m.get("umiejetnosci", [])
                or action_id in m.get("akcje", [])
                or (m.get("fizyczne") and act.get("fizyczna")))


# --- wycena -------------------------------------------------------------------

def build_quote(state, cat, action_id, approach="normalnie", circumstance=None,
                book=False, helper=None, params=None, extra_steps=None):
    """Liczy wycenę. circumstance = (kroki, powód) albo None.

    extra_steps: kroki dodane przez silnik walki (broń, etap sztywnego).
    """
    char = living_character(state)
    act = get_action(cat, action_id)
    params = dict(params or {})
    if approach not in rules.APPROACHES:
        raise GameError("Podejście: szybko, normalnie albo porzadnie.")
    skill = act["umiejetnosc"]
    level = char["umiejetnosci"][skill]
    steps = []
    node = world.current_node(state)

    ap = rules.APPROACHES[approach]
    if ap["kroki"]:
        steps.append((f"podejście: {approach}", ap["kroki"]))

    # Narzędzia.
    have = provided(state)
    for need in act.get("wymaga", []):
        if need not in have:
            raise GameError(f"Ta akcja wymaga: {need}. Postać tego nie ma.")
    helpful = [t for t in act.get("narzedzia", []) if t in have]
    tool = helpful[0] if helpful else None
    if tool:
        steps.append((f"narzędzie: {have[tool]}", 1))
    elif act.get("bez_narzedzia"):
        steps.append(("brak właściwego narzędzia", act["bez_narzedzia"]))

    # Tagi życiorysu: łącznie najwyżej +1.
    node_type = (node or {}).get("typ")
    for tag in char.get("tagi", []):
        entries = tag.get("akcje", [])
        if (action_id in entries or f"akcja:{action_id}" in entries
                or (node_type and f"miejsce:{node_type}" in entries)):
            steps.append((f"tag: {tag['nazwa']}", 1))
            break

    minutes_extra = 0
    if book:
        books = [i for i in state["ekwipunek"]
                 if "ksiazka" in i.get("daje", []) and reachable(state, i)
                 and action_id in i.get("akcje", [])]
        if not books:
            raise GameError("Postać nie ma książki pasującej do tej akcji.")
        steps.append((f"książka: {books[0]['nazwa']}", 1))
        minutes_extra += 10

    if helper:
        mates = [m for m in state.get("towarzysze", [])
                 if m.get("imie") == helper and not m.get("martwy")]
        if not mates:
            raise GameError(f"Nie ma żywego towarzysza „{helper}”.")
        steps.append((f"pomoc: {helper}", 1))

    # Rany w pasującej części ciała: liczy się najgorsza.
    parts = act.get("czesci", [])
    worst = None
    for w in char["rany"]:
        val = rules.WOUND_STEPS.get(w["ciezkosc"], 0)
        if w["miejsce"] in parts and val and (worst is None or val < worst[1]):
            worst = (f"rana: {rules.wound_name(w)}", val)
    if worst:
        steps.append(worst)

    infection = max((w.get("zakazenie", 0) for w in char["rany"]), default=0)
    if infection >= 3:
        steps.append(("sepsa", -2))
    elif infection == 2:
        steps.append(("gorączka", -1))

    from .body import disease_steps
    steps += disease_steps(char)

    if act.get("fizyczna"):
        for track, name in (("zmeczenie", "zmęczenie"), ("glod", "głód")):
            over = char.get(track, 0) - 2
            if over > 0:
                steps.append((f"{name} {char[track]}", -over))

    if skill in rules.NERVE_SKILLS:
        nerves = char.get("nerwy", 0)
        if nerves >= 8:
            steps.append((f"nerwy {nerves}", -2))
        elif nerves >= 5:
            steps.append((f"nerwy {nerves}", -1))

    if act.get("wzrokowa"):
        lvl = world.light(state)
        if lvl == "polmrok":
            steps.append(("półmrok", -1))
        elif lvl == "ciemnosc":
            steps.append(("ciemność", -2))

    for m in char.get("modyfikatory", []):
        if modifier_applies(state, char, m, action_id, act, have):
            steps.append((m["zrodlo"], m["kroki"]))

    # Parametry akcji.
    wanted = act.get("parametry", {})
    for key in wanted:
        if key not in params or params[key] in (None, ""):
            raise GameError(f"Akcja wymaga parametru --{key} "
                            f"({wanted[key]}).")
    if "nastawienie" in wanted:
        att = params["nastawienie"]
        if att not in rules.ATTITUDES:
            raise GameError("Nastawienie: wrogi, nieufny, obojetny, "
                            "przyjazny.")
        if rules.ATTITUDES[att]:
            steps.append((f"nastawienie: {att}", rules.ATTITUDES[att]))
        if params.get("oferta"):
            steps.append(("oferta, której potrzebuje", 1))
    if "cel" in wanted:
        wid = int(params["cel"])
        if not any(w["id"] == wid for w in char["rany"]):
            raise GameError(f"Postać nie ma rany #{wid}.")
        params["cel"] = wid

    if act.get("efekt") == "przeszukanie":
        from . import loot
        loot.table_for(state)   # błąd, jeśli miejsca nie da się przeszukać

    base_minutes = act["minuty"]
    if "do" in wanted:
        target = params["do"]
        links = (node or {}).get("sasiedzi", {})
        if target not in links:
            here = (node or {}).get("nazwa", "brak węzła")
            raise GameError(f"Z „{here}” nie ma przejścia do „{target}”.")
        base_minutes = links[target]

    if circumstance:
        n, reason = circumstance
        if n not in (-1, 1):
            raise GameError("Okoliczność MG to dokładnie +1 albo -1.")
        if not reason or not reason.strip():
            raise GameError("Okoliczność MG wymaga uzasadnienia (--powod).")
        steps.append((f"okoliczność MG: {reason.strip()}", n))

    steps += [s for s in (extra_steps or []) if s[1]]
    total = sum(v for _, v in steps)
    p = rules.chance(level, total)
    minutes = max(1, round(base_minutes * ap["czas"])) + minutes_extra
    noise = rules.clamp(act["halas"] + ap["halas"], 0, 5)
    return {
        "akcja": action_id,
        "nazwa": act["nazwa"],
        "umiejetnosc": skill,
        "poziom": level,
        "kroki": steps,
        "suma_krokow": total,
        "szansa": p,
        "etykieta": rules.label(p),
        "podejscie": approach,
        "minuty": minutes,
        "halas": noise,
        "porazka": act["porazka"]["tekst"],
        "okolicznosc": ({"kroki": circumstance[0],
                         "powod": circumstance[1].strip()}
                        if circumstance else None),
        "parametry": params,
        "narzedzie": tool,
        "czas": state["czas"],
        "wezel": state["lokacja"].get("wezel"),
        "status": "otwarta",
    }


# --- rzut i skutki -----------------------------------------------------------

def roll(act, quote):
    """Rzut i z góry wylosowane pozycje tabel (żeby Fart nie był przerzutem)."""
    u = rng().randint(1, 100)
    g = rules.grade(u, quote["szansa"], quote["podejscie"])
    costs = act.get("koszty", [])
    cats = act.get("katastrofy", [])
    return {
        "u": u,
        "stopien": g,
        "koszt_nr": rng().randrange(len(costs)) if costs else None,
        "katastrofa_nr": rng().randrange(len(cats)) if cats else None,
    }


def effects_for(act, rolled, grade):
    effects = []
    if grade in ("czysty", "koszt") and act.get("sukces"):
        effects.append(("sukces", act["sukces"]))
    if grade == "koszt" and rolled["koszt_nr"] is not None:
        effects.append(("koszt", act["koszty"][rolled["koszt_nr"]]))
    if grade in ("porazka", "katastrofa"):
        effects.append(("porazka", act["porazka"]))
    if grade == "katastrofa" and rolled["katastrofa_nr"] is not None:
        effects.append(("katastrofa", act["katastrofy"][rolled["katastrofa_nr"]]))
    return effects


def apply(state, act, quote, rolled, grade):
    """Stosuje skutki wyniku do stanu. Zwraca listę (rodzaj, tekst)."""
    char = state["postac"]
    out = []
    effects = effects_for(act, rolled, grade)
    minutes = quote["minuty"]
    noise = quote["halas"]
    target = quote["parametry"].get("cel")
    for kind, eff in effects:
        if eff.get("tekst"):
            out.append((kind, eff["tekst"]))
        minutes += eff.get("minuty", 0)
        noise += eff.get("halas", 0)
        if "rana" in eff:
            w = world.add_wound(state, eff["rana"]["miejsce"],
                                eff["rana"]["ciezkosc"])
            out.append(("cialo", f"Nowa rana #{w['id']}: {rules.wound_name(w)}"
                                 + (f", krwawienie {w['krwawienie']}"
                                    if w["krwawienie"] else "") + "."))
        if eff.get("zmeczenie"):
            char["zmeczenie"] = rules.clamp(
                char["zmeczenie"] + eff["zmeczenie"], 0, 5)
            out.append(("cialo", f"Zmęczenie: {char['zmeczenie']}."))
        if eff.get("nerwy"):
            char["nerwy"] = rules.clamp(char["nerwy"] + eff["nerwy"], 0, 10)
            out.append(("cialo", f"Nerwy: {char['nerwy']}."))
        if eff.get("zakazenie") and target is not None:
            for w in char["rany"]:
                if w["id"] == target:
                    w["zakazenie"] = rules.clamp(
                        w["zakazenie"] + eff["zakazenie"], 0, 4)
                    out.append(("cialo", f"Zakażenie rany #{target}: "
                                         f"{w['zakazenie']}."))
        if eff.get("zuzycie"):
            out.append(("koszt", f"Zużycie: {eff['zuzycie']}."))

    success = grade in ("czysty", "koszt")
    special = act.get("efekt")
    if success and special == "opatrz":
        for w in char["rany"]:
            if w["id"] == target:
                w["opatrzona"] = True
                w["krwawienie"] = None
                w["licznik_krwawienia"] = 0
        world.update_critical(char)
        out.append(("cialo", f"Rana #{target} opatrzona, nie krwawi."))
    if success and special == "barykada":
        node = world.current_node(state)
        if node:
            before = node.get("barykada", 0)
            node["barykada"] = min(10, before + (3 if grade == "czysty" else 2))
            out.append(("stan", f"Barykada w „{node['nazwa']}”: "
                                f"{before} → {node['barykada']}."))

    # Zużycie materiałów: jedna sztuka użytego narzędzia z listy „zuzywa”.
    used = quote.get("narzedzie")
    if used and used in act.get("zuzywa", []):
        for item in state["ekwipunek"]:
            if (used in item.get("daje", []) and item.get("ilosc", 1) > 0
                    and reachable(state, item)):
                item["ilosc"] = item.get("ilosc", 1) - 1
                out.append(("stan", f"Zużyto: {item['nazwa']} "
                                    f"(zostało {item['ilosc']})."))
                break
        state["ekwipunek"] = [i for i in state["ekwipunek"]
                              if i.get("ilosc", 1) > 0]

    out += world.pass_time(state, minutes, noise)
    if special == "przeszukanie":
        from . import loot
        out += loot.search(state, grade)
    if special == "przejscie":
        dest = quote["parametry"]["do"]
        state["lokacja"]["wezel"] = dest
        state["ukrycie"] = False
        out.append(("stan", f"Postać jest teraz w „"
                            f"{state['wezly'][dest]['nazwa']}”."))
    return out


def add_mark(char, skill):
    marks = char.setdefault("znaczniki", {})
    marks[skill] = marks.get(skill, 0) + 1
    need = 3 * char["umiejetnosci"][skill]
    return marks[skill], need
