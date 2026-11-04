"""Ziarno scenariusza: parametry, których MG nie wybiera.

MG uruchamia go raz, po utworzeniu postaci i przed napisaniem scenariusza.
Skrypt losuje 3 zegary zagrożeń, 2 wrogie frakcje, poziom niedoboru i los
bliskich postaci. Drugi raz nie losuje: ziarna nie da się przelosować.

Użycie:
  python Scripts/scenario_seed.py <kampania>          losuje ziarno
  python Scripts/scenario_seed.py <kampania> pokaz    pokazuje wylosowane
                                                      (tylko dla MG!)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs.core import Campaign, GameError, load_json, rng, run, say  # noqa: E402


def weighted(table):
    total = sum(w for _, w in table)
    r = rng().randint(1, total)
    for name, w in table:
        r -= w
        if r <= 0:
            return name
    return table[-1][0]


def show(state):
    seed = state["ziarno"]
    say("ZIARNO SCENARIUSZA", "jasny")
    say("Zegary zagrożeń (tykają same o świcie):", "jasny")
    for z in state.get("zegary", []):
        say(f"- {z['id']}: {z['nazwa']} ({z['stan']}/{z['segmenty']}). "
            f"{z['opis']}")
    say("Wrogie frakcje:", "jasny")
    for f in seed["frakcje"]:
        say(f"- {f['nazwa']}: {f['opis']}")
    say(f"Niedobór w okolicy: {seed['niedobor']}.")
    say("Los bliskich (zapieczętowany, dla MG):", "jasny")
    for b in seed["bliscy"]:
        say(f"- {b['imie']} ({b['relacja']}): {b['los']}")


def main():
    p = argparse.ArgumentParser(description="Ziarno scenariusza.")
    p.add_argument("kampania")
    p.add_argument("cmd", nargs="?", default="losuj", choices=["losuj", "pokaz"])
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args()
    camp = Campaign(args.kampania)
    state = camp.state
    if args.cmd == "pokaz":
        if not state.get("ziarno"):
            raise GameError("Ziarno nie zostało jeszcze wylosowane.")
        show(state)
        return
    if state.get("ziarno"):
        raise GameError("Ziarno już wylosowano. Nie da się go przelosować "
                        "(pokaż: scenario_seed.py <kampania> pokaz).")
    if state["rozpoczeta"]:
        raise GameError("Kampania już się zaczęła.")
    char = state.get("postac")
    if not char:
        raise GameError("Najpierw postać: los bliskich zależy od karty.")

    pools = load_json("seed.json")
    clocks = rng().sample(pools["zegary"], 3)
    factions = rng().sample(pools["frakcje"], 2)
    seed = {
        "frakcje": [dict(f) for f in factions],
        "niedobor": weighted(pools["niedobor"]),
        "bliscy": [{"imie": b["imie"], "relacja": b["relacja"],
                    "los": weighted(pools["los_bliskich"])}
                   for b in char.get("bliscy", [])],
    }
    state["ziarno"] = seed
    state["zegary"] = [dict(z, stan=0) for z in clocks]
    camp.log("ziarno", zegary=[z["id"] for z in clocks],
             frakcje=[f["id"] for f in factions], niedobor=seed["niedobor"],
             zapieczetowane={"bliscy": seed["bliscy"]})
    camp.save()
    # Bez wydruku: gracz widzi terminal. MG czyta ziarno komendą „pokaz”
    # w agencie przygotowującym scenariusz.
    say("Ziarno wylosowane i zapisane w state.json. Treść jest tajna: "
        "MG czyta ją komendą „pokaz” poza wzrokiem gracza.", "szary")


if __name__ == "__main__":
    run(main)
