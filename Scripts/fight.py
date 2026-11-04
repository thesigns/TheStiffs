"""Walka i pościg. Jedna komenda = jedna wymiana (kilka sekund).

Użycie (z katalogu głównego repozytorium):
  python Scripts/fight.py <kampania> start --swiezaki N --gnilce N
         --strefa 1-4 [--bron lom] [--opis "tramwajarz w mundurze" ...]
  python Scripts/fight.py <kampania> stan
  python Scripts/fight.py <kampania> atak [nr] [--oczy]
  python Scripts/fight.py <kampania> strzal [nr] [--seria] [--oczy]
  python Scripts/fight.py <kampania> odepchnij [nr]
  python Scripts/fight.py <kampania> wyrwij | biegnij | zgub | drzwi | wspinaj
  python Scripts/fight.py <kampania> czekaj | przeladuj | wyciagnij
  python Scripts/fight.py <kampania> bron <rodzaj>
  python Scripts/fight.py <kampania> fart | przyjmij

Strefy: 1 daleko, 2 blisko, 3 na wyciągnięcie ręki, 4 uchwycony.
Start starcia przejmie później encounter.py; do tego czasu liczbę i etap
sztywnych MG bierze ze scenariusza.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import fight as F  # noqa: E402
from stiffs import ui  # noqa: E402
from stiffs.core import Campaign, run, say  # noqa: E402

def main():
    p = argparse.ArgumentParser(description="Walka i pościg.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--swiezaki", type=int, default=0)
    s.add_argument("--gnilce", type=int, default=0)
    s.add_argument("--strefa", type=int, required=True)
    s.add_argument("--bron", default="piesci")
    s.add_argument("--opis", action="append", default=[])
    s.add_argument("--zasadzka", action="store_true",
                   help="wynik zapieczętowanego rzutu na zasadzkę")
    sub.add_parser("stan")
    for name in ("atak", "strzal", "odepchnij"):
        sp = sub.add_parser(name)
        sp.add_argument("cel", nargs="?", type=int)
        if name == "strzal":
            sp.add_argument("--seria", action="store_true")
        if name in ("atak", "strzal"):
            sp.add_argument("--oczy", action="store_true",
                            help="cel: oczy (sztywny ślepnie, nie pada)")
    for name in ("wyrwij", "biegnij", "zgub", "drzwi", "wspinaj", "czekaj",
                 "przeladuj", "wyciagnij", "fart", "przyjmij"):
        sub.add_parser(name)
    b = sub.add_parser("bron")
    b.add_argument("rodzaj")
    args = p.parse_args()

    camp = Campaign(args.kampania)
    state = camp.state
    old_time = state["czas"]
    if args.cmd == "start":
        say("Starcie!", "alarm")
        lines = F.start(state, args.swiezaki, args.gnilce, args.strefa,
                        args.bron, args.opis, args.zasadzka)
        camp.log("starcie_start", swiezaki=args.swiezaki,
                 gnilce=args.gnilce, strefa=args.strefa, bron=args.bron,
                 opisy=args.opis, zasadzka=args.zasadzka)
    elif args.cmd == "stan":
        F.current(state)
        lines = []
    elif args.cmd in ("fart", "przyjmij"):
        lines = F.accept(state, use_fart=args.cmd == "fart")
    else:
        lines = F.act(state, args.cmd, getattr(args, "cel", None),
                      getattr(args, "seria", False),
                      getattr(args, "rodzaj", None),
                      getattr(args, "oczy", False))
    if lines:
        camp.log("wymiana", komenda=args.cmd, przebieg=[t for _, t in lines])
    ui.show(lines)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
