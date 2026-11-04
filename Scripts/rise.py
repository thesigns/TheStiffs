"""Zmarli wstają. Każda śmierć trafia tutaj, a moment powstania losuje skrypt.

Użycie (z katalogu głównego repozytorium):
  python Scripts/rise.py <kampania> dodaj "<kto>" [--znany] [--wezel <id>]
                                                  [--bez-mozgu]
  python Scripts/rise.py <kampania> lista
  python Scripts/rise.py <kampania> zniszcz <nr>   przebicie mózgu (1 minuta)
  python Scripts/rise.py <kampania> zwiaz <nr>     sznur, 10 minut
  python Scripts/rise.py <kampania> spal <nr>      ogień, 30 minut, dym

MG musi dodać tu każdą śmierć NPC, która zdarzy się w grze. Śmierć postaci
gracza rejestruje się sama. Czas powstania jest zapieczętowany: widać go
w logu, ale nie na ekranie.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import actions, encounter as E, rules, ui, world  # noqa: E402
from stiffs.core import Campaign, GameError, run, say  # noqa: E402

STATES = {"lezy": "leży", "zwiazany": "związane", "wstal": "wstało",
          "wstal_zwiazany": "wstało w więzach", "zniszczony": "mózg zniszczony",
          "spalony": "spalone"}


def here_body(state, body_id):
    body = E.body_by_id(state, body_id)
    if body["wezel"] != state["lokacja"].get("wezel"):
        raise GameError(f"Ciało #{body_id} nie leży tutaj.")
    return body


def main():
    p = argparse.ArgumentParser(description="Ciała zmarłych.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dodaj")
    d.add_argument("kto")
    d.add_argument("--znany", action="store_true")
    d.add_argument("--wezel")
    d.add_argument("--bez-mozgu", action="store_true",
                   help="śmierć sama zniszczyła mózg (zob. Rules.md)")
    sub.add_parser("lista")
    for name in ("zniszcz", "zwiaz", "spal"):
        sp = sub.add_parser(name)
        sp.add_argument("nr", type=int)
    args = p.parse_args()

    camp = Campaign(args.kampania)
    state = camp.state
    old_time = state["czas"]
    lines = []
    if args.cmd == "dodaj":
        node = args.wezel or state["lokacja"].get("wezel")
        if node not in state["wezly"]:
            raise GameError(f"Nie ma węzła „{node}”.")
        body = E.add_body(state, args.kto, node, znany=args.znany,
                          bez_mozgu=args.bez_mozgu)
        if args.bez_mozgu:
            lines = [("stan", f"Ciało #{body['id']}: {args.kto}. Mózg "
                              "zniszczony śmiercią, ciało nie wstanie.")]
        else:
            lines = [("alarm", f"Ciało #{body['id']}: {args.kto}. Wstanie w "
                               "ciągu godziny, chyba że ktoś zniszczy mózg.")]
    elif args.cmd == "lista":
        for b in state.get("ciala", []):
            where = state["wezly"].get(b["wezel"], {}).get("nazwa", b["wezel"])
            say(f"#{b['id']} {b['opis']} – {where}, {STATES[b['stan']]}")
    else:
        actions.living_character(state)
        if state.get("starcie"):
            raise GameError("Trwa starcie.")
        body = here_body(state, args.nr)
        if body["stan"] not in ("lezy", "zwiazany"):
            raise GameError(f"Ciało #{args.nr}: {STATES[body['stan']]}.")
        char = state["postac"]
        if args.cmd == "zniszcz":
            body["stan"] = "zniszczony"
            n = 2 if body.get("znany") else 1
            char["nerwy"] = rules.clamp(char["nerwy"] + n, 0, 10)
            lines = [("stan", f"Ciało #{args.nr}: mózg zniszczony. "
                              f"Nerwy +{n}.")]
            lines += world.pass_time(state, 1, 2)
        elif args.cmd == "zwiaz":
            if "sznur" not in actions.provided(state):
                raise GameError("Potrzebny sznur albo lina.")
            body["stan"] = "zwiazany"
            lines = [("stan", f"Ciało #{args.nr} związane.")]
            lines += world.pass_time(state, 10, 1)
        elif args.cmd == "spal":
            if "ogien" not in actions.provided(state):
                raise GameError("Potrzebne zapałki albo inny ogień.")
            body["stan"] = "spalony"
            lines = [("stan", f"Ciało #{args.nr} płonie. Dym widać z daleka.")]
            lines += world.pass_time(state, 30, 1)
            node = world.current_node(state)
            if node:
                node["uwaga"] = node.get("uwaga", 0) + 4
        camp.log("cialo_" + args.cmd, cialo=args.nr)
    ui.show(lines)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
