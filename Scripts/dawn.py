"""Doba: podgląd i rozliczenie świtu.

Rozliczenie robi się samo po każdej komendzie, która przesunęła zegar
za wschód słońca (gdy nie trwa starcie, spotkanie ani decyzja o Farcie).
Ten skrypt pokazuje stan doby i pozwala rozliczyć ją od razu.

Użycie:
  python Scripts/dawn.py <kampania> stan
  python Scripts/dawn.py <kampania> rozlicz
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import body, rules, ui, world  # noqa: E402
from stiffs.core import Campaign, GameError, run, say  # noqa: E402


def cmd_stan(camp):
    state = camp.state
    t = world.parse(state["czas"])
    s = world.sun_times(t.date())
    say(f"{world.human(t)}. Świt {s['swit']:%H:%M}, wschód "
        f"{s['wschod']:%H:%M}, zachód {s['zachod']:%H:%M}, zmierzch "
        f"{s['zmierzch']:%H:%M}.")
    pog = state.get("pogoda", {})
    if pog.get("niebo"):
        say(f"Pogoda: {pog['niebo']}, {pog['temperatura']}°C"
            + (", przymrozek do " + pog["przymrozek_do"][11:]
               if pog.get("przymrozek_do") else "") + ".")
    char = state.get("postac")
    if char and not char.get("martwy"):
        d = body.day(char, state)
        say(f"Doba od {world.human(world.parse(d['od']))}: posiłki "
            f"{d['posilki']}, woda czysta {d['woda_l']} l, surowa "
            f"{d['woda_surowa_l']} l, sen {d['sen_min']} min.")
        say(f"Głód {char['glod']}, zmęczenie {char['zmeczenie']}, nerwy "
            f"{char['nerwy']}, dni bez wody {char.get('dni_bez_wody', 0)}.")
        if char.get("choroba") and char["choroba"]["poziom"] > 0:
            say(f"Choroba: {char['choroba']['nazwa']} (poziom "
                f"{char['choroba']['poziom']}).")
        marks = char.get("znaczniki", {})
        ready = [rules.SKILLS[k] for k, v in marks.items()
                 if v >= 3 * char["umiejetnosci"][k]
                 and char["umiejetnosci"][k] < rules.SKILL_MAX]
        if ready:
            say("Gotowe do rozwoju przy pełnym śnie w bezpiecznym miejscu: "
                + ", ".join(ready) + ".")
    if state.get("czeka_swit"):
        say("Doba czeka na rozliczenie.", "jasny")


def main():
    p = argparse.ArgumentParser(description="Doba i świt.")
    p.add_argument("kampania")
    p.add_argument("cmd", choices=["stan", "rozlicz"])
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args()
    camp = Campaign(args.kampania)
    old_time = camp.state["czas"]
    if args.cmd == "stan":
        cmd_stan(camp)
        return
    if not camp.state.get("czeka_swit"):
        raise GameError("Nie ma doby do rozliczenia: zegar nie minął "
                        "jeszcze wschodu słońca.")
    if not ui.dawn(camp):
        raise GameError("Najpierw trzeba rozstrzygnąć starcie, spotkanie "
                        "albo decyzję o Farcie.")
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
