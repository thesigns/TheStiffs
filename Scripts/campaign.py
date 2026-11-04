"""Zakładanie i przygotowanie kampanii.

Użycie (z katalogu głównego repozytorium):
  python Scripts/campaign.py nowa <kampania> [--start 1990-03-21T23:30]
  python Scripts/campaign.py wezel <kampania> <id> --nazwa "<nazwa>" --typ <typ>
        [--gestosc 0-100] [--zrodlo <źródło>] [--swiatlo dzien|polmrok|ciemnosc]
        [--drzwi brak|zwykle|zamek] [--bez-kryjowek]
  python Scripts/campaign.py polacz <kampania> <id1> <id2> --minuty N
  python Scripts/campaign.py umiesc <kampania> <id węzła>
  python Scripts/campaign.py znajomy <kampania> "<opis>" --wezel <id>
        (sąsiedzi i znajomi ze scenariusza; ich los losuje skrypt)
  python Scripts/campaign.py sztywny <kampania> "<opis>" --wezel <id>
        [--etap swiezak|gnilec] [--znajomy <nr>]
        (sztywni ze scenariusza; spotkanie zaczyna się samo w tym węźle)
  python Scripts/campaign.py ustal <kampania> <nr znajomego> --wpis <nr logu>
        [--tak-znaczy zywy|martwy]   (los „nieznany” według act.py los)
  python Scripts/campaign.py zegar <kampania> <id> +1|-1 --powod "..."
        (skutek działań postaci; samo tykanie robi świt)
  python Scripts/campaign.py start <kampania>
  python Scripts/campaign.py stan <kampania>
  python Scripts/campaign.py automat <kampania> <próg %|off>

Węzły, połączenia i miejsce startu można ustawiać tylko przed startem
kampanii. Po starcie scenariusz jest zamrożony.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import render, rules, world  # noqa: E402
from stiffs.core import Campaign, GameError, run, say  # noqa: E402


def before_start(camp):
    if camp.state["rozpoczeta"]:
        raise GameError("Kampania już się zaczęła. Scenariusz jest "
                        "zamrożony; nowe miejsca tylko przez addendum.py.")


def node_or_error(state, node_id):
    if node_id not in state["wezly"]:
        raise GameError(f"Nie ma węzła „{node_id}”.")
    return state["wezly"][node_id]


def cmd_nowa(args):
    try:
        world.parse(args.start)
    except ValueError:
        raise GameError("Start w formacie RRRR-MM-DDTGG:MM.")
    camp = Campaign.create(args.kampania, args.start)
    say(f"Utworzono kampanię „{args.kampania}” w {camp.path}.")
    say(f"Czas startu: {world.human(world.parse(args.start))}.")


def cmd_wezel(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    if args.swiatlo and args.swiatlo not in rules.LIGHT_NAMES:
        raise GameError("Światło: dzien, polmrok albo ciemnosc.")
    nodes = camp.state["wezly"]
    node = nodes.setdefault(args.id, {"uwaga": 0, "sasiedzi": {}})
    node.update({"nazwa": args.nazwa, "typ": args.typ,
                 "gestosc": rules.clamp(args.gestosc, 0, 100),
                 "zrodlo": args.zrodlo, "swiatlo": args.swiatlo,
                 "drzwi": args.drzwi, "kryjowki": not args.bez_kryjowek})
    camp.log("wezel", id=args.id, **{k: node[k] for k in
                                     ("nazwa", "typ", "gestosc", "zrodlo",
                                      "swiatlo", "drzwi", "kryjowki")})
    camp.save()
    say(f"Węzeł „{args.id}”: {args.nazwa} ({args.typ}).")


def cmd_polacz(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    a = node_or_error(camp.state, args.a)
    b = node_or_error(camp.state, args.b)
    if args.minuty <= 0:
        raise GameError("Przejście musi trwać co najmniej minutę.")
    a["sasiedzi"][args.b] = args.minuty
    b["sasiedzi"][args.a] = args.minuty
    camp.log("polaczenie", a=args.a, b=args.b, minuty=args.minuty)
    camp.save()
    say(f"Połączono „{args.a}” i „{args.b}” ({args.minuty} min).")


def cmd_umiesc(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    node_or_error(camp.state, args.id)
    camp.state["lokacja"]["wezel"] = args.id
    camp.log("umiesc", wezel=args.id)
    camp.save()
    say(f"Postać zaczyna w „{camp.state['wezly'][args.id]['nazwa']}”.")


def cmd_znajomy(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    node_or_error(camp.state, args.wezel)
    known = camp.state.setdefault("znajomi", [])
    from stiffs.core import load_json, rng
    table = load_json("seed.json")["los_znajomych"]
    r = rng().randint(1, sum(w for _, w in table))
    for fate, w in table:
        r -= w
        if r <= 0:
            break
    entry = {"id": len(known) + 1, "opis": args.opis, "wezel": args.wezel,
             "los": fate}
    known.append(entry)
    camp.log("znajomy", **entry)
    camp.save()
    say(f"Znajomy #{entry['id']}: {args.opis} ({args.wezel}). Los "
        "wylosowany i zapisany (tajny; state.json → znajomi).")


def cmd_sztywny(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    node = node_or_error(camp.state, args.wezel)
    entry = {"etap": args.etap, "opis": args.opis}
    if args.znajomy:
        known = {k["id"]: k for k in camp.state.get("znajomi", [])}
        k = known.get(args.znajomy)
        if not k:
            raise GameError(f"Nie ma znajomego #{args.znajomy}.")
        if k["los"] not in ("martwy", "nieznany"):
            raise GameError(f"Znajomy #{k['id']} ma los „{k['los']}”. "
                            "Sztywnym może być tylko martwy albo nieznany.")
        k["los"] = "sztywny"
        entry.update(znajomy=k["id"], znany=True)
    node.setdefault("czeka", []).append(entry)
    camp.log("sztywny_ze_scenariusza", wezel=args.wezel, **entry)
    camp.save()
    say(f"Sztywny ze scenariusza zapisany w węźle „{args.wezel}”. "
        "Spotkanie zacznie się samo, gdy postać tam będzie.")


def cmd_ustal(args):
    """Los znajomego „nieznany” ustalony rzutem z act.py los."""
    camp = Campaign(args.kampania)
    state = camp.state
    k = {x["id"]: x for x in state.get("znajomi", [])}.get(args.nr)
    if not k:
        raise GameError(f"Nie ma znajomego #{args.nr}.")
    if k["los"] != "nieznany":
        raise GameError(f"Los znajomego #{k['id']} to już „{k['los']}”.")
    roll = [e for e in state.get("losy", []) if e["n"] == args.wpis]
    if not roll:
        raise GameError(f"Nie ma rozstrzygnięcia act.py los z wpisem "
                        f"#{args.wpis} w logu.")
    fate = "zywy" if roll[0]["tak"] == (args.tak_znaczy == "zywy") else "martwy"
    k["los"] = fate
    camp.log("los_znajomego", znajomy=k["id"], los=fate, wpis=args.wpis,
             pytanie=roll[0]["pytanie"])
    camp.save()
    say(f"Znajomy #{k['id']}: los ustalony według rozstrzygnięcia "
        f"#{args.wpis}.")


def cmd_zegar(args):
    camp = Campaign(args.kampania)
    if not camp.state["rozpoczeta"]:
        raise GameError("Zegary ruszają dopiero po starcie kampanii.")
    for z in camp.state.get("zegary", []):
        if z["id"] == args.id:
            break
    else:
        raise GameError(f"Nie ma zegara „{args.id}”.")
    if args.zmiana not in ("+1", "-1"):
        raise GameError("Zmiana: +1 albo -1.")
    before = z["stan"]
    z["stan"] = rules.clamp(before + int(args.zmiana), 0, z["segmenty"])
    camp.log("zegar", zegar=z["id"], z=before, na=z["stan"], powod=args.powod)
    camp.save()
    say(f"Zegar „{z['nazwa']}”: {before} → {z['stan']}/{z['segmenty']}. "
        f"Powód: {args.powod}")


def cmd_start(args):
    camp = Campaign(args.kampania)
    before_start(camp)
    state = camp.state
    if not state.get("postac"):
        raise GameError("Najpierw trzeba stworzyć postać.")
    if not state["lokacja"].get("wezel"):
        raise GameError("Najpierw trzeba umieścić postać w węźle (umiesc).")
    if not state.get("ziarno"):
        raise GameError("Najpierw ziarno scenariusza (scenario_seed.py).")
    if not (camp.path / "scenario.md").exists():
        raise GameError("Brak scenario.md. MG pisze scenariusz przed startem.")
    state["rozpoczeta"] = True
    camp.log("start")
    camp.save()
    say(f"Kampania „{args.kampania}” rozpoczęta. Scenariusz jest od teraz "
        "zamrożony.")


def cmd_stan(args):
    camp = Campaign(args.kampania)
    print(render.state_md(camp.state), end="")


def cmd_automat(args):
    camp = Campaign(args.kampania)
    if args.prog == "off":
        value = None
    else:
        try:
            value = int(args.prog)
        except ValueError:
            raise GameError("Próg to liczba 5–95 albo off.")
        if not 5 <= value <= 95:
            raise GameError("Próg to liczba 5–95 albo off.")
    camp.state["ustawienia"]["automat"] = value
    camp.log("automat", prog=value)
    camp.save()
    say("Automat wyłączony." if value is None else
        f"Wyceny z szansą ≥{value}% rzucają się bez potwierdzenia.")


def main():
    p = argparse.ArgumentParser(description="Przygotowanie kampanii.")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("nowa")
    n.add_argument("kampania")
    n.add_argument("--start", default="1990-03-21T23:30")

    w = sub.add_parser("wezel")
    w.add_argument("kampania")
    w.add_argument("id")
    w.add_argument("--nazwa", required=True)
    w.add_argument("--typ", required=True)
    w.add_argument("--gestosc", type=int, default=10)
    w.add_argument("--zrodlo", default="mieszkania")
    w.add_argument("--swiatlo")
    w.add_argument("--drzwi", default="zwykle",
                   choices=["brak", "zwykle", "zamek"])
    w.add_argument("--bez-kryjowek", action="store_true")

    pl = sub.add_parser("polacz")
    pl.add_argument("kampania")
    pl.add_argument("a")
    pl.add_argument("b")
    pl.add_argument("--minuty", type=int, required=True)

    u = sub.add_parser("umiesc")
    u.add_argument("kampania")
    u.add_argument("id")

    z = sub.add_parser("znajomy")
    z.add_argument("kampania")
    z.add_argument("opis")
    z.add_argument("--wezel", required=True)

    sz = sub.add_parser("sztywny")
    sz.add_argument("kampania")
    sz.add_argument("opis")
    sz.add_argument("--wezel", required=True)
    sz.add_argument("--etap", choices=["swiezak", "gnilec"], default="swiezak")
    sz.add_argument("--znajomy", type=int)

    us = sub.add_parser("ustal")
    us.add_argument("kampania")
    us.add_argument("nr", type=int)
    us.add_argument("--wpis", type=int, required=True)
    us.add_argument("--tak-znaczy", choices=["zywy", "martwy"], default="zywy")

    zg = sub.add_parser("zegar")
    zg.add_argument("kampania")
    zg.add_argument("id")
    zg.add_argument("zmiana")
    zg.add_argument("--powod", required=True)

    for name in ("start", "stan"):
        sp = sub.add_parser(name)
        sp.add_argument("kampania")

    a = sub.add_parser("automat")
    a.add_argument("kampania")
    a.add_argument("prog")

    args = p.parse_args()
    {"nowa": cmd_nowa, "wezel": cmd_wezel, "polacz": cmd_polacz,
     "umiesc": cmd_umiesc, "znajomy": cmd_znajomy, "start": cmd_start, "stan": cmd_stan,
     "zegar": cmd_zegar, "sztywny": cmd_sztywny,
     "ustal": cmd_ustal,
     "automat": cmd_automat}[args.cmd](args)


if __name__ == "__main__":
    run(main)
