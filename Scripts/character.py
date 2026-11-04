"""Kreator postaci.

Postać powstaje z karty Campaigns/<kampania>/postac.json, wypełnionej
odpowiedziami gracza. Skrypt sprawdza kartę, losuje ekwipunek startowy
i zapisuje postać do stanu gry. Ekwipunek losuje się raz i nie da się go
przelosować.

Użycie (z katalogu głównego repozytorium):
  python Scripts/character.py opcje              tagi, słabości i rzeczy
  python Scripts/character.py szablon <kampania> pusta karta postac.json
  python Scripts/character.py sprawdz <kampania> sprawdzenie karty
  python Scripts/character.py utworz <kampania>  utworzenie postaci
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import actions, body, rules  # noqa: E402
from stiffs.core import Campaign, GameError, load_json, rng, run, say  # noqa: E402

CARD = "postac.json"


def catalogs():
    return {
        "przedmioty": load_json("items.json"),
        "tagi": {k: v for k, v in load_json("tags.json").items()
                 if not k.startswith("_")},
        "slabosci": {k: v for k, v in load_json("weaknesses.json").items()
                     if not k.startswith("_")},
        "dom": load_json("household.json"),
        "akcje": actions.catalog(),
    }


def template():
    return {
        "imie": "",
        "nazwisko": "",
        "wiek": 30,
        "zawod": "",
        "wyglad": "",
        "historia": "",
        "umiejetnosci": {sid: rules.SKILL_START for sid in rules.SKILLS},
        "tagi": [],
        "slabosc": "",
        "rzecz": "",
        "adres": {"osiedle": "", "ulica": "", "blok": "", "klatka": "",
                  "pietro": 0, "mieszkanie": ""},
        "dom": "",
        "start": "",
        "noc": {"opis": "", "czynnosci": []},
        "bliscy": [{"imie": "", "relacja": "", "gdzie": ""}],
    }


# --- sprawdzanie karty -------------------------------------------------------

def resolve_tag(entry, cat, errors):
    """Tag z katalogu (identyfikator) albo własny (obiekt)."""
    if isinstance(entry, str):
        if entry not in cat["tagi"]:
            errors.append(f"Nie ma tagu „{entry}” w katalogu.")
            return None
        return {"id": entry, **cat["tagi"][entry]}
    if not isinstance(entry, dict):
        errors.append("Tag to identyfikator z katalogu albo obiekt.")
        return None
    tag = {"id": entry.get("id") or entry.get("nazwa", ""), **entry}
    name = tag.get("nazwa") or "?"
    if not tag.get("nazwa"):
        errors.append("Własny tag musi mieć nazwę.")
    known = set(cat["akcje"]) | rules.PLANNED_ACTIONS
    acts = tag.get("akcje", [])
    if not 3 <= len(acts) <= 5:
        errors.append(f"Tag „{name}”: lista akcji musi mieć 3–5 pozycji.")
    for a in acts:
        if not a.startswith("miejsce:") and a not in known:
            errors.append(f"Tag „{name}”: nieznana akcja „{a}”.")
    if not 1 <= len(tag.get("dostepy", [])) <= 2:
        errors.append(f"Tag „{name}”: 1–2 dostępy fabularne.")
    if not tag.get("rzeczy"):
        errors.append(f"Tag „{name}”: brak listy rzeczy do wyboru.")
    for r in tag.get("rzeczy", []) + tag.get("przedmioty", []):
        if r.get("przedmiot") not in cat["przedmioty"]:
            errors.append(f"Tag „{name}”: nieznany przedmiot "
                          f"„{r.get('przedmiot')}”.")
    return tag


def check(card, state, cat):
    errors = []
    for field in ("imie", "nazwisko", "zawod"):
        if not str(card.get(field, "")).strip():
            errors.append(f"Brak pola „{field}”.")
    if not isinstance(card.get("wiek"), int) or not 16 <= card["wiek"] <= 90:
        errors.append("Wiek: liczba 16–90.")

    skills = card.get("umiejetnosci", {})
    if set(skills) != set(rules.SKILLS):
        errors.append("Umiejętności: dokładnie dziewięć z Rules.md.")
    else:
        for sid, val in skills.items():
            if not isinstance(val, int) or not (
                    rules.SKILL_START <= val <= rules.SKILL_START_MAX):
                errors.append(f"{rules.SKILLS[sid]}: na starcie "
                              f"{rules.SKILL_START}–{rules.SKILL_START_MAX}.")
        spent = sum(skills.values()) - rules.SKILL_START * len(rules.SKILLS)
        if spent != rules.SKILL_POINTS:
            errors.append(f"Rozdano {spent} punktów umiejętności, a trzeba "
                          f"dokładnie {rules.SKILL_POINTS}.")

    tags = [resolve_tag(t, cat, errors) for t in card.get("tagi", [])]
    tags = [t for t in tags if t]
    if not rules.TAGS_MIN <= len(card.get("tagi", [])) <= rules.TAGS_MAX:
        errors.append(f"Tagów życiorysu: {rules.TAGS_MIN}–{rules.TAGS_MAX}.")
    if len({t["id"] for t in tags}) != len(tags):
        errors.append("Tagi się powtarzają.")

    weak = card.get("slabosc")
    if weak not in cat["slabosci"]:
        errors.append("Słabość: jedna z katalogu (character.py opcje).")

    thing = card.get("rzecz")
    allowed = {r["przedmiot"] for t in tags for r in t.get("rzeczy", [])}
    if thing not in allowed:
        errors.append("Rzecz musi pochodzić z listy rzeczy jednego z tagów "
                      f"postaci: {', '.join(sorted(allowed)) or 'brak'}.")

    addr = card.get("adres", {})
    if not addr.get("osiedle") or not addr.get("blok"):
        errors.append("Adres: co najmniej osiedle i blok.")
    home = card.get("dom")
    if home not in state["wezly"]:
        errors.append(f"Dom: „{home}” nie jest węzłem mapy kampanii. "
                      "Najpierw dodaj węzeł mieszkania (campaign.py wezel).")

    start = card.get("start")
    if start and start not in state["wezly"]:
        errors.append(f"Start: „{start}” nie jest węzłem mapy kampanii. "
                      "Puste pole oznacza start w domu.")
    errors += check_night(card, first=not state.get("postac"))

    rel = card.get("bliscy", [])
    if not rules.RELATIVES_MIN <= len(rel) <= rules.RELATIVES_MAX:
        errors.append(f"Bliskich: {rules.RELATIVES_MIN}–"
                      f"{rules.RELATIVES_MAX}.")
    for r in rel:
        if not all(str(r.get(k, "")).strip()
                   for k in ("imie", "relacja", "gdzie")):
            errors.append("Każdy bliski: imię, relacja i gdzie był tej nocy.")
    return errors, tags


def check_night(card, first):
    """Noc zero: opowieść gracza i wiersze tabeli (Rules.md, *Noc zero*)."""
    night = card.get("noc") or {}
    acts = night.get("czynnosci") or []
    errors = []
    if first and not str(night.get("opis", "")).strip():
        errors.append("Noc zero: opisz, co postać robiła od wieczora 21 "
                      "marca do północy (pole noc.opis).")
    if first and not acts:
        errors.append("Noc zero: wybierz co najmniej jedną czynność "
                      "(noc.czynnosci): " + ", ".join(rules.NIGHT_ACTIVITIES)
                      + ".")
    for a in acts:
        if a not in rules.NIGHT_ACTIVITIES:
            errors.append(f"Noc zero: nieznana czynność „{a}”. Znane: "
                          + ", ".join(rules.NIGHT_ACTIVITIES) + ".")
    return errors


STAT_NAMES = {"zmeczenie": "zmęczenie", "glod": "głód", "nerwy": "nerwy"}


def apply_night(state, char, acts):
    """Skutki nocy zero na starcie. Zwraca opis do wypisania."""
    limits = {"zmeczenie": 5, "glod": 5, "nerwy": 10}
    lines = []
    for a in dict.fromkeys(acts):
        label, effects, alcohol = rules.NIGHT_ACTIVITIES[a]
        bits = []
        for stat, delta in effects.items():
            char[stat] = rules.clamp(char[stat] + delta, 0, limits[stat])
            bits.append(f"{STAT_NAMES[stat]} {rules.signed(delta)}")
        if alcohol:
            body.add_timed_modifier(state, char, "alkohol", -1,
                                    body.VODKA_MINUTES)
            bits.append("−1 krok do wszystkiego przez 2 godziny")
        lines.append(f"{label}: " + (", ".join(bits) if bits else "bez skutku"))
    return lines


# --- ekwipunek ---------------------------------------------------------------

def roll_table(table, where, rolled):
    for entry in table:
        u = rng().randint(1, 100)
        if u <= entry["szansa"]:
            lo, hi = entry["ilosc"]
            qty = rng().randint(lo, hi)
            step = entry.get("krok", 1)
            qty = max(step, qty // step * step)
            rolled.append((entry["przedmiot"], qty, where))


def make_items(rolled, cat):
    merged = {}
    for item_id, qty, where in rolled:
        key = (item_id, where)
        merged[key] = merged.get(key, 0) + qty
    items = []
    for (item_id, where), qty in merged.items():
        spec = cat["przedmioty"][item_id]
        item = {"id": item_id, "nazwa": spec["nazwa"], "ilosc": qty,
                "daje": list(spec.get("daje", [])), "gdzie": where}
        if spec.get("akcje"):
            item["akcje"] = list(spec["akcje"])
        items.append(item)
    return items


def starting_equipment(card, tags, cat):
    home = card["dom"]
    rolled = []
    roll_table(cat["dom"]["przy_sobie"], "przy_sobie", rolled)
    roll_table(cat["dom"]["mieszkanie"], home, rolled)
    for t in tags:
        roll_table(t.get("przedmioty", []), home, rolled)
    weak = cat["slabosci"][card["slabosc"]]
    for p in weak.get("przedmioty", []):
        rolled.append((p["przedmiot"], p["ilosc"], "przy_sobie"))
    for t in tags:
        for r in t.get("rzeczy", []):
            if r["przedmiot"] == card["rzecz"]:
                spec = cat["przedmioty"][r["przedmiot"]]
                where = home if "samochod" in spec["daje"] else "przy_sobie"
                rolled.append((r["przedmiot"], r["ilosc"], where))
                break
    return make_items(rolled, cat)


# --- komendy -------------------------------------------------------------------

def cmd_opcje(args):
    cat = catalogs()
    say("TAGI ŻYCIORYSU (wybierz 2–3; +1 krok w wymienionych akcjach/miejscach)",
        "jasny")
    for tid, t in cat["tagi"].items():
        say(f"{tid}: {t['nazwa']}", "jasny")
        say(t["opis"], indent="  ")
        say("akcje: " + ", ".join(t["akcje"]), indent="  ")
        say("dostępy: " + "; ".join(t["dostepy"]), indent="  ")
        things = ", ".join(
            f"{r['przedmiot']} ({cat['przedmioty'][r['przedmiot']]['nazwa']}"
            + (f" × {r['ilosc']}" if r["ilosc"] != 1 else "") + ")"
            for r in t["rzeczy"])
        say("rzeczy do wyboru: " + things, indent="  ")
    say()
    say("SŁABOŚCI (wybierz 1)", "jasny")
    for wid, w in cat["slabosci"].items():
        mods = "; ".join(f"{m['zrodlo']} {rules.signed(m['kroki'])}"
                         for m in w["modyfikatory"])
        say(f"{wid}: {w['nazwa']}. {w['opis']} [{mods}]")
    say()
    say(f"UMIEJĘTNOŚCI: wszystkie zaczynają od {rules.SKILL_START}, do "
        f"rozdania {rules.SKILL_POINTS} punktów, na starcie najwyżej "
        f"{rules.SKILL_START_MAX}.", "jasny")
    say(", ".join(f"{k} ({v})" for k, v in rules.SKILLS.items()))


def cmd_szablon(args):
    camp = Campaign(args.kampania)
    path = camp.path / CARD
    if path.exists():
        raise GameError(f"{path} już istnieje.")
    path.write_text(json.dumps(template(), ensure_ascii=False, indent=2)
                    + "\n", encoding="utf-8")
    say(f"Pusta karta: {path}")


def load_card(camp):
    path = camp.path / CARD
    if not path.exists():
        raise GameError(f"Brak karty {path}. Użyj: character.py szablon.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise GameError(f"Karta {path} nie jest poprawnym JSON-em: {e}")


def can_create(state):
    char = state.get("postac")
    if char and not char.get("martwy"):
        raise GameError("Kampania ma już żyjącą postać. Ekwipunek losuje się "
                        "raz, więc postaci nie tworzy się od nowa.")


def summary(card, tags, cat, state_nodes):
    s = card["umiejetnosci"]
    say(f"{card['imie']} {card['nazwisko']}, {card['wiek']} lat, "
        f"{card['zawod']}", "jasny")
    say("Umiejętności: " + ", ".join(
        f"{rules.SKILLS[k]} {v}" for k, v in s.items()))
    say("Tagi: " + ", ".join(t["nazwa"] for t in tags))
    w = cat["slabosci"][card["slabosc"]]
    say(f"Słabość: {w['nazwa']}")
    say(f"Rzecz: {cat['przedmioty'][card['rzecz']]['nazwa']}")
    a = card["adres"]
    say(f"Adres: {a.get('osiedle')}, {a.get('ulica', '')} {a.get('blok')}"
        f", klatka {a.get('klatka', '?')}, piętro {a.get('pietro', '?')}"
        f", m. {a.get('mieszkanie', '?')}")
    start = card.get("start") or card["dom"]
    night = card.get("noc") or {}
    if night.get("opis"):
        say(f"Noc zero: {night['opis']}")
    say(f"Start: {state_nodes.get(start, start)}")
    say("Bliscy: " + "; ".join(
        f"{r['imie']} ({r['relacja']}), tej nocy: {r['gdzie']}"
        for r in card["bliscy"]))


def node_names(state):
    return {k: v["nazwa"] for k, v in state["wezly"].items()}


def cmd_sprawdz(args):
    camp = Campaign(args.kampania)
    cat = catalogs()
    card = load_card(camp)
    errors, tags = check(card, camp.state, cat)
    if errors:
        say("Karta wymaga poprawek:", "czerwony")
        for e in errors:
            say(f"- {e}")
        sys.exit(1)
    summary(card, tags, cat, node_names(camp.state))
    say("Karta jest poprawna. Utworzenie: character.py utworz.", "zielony")


def cmd_utworz(args):
    camp = Campaign(args.kampania)
    state = camp.state
    can_create(state)
    cat = catalogs()
    card = load_card(camp)
    errors, tags = check(card, state, cat)
    if errors:
        say("Karta wymaga poprawek:", "czerwony")
        for e in errors:
            say(f"- {e}")
        sys.exit(1)

    weak = cat["slabosci"][card["slabosc"]]
    old = state.get("postac")
    number = (old or {}).get("nr", 0) + 1
    char = {
        "nr": number,
        "imie": f"{card['imie']} {card['nazwisko']}",
        "wiek": card["wiek"],
        "zawod": card["zawod"],
        "wyglad": card.get("wyglad", ""),
        "historia": card.get("historia", ""),
        "adres": card["adres"],
        "dom": card["dom"],
        "bliscy": card["bliscy"],
        "umiejetnosci": dict(card["umiejetnosci"]),
        "tagi": [{"id": t["id"], "nazwa": t["nazwa"], "akcje": t["akcje"],
                  "dostepy": t["dostepy"]} for t in tags],
        "slabosc": {"id": card["slabosc"], "nazwa": weak["nazwa"],
                    "opis": weak["opis"]},
        "rzecz": cat["przedmioty"][card["rzecz"]]["nazwa"],
        "modyfikatory": [dict(m) for m in weak["modyfikatory"]],
        "zmeczenie": 0, "glod": 0, "nerwy": 0,
        "fart": rules.START_FART,
        "rany": [], "znaczniki": {}, "swiatlo": False,
        "aktywnosc_min": 0, "krytyczny": False, "martwy": False,
    }
    start = card.get("start") or card["dom"]
    night = card.get("noc") or {}
    night_lines = []
    if not state.get("postac") and night.get("czynnosci"):
        night_lines = apply_night(state, char, night["czynnosci"])
    if night.get("opis"):
        char["noc"] = {"opis": night["opis"],
                       "czynnosci": list(night.get("czynnosci", []))}
    items = starting_equipment(card, tags, cat)

    if old:
        state.setdefault("polegli", []).append(old)
        # Rzeczy poprzedniej postaci zostają tam, gdzie zginęła.
        for item in state["ekwipunek"]:
            if item.get("gdzie", "przy_sobie") == "przy_sobie":
                item["gdzie"] = state["lokacja"].get("wezel")
                item["przy_zwlokach"] = old["imie"]
        state["lokacja"]["wezel"] = start
    elif card.get("start") or not state["lokacja"].get("wezel"):
        state["lokacja"]["wezel"] = start

    state["postac"] = char
    state["ekwipunek"] += items
    camp.log("postac_utworzona", postac=char,
             ekwipunek=[{k: i[k] for k in ("id", "ilosc", "gdzie")}
                        for i in items])
    camp.save()
    (camp.path / CARD).rename(camp.path / f"postac.{number}.json")

    summary(card, tags, cat, node_names(state))
    if night_lines:
        say()
        say("Skutki nocy zero:", "jasny")
        for line in night_lines:
            say("- " + line)
    say()
    say("Ekwipunek startowy (losowany):", "jasny")
    for where, label in (("przy_sobie", "Przy sobie"),
                         (card["dom"], "W mieszkaniu")):
        group = [i for i in items if i["gdzie"] == where]
        if group:
            say(label + ": " + ", ".join(
                i["nazwa"] + (f" × {i['ilosc']}" if i["ilosc"] != 1 else "")
                for i in group))
    say()
    say(f"Postać zapisana. Karta przeniesiona do postac.{number}.json.",
        "zielony")


def main():
    p = argparse.ArgumentParser(description="Kreator postaci.")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("opcje")
    for name in ("szablon", "sprawdz", "utworz"):
        sp = sub.add_parser(name)
        sp.add_argument("kampania")
    args = p.parse_args()
    {"opcje": cmd_opcje, "szablon": cmd_szablon, "sprawdz": cmd_sprawdz,
     "utworz": cmd_utworz}[args.cmd](args)


if __name__ == "__main__":
    run(main)
