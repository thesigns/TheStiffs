"""Spotkania. Same się losują po upływie czasu w każdym skrypcie.

Gdy postać zauważy sztywnych pierwsza, gracz wybiera:
  python Scripts/encounter.py <kampania> unik     próba przemknięcia
  python Scripts/encounter.py <kampania> walcz    starcie (dalej fight.py)

Pozostałe komendy:
  python Scripts/encounter.py <kampania> stan
  python Scripts/encounter.py <kampania> bron <rodzaj>   broń trzymana w ręku
  python Scripts/encounter.py <kampania> kryjowka on|off  bieżący węzeł jako
                                                          kryjówka gracza
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import actions, encounter as E, fight as F, ui, world  # noqa: E402
from stiffs.core import Campaign, GameError, run, say  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Spotkania.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("stan", "unik", "walcz"):
        sub.add_parser(name)
    b = sub.add_parser("bron")
    b.add_argument("rodzaj")
    k = sub.add_parser("kryjowka")
    k.add_argument("stan", choices=["on", "off"])
    args = p.parse_args()

    camp = Campaign(args.kampania)
    state = camp.state
    old_time = state["czas"]
    lines = []
    if args.cmd == "stan":
        enc = state.get("spotkanie")
        if not enc:
            say("Nie trwa żadne spotkanie.")
        else:
            lines = E.describe(enc["sztywni"], enc["strefa"])
    elif args.cmd == "unik":
        lines, _ = E.avoid(state)
    elif args.cmd == "walcz":
        lines = E.engage(state)
    elif args.cmd == "bron":
        actions.living_character(state)
        if args.rodzaj not in F.weapons() or args.rodzaj == "kolba":
            raise GameError("Nieznana broń.")
        if args.rodzaj != "piesci" and args.rodzaj not in actions.provided(state):
            raise GameError("Postać nie ma tej broni pod ręką.")
        state["postac"]["bron"] = args.rodzaj
        camp.log("bron_w_reku", bron=args.rodzaj)
        lines = [("info", f"W ręku: {F.weapons()[args.rodzaj]['nazwa']}.")]
    elif args.cmd == "kryjowka":
        node = world.current_node(state)
        if not node:
            raise GameError("Postać nie jest w żadnym węźle.")
        node["kryjowka"] = args.stan == "on"
        camp.log("kryjowka", wezel=state["lokacja"]["wezel"],
                 wlaczona=node["kryjowka"])
        lines = [("stan", f"„{node['nazwa']}”: "
                          + ("kryjówka gracza. Tu nie losuje się spotkań; "
                             "zdarzenia przy kryjówce rozlicza dawn.py."
                             if node["kryjowka"] else "już nie kryjówka."))]
    ui.show(lines)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
