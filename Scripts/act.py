"""Silnik akcji: wycena, rzut, Fart, czynności rutynowe.

Użycie (z katalogu głównego repozytorium):
  python Scripts/act.py <kampania> akcje
  python Scripts/act.py <kampania> wycen <akcja> [opcje]
  python Scripts/act.py <kampania> rzuc <ID>
  python Scripts/act.py <kampania> rezygnuj <ID>
  python Scripts/act.py <kampania> fart <ID>
  python Scripts/act.py <kampania> przyjmij <ID>
  python Scripts/act.py <kampania> rutyna "<opis>" --minuty N [--halas 0-5]
  python Scripts/act.py <kampania> swiatlo on|off
  python Scripts/act.py <kampania> spij (--godziny N | --do HH:MM)
  python Scripts/act.py <kampania> los "<pytanie>" [--szansa N --zrodlo "..."]
        (pytanie o świat bez odpowiedzi w scenariuszu: 50/50; inna szansa
         tylko z podanym źródłem w scenariuszu)

Opcje wyceny:
  --podejscie szybko|normalnie|porzadnie
  --okolicznosc +1|-1 --powod "<uzasadnienie>"   (najwyżej jedna, MG)
  --ksiazka            postać korzysta z pasującej książki (+10 min)
  --pomoc <imię>       pomoc towarzysza
  --cel <nr rany>      dla opatrunku
  --do <węzeł>         dla przejścia
  --nastawienie wrogi|nieufny|obojetny|przyjazny  [--oferta]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import datetime as dt  # noqa: E402

from stiffs import actions, body, encounter, rules, ui, world  # noqa: E402
from stiffs.core import Campaign, GameError, c, run, say  # noqa: E402

KIND_COLORS = {
    "sukces": "zielony", "koszt": "zolty", "porazka": "czerwony",
    "katastrofa": "czerwony", "cialo": "czerwony", "alarm": "alarm",
    "czas": "szary", "stan": "niebieski", "swit": "jasny",
}

SCRIPT = "python Scripts/act.py"


def print_lines(lines):
    for kind, text in lines:
        say(text, KIND_COLORS.get(kind))


def print_quote(name, qid, q):
    say(f"[#{qid}] {q['nazwa']}", "jasny")
    say(f"{rules.SKILLS[q['umiejetnosc']]} {q['poziom']}, "
        f"podejście: {q['podejscie']}")
    if q["kroki"]:
        say("Kroki:")
        width = max(len(s) for s, _ in q["kroki"])
        for source, val in q["kroki"]:
            say(f"  {source.ljust(width)}  {rules.signed(val)}")
    say(f"Szansa: {q['szansa']}% ({q['etykieta']})", "jasny")
    say(f"Czas: {q['minuty']} min. Hałas: {q['halas']}.")
    say(f"Porażka: {q['porazka']}")


def settle_pending(camp, cat, keep=None):
    """Nowa komenda oznacza rezygnację z Fartu przy oczekującym wyniku."""
    pending = camp.state.get("czeka_fart")
    if pending is None or str(pending) == str(keep):
        return
    say(f"[#{pending}] Bez Fartu, wynik przyjęty.", "szary")
    finish(camp, cat, str(pending), use_fart=False)


def finish(camp, cat, qid, use_fart):
    state = camp.state
    q = state["wyceny"][qid]
    act = actions.get_action(cat, q["akcja"])
    g = q["rzut"]["stopien"]
    if use_fart:
        new = rules.grade_up(g)
        state["postac"]["fart"] -= 1
        camp.log("fart", wycena=int(qid), z=g, na=new)
        say(f"[#{qid}] Fart: {rules.GRADE_NAMES[g]} → "
              f"{rules.GRADE_NAMES[new]}. Zostało Fartu: "
              f"{state['postac']['fart']}.", "jasny")
        g = new
    else:
        camp.log("przyjety", wycena=int(qid), stopien=g)
    lines = actions.apply(state, act, q, q["rzut"], g)
    q["status"] = "zamknieta"
    q["stopien_koncowy"] = g
    state["czeka_fart"] = None
    camp.log("skutki", wycena=int(qid), stopien=g,
             skutki=[t for _, t in lines])
    print_lines(lines)


def cmd_akcje(camp, cat, args):
    for aid, act in cat.items():
        where = "  [tylko w fight.py]" if act.get("walka") else ""
        say(f"{aid.ljust(18)} {act['nazwa']} "
            f"({rules.SKILLS[act['umiejetnosc']]}){where}")


def no_fight(state):
    if state.get("starcie"):
        raise GameError("Trwa starcie. Najpierw trzeba je rozstrzygnąć "
                        "w fight.py.")
    if state.get("spotkanie"):
        raise GameError("Trwa spotkanie. Najpierw encounter.py unik "
                        "albo walcz.")


def cmd_wycen(camp, cat, args):
    state = camp.state
    no_fight(state)
    if actions.get_action(cat, args.akcja).get("walka"):
        raise GameError("To akcja walki. Służy do niej fight.py.")
    settle_pending(camp, cat)
    circ = None
    if args.okolicznosc is not None:
        circ = (args.okolicznosc, args.powod or "")
    elif args.powod:
        raise GameError("--powod bez --okolicznosc nie ma sensu.")
    params = {"cel": args.cel, "do": args.do, "nastawienie": args.nastawienie,
              "oferta": args.oferta}
    q = actions.build_quote(state, cat, args.akcja, args.podejscie, circ,
                            args.ksiazka, args.pomoc, params)

    # Ta sama akcja w tej samej sytuacji (to samo miejsce, ten sam czas).
    warnings = []
    for oid, old in state["wyceny"].items():
        same = (old["akcja"] == q["akcja"] and old["wezel"] == q["wezel"]
                and old["czas"] == q["czas"])
        if not same or old["status"] not in ("otwarta", "anulowana"):
            continue
        if old["status"] == "otwarta":
            old["status"] = "anulowana"
            camp.log("rezygnacja", wycena=int(oid), powod="nowa wycena")
        if old.get("okolicznosc") != q["okolicznosc"]:
            warnings.append(f"Zmieniona okoliczność MG względem [#{oid}].")
        else:
            warnings.append(f"Ponowna wycena tej samej akcji (po [#{oid}]).")

    qid = str(camp.next_id("wycena"))
    state["wyceny"][qid] = q
    camp.log("wycena", wycena=int(qid), akcja=q["akcja"],
             podejscie=q["podejscie"], kroki=q["kroki"], szansa=q["szansa"],
             minuty=q["minuty"], halas=q["halas"],
             okolicznosc=q["okolicznosc"], parametry=q["parametry"],
             ostrzezenia=warnings)
    print_quote(camp.name, qid, q)
    for w in warnings:
        say(f"UWAGA: {w} Zapisano w logu.", "zolty")

    auto = state["ustawienia"].get("automat")
    if auto is not None and q["szansa"] >= auto:
        say(f"Automat (≥{auto}%): rzut bez pytania.", "szary")
        do_roll(camp, cat, qid)
    else:
        say(f"Rzut: {SCRIPT} {camp.name} rzuc {qid}", "szary")
    trim(state)
    camp.save()


def do_roll(camp, cat, qid):
    state = camp.state
    q = state["wyceny"].get(qid)
    if not q:
        raise GameError(f"Nie ma wyceny #{qid}.")
    if q["status"] != "otwarta":
        raise GameError(f"Wycena #{qid} ma status „{q['status']}”. "
                        "Jedna wycena, jeden rzut.")
    if q["czas"] != state["czas"] or q["wezel"] != state["lokacja"]["wezel"]:
        q["status"] = "nieaktualna"
        camp.log("nieaktualna", wycena=int(qid))
        camp.save()
        raise GameError(f"Wycena #{qid} jest nieaktualna (minął czas albo "
                        "postać zmieniła miejsce). Trzeba wycenić od nowa.")
    actions.living_character(state)
    act = actions.get_action(cat, q["akcja"])
    if q["szansa"] >= 95:
        r = {"u": None, "stopien": "czysty", "koszt_nr": None,
             "katastrofa_nr": None}
    else:
        r = actions.roll(act, q)
    q["rzut"] = r
    g = r["stopien"]
    char = state["postac"]
    mark = None
    if q["szansa"] <= rules.MARK_THRESHOLD:
        mark = actions.add_mark(char, q["umiejetnosc"])
    camp.log("rzut", wycena=int(qid), szansa=q["szansa"], wynik=r["u"],
             stopien=g, koszt_nr=r["koszt_nr"],
             katastrofa_nr=r["katastrofa_nr"], znacznik=bool(mark))

    if r["u"] is None:
        head = f"[#{qid}] {q['nazwa']}: {q['szansa']}%, bez rzutu → "
    else:
        head = f"[#{qid}] {q['nazwa']}: {q['szansa']}%, wypadło {r['u']} → "
    say(head + c(rules.GRADE_NAMES[g], rules.GRADE_COLORS[g]))
    if mark:
        say(f"Znacznik rozwoju: {rules.SKILLS[q['umiejetnosc']]} "
              f"({mark[0]}/{mark[1]}).", "szary")

    if g != "czysty" and char.get("fart", 0) > 0:
        q["status"] = "czeka_na_fart"
        state["czeka_fart"] = int(qid)
        better = rules.grade_up(g)
        say(f"Fart: {char['fart']}. Może zmienić wynik na "
              f"{rules.GRADE_NAMES[better]}. Decyzja należy do gracza:", "jasny")
        say(f"  {SCRIPT} {camp.name} fart {qid}")
        say(f"  {SCRIPT} {camp.name} przyjmij {qid}"
            "   (albo następna komenda)")
    else:
        finish(camp, cat, qid, use_fart=False)


def cmd_rzuc(camp, cat, args):
    settle_pending(camp, cat)
    do_roll(camp, cat, args.id)
    camp.save()


def cmd_fart(camp, cat, args):
    state = camp.state
    if str(state.get("czeka_fart")) != args.id:
        raise GameError(f"Wynik #{args.id} nie czeka na decyzję o Farcie.")
    finish(camp, cat, args.id, use_fart=True)
    camp.save()


def cmd_przyjmij(camp, cat, args):
    if str(camp.state.get("czeka_fart")) != args.id:
        raise GameError(f"Wynik #{args.id} nie czeka na decyzję.")
    finish(camp, cat, args.id, use_fart=False)
    camp.save()


def cmd_rezygnuj(camp, cat, args):
    q = camp.state["wyceny"].get(args.id)
    if not q or q["status"] != "otwarta":
        raise GameError(f"Nie ma otwartej wyceny #{args.id}.")
    q["status"] = "anulowana"
    camp.log("rezygnacja", wycena=int(args.id), powod="gracz")
    say(f"[#{args.id}] Gracz rezygnuje z akcji.")
    camp.save()


def cmd_rutyna(camp, cat, args):
    state = camp.state
    no_fight(state)
    settle_pending(camp, cat)
    actions.living_character(state)
    if args.minuty < 0:
        raise GameError("Czas nie płynie wstecz.")
    noise = rules.clamp(args.halas, 0, 5)
    lines = world.pass_time(state, args.minuty, noise)
    camp.log("rutyna", opis=args.opis, minuty=args.minuty, halas=noise,
             zdarzenia=[t for _, t in lines])
    say(args.opis, "jasny")
    print_lines(lines)
    camp.save()


def cmd_spij(camp, cat, args):
    state = camp.state
    no_fight(state)
    settle_pending(camp, cat)
    char = actions.living_character(state)
    now = world.parse(state["czas"])
    if args.do:
        hh, mm = (int(x) for x in args.do.split(":"))
        end = now.replace(hour=hh, minute=mm)
        if end <= now:
            end += dt.timedelta(days=1)
        minutes = int((end - now).total_seconds() // 60)
    else:
        minutes = int(round(args.godziny * 60))
    if not 10 <= minutes <= 16 * 60:
        raise GameError("Sen trwa od 10 minut do 16 godzin.")
    safe = body.safe_place(state)
    node = world.current_node(state) or {}
    say(f"Postać kładzie się spać w „{node.get('nazwa', '?')}” "
        f"({'bezpieczne' if safe else 'niepewne'} miejsce), "
        f"planowo do {world.human(now + dt.timedelta(minutes=minutes))}.",
        "jasny")
    if char.get("swiatlo"):
        say("Światło zostaje zapalone na czas snu.", "zolty")

    char["spi"] = True
    slept = 0
    events = []
    interrupted = None
    while slept < minutes:
        step = min(10 - world.parse(state["czas"]).minute % 10,
                   minutes - slept)
        before = state["czas"]
        lines = world.advance(state, step)
        slept += step
        body.day(char, state)["sen_min"] += step
        lines = [x for x in lines if x[0] != "swit"]
        if state.get("czeka_swit"):
            print_lines(lines)
            events += [t for _, t in lines]
            lines = []
            ui.dawn(camp)
        lines += encounter.after(state, before)
        print_lines(lines)
        events += [t for _, t in lines]
        if char.get("martwy"):
            interrupted = "śmierć"
            break
        if state.get("spotkanie") or state.get("starcie"):
            interrupted = "spotkanie"
            break
    char["spi"] = False
    if interrupted == "spotkanie":
        say(f"Sen przerwany po {slept} min.", "alarm")
    if not char.get("martwy"):
        wake_lines = body.wake(state, char, slept, safe)
        print_lines(wake_lines)
        events += [t for _, t in wake_lines]
    camp.log("sen", minuty=slept, planowane=minutes, bezpieczne=safe,
             przerwany=interrupted, zdarzenia=events)
    camp.save()


def cmd_los(camp, cat, args):
    if args.szansa != 50 and not args.zrodlo:
        raise GameError("Szansa inna niż 50% tylko ze źródłem w scenariuszu "
                        "(--zrodlo \"scenario.md: <sekcja>\").")
    if not 1 <= args.szansa <= 99:
        raise GameError("Szansa od 1 do 99%.")
    for e in camp.state.setdefault("losy", []):
        if e["pytanie"].strip().lower() == args.pytanie.strip().lower():
            raise GameError(f"To pytanie już rozstrzygnięto: "
                            f"{'TAK' if e['tak'] else 'NIE'} (log #{e['n']}).")
    u = actions.rng().randint(1, 100)
    yes = u <= args.szansa
    camp.log("los", pytanie=args.pytanie, szansa=args.szansa,
             zrodlo=args.zrodlo, wynik=u, tak=yes)
    camp.state["losy"].append({"pytanie": args.pytanie, "tak": yes,
                               "n": camp.state["liczniki"]["log"]})
    say(f"Los: {args.pytanie} ({args.szansa}%, wypadło {u}) → "
        + c("TAK" if yes else "NIE", "jasny"))
    camp.save()


def cmd_swiatlo(camp, cat, args):
    state = camp.state
    char = actions.living_character(state)
    on = args.stan == "on"
    if on:
        have = actions.provided(state)
        if "swiatlo" not in have:
            raise GameError("Postać nie ma latarki, świecy ani lampy.")
        say(f"Światło włączone: {have['swiatlo']}.")
    else:
        say("Światło zgaszone.")
    char["swiatlo"] = on
    camp.log("swiatlo", wlaczone=on)
    camp.save()


def trim(state, keep=40):
    """Stan trzyma tylko ostatnie wyceny; pełna historia jest w logu."""
    ids = sorted(state["wyceny"], key=int)
    for qid in ids[:-keep]:
        if state["wyceny"][qid]["status"] not in ("otwarta", "czeka_na_fart"):
            del state["wyceny"][qid]


def main():
    p = argparse.ArgumentParser(description="Silnik akcji The Stiffs.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("akcje", help="lista akcji z katalogu")

    w = sub.add_parser("wycen", help="wycena akcji")
    w.add_argument("akcja")
    w.add_argument("--podejscie", default="normalnie",
                   choices=list(rules.APPROACHES))
    w.add_argument("--okolicznosc", type=int, choices=[-1, 1])
    w.add_argument("--powod")
    w.add_argument("--ksiazka", action="store_true")
    w.add_argument("--pomoc")
    w.add_argument("--cel")
    w.add_argument("--do")
    w.add_argument("--nastawienie")
    w.add_argument("--oferta", action="store_true")

    for name in ("rzuc", "fart", "przyjmij", "rezygnuj"):
        sp = sub.add_parser(name)
        sp.add_argument("id")

    r = sub.add_parser("rutyna", help="czynność bez testu")
    r.add_argument("opis")
    r.add_argument("--minuty", type=int, required=True)
    r.add_argument("--halas", type=int, default=0)

    z = sub.add_parser("spij", help="sen (przerywany spotkaniem)")
    g = z.add_mutually_exclusive_group(required=True)
    g.add_argument("--godziny", type=float)
    g.add_argument("--do")

    lo = sub.add_parser("los", help="pytanie o świat, rozstrzyga skrypt")
    lo.add_argument("pytanie")
    lo.add_argument("--szansa", type=int, default=50)
    lo.add_argument("--zrodlo")

    s = sub.add_parser("swiatlo", help="latarka/świeca")
    s.add_argument("stan", choices=["on", "off"])

    args = p.parse_args()
    camp = Campaign(args.kampania)
    cat = actions.catalog()
    old_time = camp.state["czas"]
    handler = {
        "akcje": cmd_akcje, "wycen": cmd_wycen, "rzuc": cmd_rzuc,
        "fart": cmd_fart, "przyjmij": cmd_przyjmij,
        "rezygnuj": cmd_rezygnuj, "rutyna": cmd_rutyna,
        "swiatlo": cmd_swiatlo, "spij": cmd_spij,
        "los": cmd_los,
    }[args.cmd]
    handler(camp, cat, args)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
