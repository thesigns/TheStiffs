"""Symulacja Monte Carlo starć do kalibracji liczb.

Nie dotyka żadnej kampanii. Rozgrywa wiele starć tym samym silnikiem co
fight.py, z prostą, rozsądną taktyką gracza.

Użycie:
  python Scripts/sim.py --gnilce 1 --bron lom --walka 2
  python Scripts/sim.py --swiezaki 1 --strefa 3 --swiatlo polmrok
  python Scripts/sim.py --tabela      zestaw scenariuszy kalibracyjnych

Taktyka: trzymany → atak krótką bronią albo wyrwanie (co ma większą
szansę); sztywny na wyciągnięcie ręki → atak; zaklinowana broń →
wyciągnięcie; wypadnięta broń → podniesienie; inaczej czekanie.
Fart zużywany na porażkę albo katastrofę.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import fight as F  # noqa: E402
from stiffs import rules  # noqa: E402
from stiffs.core import GameError, new_state, setup_io  # noqa: E402

MAX_EXCHANGES = 60

ITEMS = {
    "lom": ("Łom", ["lom"]), "siekiera": ("Siekiera", ["siekiera"]),
    "mlotek": ("Młotek", ["mlotek"]), "noz": ("Nóż", ["noz"]),
    "saperka": ("Saperka", ["saperka"]), "palka": ("Pałka", ["palka"]),
}


def make_state(args):
    state = new_state("sim", "1990-03-22T12:00")
    state["wezly"] = {"x": {"nazwa": "symulacja", "typ": "blok", "uwaga": 0,
                            "sasiedzi": {}, "swiatlo": args.swiatlo}}
    state["lokacja"]["wezel"] = "x"
    skills = {k: 1 for k in rules.SKILLS}
    skills.update(walka=args.walka, kondycja=args.kondycja)
    state["postac"] = {
        "imie": "Sim", "umiejetnosci": skills, "tagi": [], "modyfikatory": [],
        "zmeczenie": args.zmeczenie, "glod": 0, "nerwy": 0,
        "fart": args.fart, "rany": [], "znaczniki": {}, "swiatlo": False,
        "aktywnosc_min": 0, "krytyczny": False, "martwy": False,
    }
    if args.bron != "piesci":
        name, gives = ITEMS[args.bron]
        state["ekwipunek"] = [{"nazwa": name, "ilosc": 1, "daje": gives,
                               "gdzie": "przy_sobie"}]
    return state


def chance(state, cmd):
    try:
        return F.quote(state, cmd)[0]["szansa"]
    except GameError:
        return None


def decide(state, args):
    fight = state["starcie"]
    if fight.get("zaklinowana"):
        return "wyciagnij", None
    if fight["bron"] == "piesci" and args.bron != "piesci":
        return "bron", args.bron
    if F.holders(fight):
        a, w = chance(state, "atak"), chance(state, "wyrwij")
        return ("atak", None) if (a or 0) >= (w or 0) else ("wyrwij", None)
    if any(s["strefa"] == 3 for s in F.alive_stiffs(fight)):
        return "atak", None
    return "czekaj", None


def one_fight(args):
    state = make_state(args)
    F.start(state, args.swiezaki, args.gnilce, args.strefa, args.bron,
            ambush=args.zasadzka)
    while state.get("starcie"):
        fight = state["starcie"]
        if fight["wymiana"] >= MAX_EXCHANGES:
            break
        if fight.get("czeka"):
            bad = fight["czeka"]["stopien"] in ("porazka", "katastrofa")
            F.accept(state, use_fart=bad)
            continue
        cmd, arg = decide(state, args)
        F.act(state, cmd, arg=arg)
    char = state["postac"]
    return {
        "martwy": char["martwy"],
        "rany": len(char["rany"]),
        "krytyczne": sum(w["ciezkosc"] == "krytyczna" for w in char["rany"]),
        "wymiany": (state.get("ostatnie_starcie") or {}).get("wymiana",
                                                             MAX_EXCHANGES),
    }


def simulate(args):
    n = args.n
    results = [one_fight(args) for _ in range(n)]
    dead = sum(r["martwy"] for r in results)
    clean = sum(not r["martwy"] and r["rany"] == 0 for r in results)
    crit = sum(not r["martwy"] and r["krytyczne"] > 0 for r in results)
    wounded = n - dead - clean
    avg_ex = sum(r["wymiany"] for r in results) / n
    return {"cało": 100 * clean / n, "ranny": 100 * wounded / n,
            "w tym krytycznie": 100 * crit / n, "martwy": 100 * dead / n,
            "wymian": avg_ex}


def describe(args):
    who = []
    if args.swiezaki:
        who.append(f"{args.swiezaki} świeżak")
    if args.gnilce:
        who.append(f"{args.gnilce} gnilec")
    amb = ", zasadzka" if args.zasadzka else ""
    return (f"{' + '.join(who)}, strefa {args.strefa}{amb}, {args.bron}, "
            f"Walka {args.walka}, Kondycja {args.kondycja}, {args.swiatlo}")


def print_result(args, r):
    print(f"{describe(args)}")
    print(f"  cało {r['cało']:5.1f}%  ranny {r['ranny']:5.1f}% "
          f"(krytycznie {r['w tym krytycznie']:4.1f}%)  "
          f"martwy {r['martwy']:5.1f}%  wymian {r['wymian']:.1f}")


TABLE = [
    dict(gnilce=1, swiezaki=0, strefa=2),
    dict(gnilce=3, swiezaki=0, strefa=2),
    dict(gnilce=5, swiezaki=0, strefa=2),
    dict(gnilce=0, swiezaki=1, strefa=2),
    dict(gnilce=0, swiezaki=1, strefa=3, zasadzka=True),
    dict(gnilce=2, swiezaki=1, strefa=2),
]


def main():
    setup_io()
    p = argparse.ArgumentParser(description="Symulacja starć.")
    p.add_argument("--swiezaki", type=int, default=0)
    p.add_argument("--gnilce", type=int, default=0)
    p.add_argument("--strefa", type=int, default=2)
    p.add_argument("--bron", default="lom",
                   choices=["piesci"] + list(ITEMS))
    p.add_argument("--walka", type=int, default=2)
    p.add_argument("--kondycja", type=int, default=2)
    p.add_argument("--zmeczenie", type=int, default=0)
    p.add_argument("--fart", type=int, default=1)
    p.add_argument("--swiatlo", default="dzien",
                   choices=["dzien", "polmrok", "ciemnosc"])
    p.add_argument("--zasadzka", action="store_true")
    p.add_argument("--n", type=int, default=2000)
    p.add_argument("--tabela", action="store_true")
    args = p.parse_args()
    if args.tabela:
        for row in TABLE:
            args.zasadzka = False
            for k, v in row.items():
                setattr(args, k, v)
            print_result(args, simulate(args))
        return
    if args.swiezaki + args.gnilce < 1:
        p.error("Podaj --swiezaki albo --gnilce.")
    print_result(args, simulate(args))


if __name__ == "__main__":
    main()
