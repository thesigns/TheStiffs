"""Nieświadomi hałasujący: niemowlęta, dzieci i zwierzęta (Rules.md).

Użycie (z katalogu głównego repozytorium):
  python Scripts/halasujacy.py <kampania> dodaj "<opis>" --rodzaj R
         [--wiek N] [--wezel <id>]
  python Scripts/halasujacy.py <kampania> lista
  python Scripts/halasujacy.py <kampania> usun <nr>
  python Scripts/halasujacy.py <kampania> ukryj | wyjdz

Rodzaj: dziecko (z --wiek 0–9), pies, kot, ptak_cichy, ptak_glosny.
Bez --wezel hałasujący jest z postacią (niesiony albo ukryty razem z nią).
Z --wezel stoi w tym węźle (np. ze scenariusza) i rzuca, gdy postać tam jest.
Rzuty robi skrypt co jednostkę czasu i zapisuje w logu; wynik widać dopiero
wtedy, gdy ktoś się odezwie. Postać ukrywa się sama po udanym zgubieniu
pościgu i uniku, a przestaje przy przejściu do innego węzła i na początku
starcia. `ukryj` i `wyjdz` ustawiają to ręcznie (rzuty idą wtedy także
w węźle bez uwagi).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import actions, noisy, ui  # noqa: E402
from stiffs.core import Campaign, GameError, run, say  # noqa: E402


def describe(h, state):
    where = ("z postacią" if h.get("wezel") is None
             else "w: " + state["wezly"].get(h["wezel"], {}).get("nazwa",
                                                                  h["wezel"]))
    extra = f", {h['wiek']} lat" if h["rodzaj"] == "dziecko" else ""
    return (f"#{h['id']} {h['opis']} ({noisy.KIND_NAMES[h['rodzaj']]}{extra}), "
            f"{where}")


def main():
    p = argparse.ArgumentParser(description="Nieświadomi hałasujący.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dodaj")
    d.add_argument("opis")
    d.add_argument("--rodzaj", required=True)
    d.add_argument("--wiek", type=int)
    d.add_argument("--wezel")
    sub.add_parser("lista")
    u = sub.add_parser("usun")
    u.add_argument("nr", type=int)
    sub.add_parser("ukryj")
    sub.add_parser("wyjdz")
    args = p.parse_args()

    camp = Campaign(args.kampania)
    state = camp.state
    old_time = state["czas"]
    state.setdefault("halasujacy", [])
    lines = []
    if args.cmd == "dodaj":
        noisy.validate(args.rodzaj, args.wiek)
        if args.wezel and args.wezel not in state["wezly"]:
            raise GameError(f"Nie ma węzła „{args.wezel}”.")
        state["liczniki"].setdefault("halasujacy", 0)
        state["liczniki"]["halasujacy"] += 1
        h = {"id": state["liczniki"]["halasujacy"], "opis": args.opis,
             "rodzaj": args.rodzaj, "wezel": args.wezel}
        if args.wiek is not None:
            h["wiek"] = args.wiek
        state["halasujacy"].append(h)
        camp.log("halasujacy_dodaj", **h)
        lines = [("stan", "Dodano: " + describe(h, state) + ".")]
    elif args.cmd == "lista":
        for h in state["halasujacy"]:
            say(describe(h, state))
        if state.get("ukrycie"):
            say("Postać się ukrywa.")
    elif args.cmd == "usun":
        found = [h for h in state["halasujacy"] if h["id"] == args.nr]
        if not found:
            raise GameError(f"Nie ma hałasującego #{args.nr}.")
        state["halasujacy"].remove(found[0])
        camp.log("halasujacy_usun", nr=args.nr)
        lines = [("stan", f"Usunięto: #{args.nr} {found[0]['opis']}.")]
    else:
        actions.living_character(state)
        state["ukrycie"] = args.cmd == "ukryj"
        camp.log("ukrycie", ukryta=state["ukrycie"])
        lines = [("stan", "Postać się ukrywa." if state["ukrycie"]
                  else "Postać przestaje się ukrywać.")]
    ui.show(lines)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
