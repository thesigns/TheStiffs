"""Ekwipunek i potrzeby ciała: jedzenie, woda, papierosy, wódka, leki.

Każda zmiana ekwipunku idzie przez ten skrypt i trafia do logu. Zmiany
spoza zasad (zysk, strata, wymiana) wymagają podania powodu.

Użycie:
  python Scripts/inv.py <kampania> lista
  python Scripts/inv.py <kampania> wez <nr> [--ilosc N]
  python Scripts/inv.py <kampania> odloz <nr> [--ilosc N]
  python Scripts/inv.py <kampania> jedz [<nr>]
  python Scripts/inv.py <kampania> pij [<nr>] [--litry N]
  python Scripts/inv.py <kampania> gotuj [--litry N]
  python Scripts/inv.py <kampania> pal
  python Scripts/inv.py <kampania> alkohol
  python Scripts/inv.py <kampania> odkaz <nr rany>
  python Scripts/inv.py <kampania> antybiotyk (<nr rany> | choroba)
  python Scripts/inv.py <kampania> zysk <id> [--ilosc N] [--tutaj] --powod "..."
  python Scripts/inv.py <kampania> strata <nr> [--ilosc N] --powod "..."
  python Scripts/inv.py <kampania> wymien --daj <nr>[:N] ... --dostaje <id>[:N] ...
                        --powod "..." [--wycena <ID>]

Numery przedmiotów pokazuje komenda lista.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import act  # noqa: E402
from stiffs import actions, body, inventory, rules, ui, world  # noqa: E402
from stiffs.core import Campaign, GameError, load_json, run, say  # noqa: E402

SPECIAL = ("zaladowane", "napoczete", "przy_zwlokach")


def label(item):
    qty = item.get("ilosc", 1)
    text = item["nazwa"] + (f" × {qty}" if qty != 1 else "")
    if "napoczete" in item:
        portions = load_json("items.json").get(item["id"], {}).get("porcje", 1)
        text += f" (napoczęte: {item['napoczete']}/{portions})"
    if item.get("przy_zwlokach"):
        text += f" (przy zwłokach: {item['przy_zwlokach']})"
    return text


def numbered(state):
    """Przedmioty pod ręką z numerami: najpierw przy sobie, potem tutaj."""
    here = state["lokacja"].get("wezel")
    own = [i for i in state["ekwipunek"] if i.get("gdzie") == "przy_sobie"]
    local = [i for i in state["ekwipunek"] if i.get("gdzie") == here]
    return own + local


def by_number(state, nr):
    items = numbered(state)
    if not 1 <= nr <= len(items):
        raise GameError(f"Nie ma przedmiotu nr {nr} pod ręką. "
                        "Zobacz: inv.py lista.")
    return items[nr - 1]


def move(state, item, qty, where):
    qty = qty or item.get("ilosc", 1)
    if qty > item.get("ilosc", 1) or qty < 1:
        raise GameError(f"„{item['nazwa']}”: jest {item.get('ilosc', 1)}.")
    if qty == item.get("ilosc", 1):
        item["gdzie"] = where
        item.pop("przy_zwlokach", None)
        moved = item
    else:
        item["ilosc"] -= qty
        moved = {k: v for k, v in item.items() if k not in SPECIAL}
        moved.update(ilosc=qty, gdzie=where)
        state["ekwipunek"].append(moved)
    # Scal z takim samym przedmiotem w miejscu docelowym.
    if not any(k in moved for k in SPECIAL):
        for other in state["ekwipunek"]:
            if (other is not moved and other.get("id") == moved.get("id")
                    and other.get("gdzie") == where
                    and not any(k in other for k in SPECIAL)):
                other["ilosc"] = other.get("ilosc", 1) + moved["ilosc"]
                state["ekwipunek"].remove(moved)
                return other
    return moved


def remove(state, item, qty):
    qty = qty or item.get("ilosc", 1)
    if qty > item.get("ilosc", 1) or qty < 1:
        raise GameError(f"„{item['nazwa']}”: jest {item.get('ilosc', 1)}.")
    item["ilosc"] = item.get("ilosc", 1) - qty
    state["ekwipunek"] = [i for i in state["ekwipunek"]
                          if i.get("ilosc", 1) > 0]


def calm(camp):
    act.no_fight(camp.state)
    act.settle_pending(camp, actions.catalog())
    char = actions.living_character(camp.state)
    body.prune_modifiers(camp.state, char)
    return char


def spend(camp, minutes, noise, lines):
    lines += world.pass_time(camp.state, minutes, noise)
    return lines


def pick(state, nr, tags, what):
    if nr is not None:
        item = by_number(state, nr)
        if not any(t in item.get("daje", []) for t in tags):
            raise GameError(f"„{item['nazwa']}” to nie {what}.")
        return item
    for tag in tags:
        item = body.find(state, tag)
        if item:
            return item
    raise GameError(f"Pod ręką nie ma: {what}.")


# --- komendy -------------------------------------------------------------------

def cmd_lista(camp, args):
    state = camp.state
    here = state["lokacja"].get("wezel")
    items = numbered(state)
    node = world.current_node(state) or {}
    group = None
    for n, item in enumerate(items, 1):
        g = item.get("gdzie")
        if g != group:
            group = g
            say("Przy sobie:" if g == "przy_sobie"
                else f"Tutaj ({node.get('nazwa', '?')}):", "jasny")
        say(f"  {n}. {label(item)}")
    if not items:
        say("Nic pod ręką.")
    elsewhere = {}
    for item in state["ekwipunek"]:
        g = item.get("gdzie")
        if g not in ("przy_sobie", here):
            elsewhere.setdefault(g, []).append(item)
    for g, group in elsewhere.items():
        name = state["wezly"].get(g, {}).get("nazwa", g)
        say(f"Gdzie indziej ({name}): "
            + ", ".join(label(i) for i in group), "szary")
    char = state.get("postac")
    if char and not char.get("martwy"):
        d = body.day(char, state)
        say(f"Ta doba: posiłki {d['posilki']}, woda "
            f"{d['woda_l'] + d['woda_surowa_l']} l, sen {d['sen_min']} min.",
            "szary")


def cmd_wez(camp, args):
    calm(camp)
    state = camp.state
    item = by_number(state, args.nr)
    if item.get("gdzie") == "przy_sobie":
        raise GameError(f"„{item['nazwa']}” postać już ma przy sobie.")
    was = item.get("przy_zwlokach")
    got = move(state, item, args.ilosc, "przy_sobie")
    camp.log("ekwipunek", ruch="wez", przedmiot=got["id"],
             ilosc=args.ilosc or got.get("ilosc", 1), z_zwlok=was)
    say(f"Wzięte: {label(got)}.")


def cmd_odloz(camp, args):
    calm(camp)
    state = camp.state
    item = by_number(state, args.nr)
    if item.get("gdzie") != "przy_sobie":
        raise GameError(f"„{item['nazwa']}” nie jest przy postaci.")
    where = state["lokacja"].get("wezel")
    left = move(state, item, args.ilosc, where)
    camp.log("ekwipunek", ruch="odloz", przedmiot=left["id"],
             ilosc=args.ilosc or left.get("ilosc", 1), wezel=where)
    say(f"Odłożone tutaj: {label(left)}.")


def cmd_jedz(camp, args):
    char = calm(camp)
    state = camp.state
    item = pick(state, args.nr, ["jedzenie", "jedzenie_surowe"], "jedzenie")
    lines = []
    minutes, noise = 15, 0
    if "jedzenie_surowe" in item.get("daje", []) \
            and "jedzenie" not in item.get("daje", []):
        if "ogien" not in actions.provided(state):
            raise GameError(f"„{item['nazwa']}” trzeba ugotować, a postać "
                            "nie ma czym rozpalić ognia.")
        minutes, noise = 45, 1
        lines.append(("info", "Gotowanie na ogniu (45 min, hałas 1, dym)."))
        lines.append(("stan", body.consume(state, body.find(state, "ogien"))
                      + "."))
    rest = body.consume(state, item)
    d = body.day(char, state)
    d["posilki"] += 1
    before = char["glod"]
    if d["posilki"] <= body.MEALS_PER_DAY and before > 0:
        char["glod"] = before - 1
        lines.append(("cialo", f"Posiłek: głód {before} → {char['glod']}."))
    elif before == 0:
        lines.append(("info", "Posiłek. Postać nie była głodna; doba "
                              "z jedzeniem zaliczona."))
    else:
        lines.append(("info", f"Posiłek ponad {body.MEALS_PER_DAY} w tej "
                              "dobie: głód już nie spada."))
    lines.append(("stan", rest + "."))
    spend(camp, minutes, noise, lines)
    camp.log("jedzenie", przedmiot=item["id"], glod=char["glod"],
             posilki=d["posilki"], zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_pij(camp, args):
    char = calm(camp)
    state = camp.state
    lines = []
    raw_total = 0
    clean_total = 0
    for _ in range(args.litry):
        item = pick(state, args.nr, ["woda", "woda_surowa"], "woda")
        raw = "woda_surowa" in item.get("daje", [])
        lines.append(("stan", body.consume(state, item) + "."))
        if raw:
            raw_total += 1
        else:
            clean_total += 1
        if args.nr is not None and item not in state["ekwipunek"]:
            args.nr = None
    d = body.day(char, state)
    d["woda_l"] += clean_total
    d["woda_surowa_l"] += raw_total
    sealed = None
    if raw_total:
        u, sick = body.catch_disease(char)
        sealed = {"wynik": u, "szansa": body.RAW_WATER_SICK, "choroba": sick}
        lines.append(("info", "Surowa woda. Skrypt rzucił na chorobę "
                              "(rzut zapieczętowany, objawy o świcie)."))
    lines.append(("info", f"Wypite: {clean_total + raw_total} l. W tej "
                          f"dobie razem {d['woda_l'] + d['woda_surowa_l']} l."))
    spend(camp, 5, 0, lines)
    camp.log("picie", czysta=clean_total, surowa=raw_total,
             zapieczetowane=sealed, zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_gotuj(camp, args):
    calm(camp)
    state = camp.state
    if "ogien" not in actions.provided(state):
        raise GameError("Postać nie ma czym rozpalić ognia.")
    lines = [("stan", body.consume(state, body.find(state, "ogien")) + ".")]
    for _ in range(args.litry):
        item = body.find(state, "woda_surowa")
        if not item:
            raise GameError("Pod ręką nie ma tyle surowej wody.")
        where = item.get("gdzie", "przy_sobie")
        remove(state, item, 1)
        inventory.add(state, "woda", 1, where)
    minutes = 30 + 10 * args.litry
    lines.append(("info", f"Gotowanie wody: {args.litry} l surowej → "
                          f"czysta ({minutes} min, hałas 1, dym i światło "
                          "ognia)."))
    spend(camp, minutes, 1, lines)
    camp.log("gotowanie_wody", litry=args.litry,
             zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_pal(camp, args):
    char = calm(camp)
    state = camp.state
    item = pick(state, None, ["papierosy"], "papierosy")
    lines = [("stan", body.consume(state, item) + ".")]
    last = char.get("ostatni_papieros")
    now = world.parse(state["czas"])
    if last and (now - world.parse(last)).total_seconds() < \
            body.SMOKE_COOLDOWN * 60:
        lines.append(("info", "Papieros. Ulga dopiero co była: nerwy bez "
                              "zmian (najwyżej raz na godzinę)."))
    else:
        before = char["nerwy"]
        char["nerwy"] = rules.clamp(before - 1, 0, 10)
        char["ostatni_papieros"] = state["czas"]
        lines.append(("cialo", f"Papieros: nerwy {before} → {char['nerwy']}."))
    if world.is_night(state) and (world.current_node(state) or {}).get(
            "gestosc", 10):
        lines.append(("info", "Żar papierosa widać w ciemności z daleka."))
    spend(camp, 10, 0, lines)
    camp.log("papieros", nerwy=char["nerwy"], zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_alkohol(camp, args):
    char = calm(camp)
    state = camp.state
    item = pick(state, None, ["alkohol"], "alkohol")
    lines = [("stan", body.consume(state, item) + ".")]
    before = char["nerwy"]
    char["nerwy"] = rules.clamp(before - 2, 0, 10)
    char["zmeczenie"] = rules.clamp(char["zmeczenie"] + 1, 0, 5)
    body.add_timed_modifier(state, char, "alkohol", -1, body.VODKA_MINUTES)
    lines.append(("cialo", f"Kilka łyków: nerwy {before} → {char['nerwy']}, "
                           f"zmęczenie {char['zmeczenie']}, −1 krok do "
                           "wszystkiego przez 2 godziny."))
    spend(camp, 15, 0, lines)
    camp.log("alkohol", przedmiot=item["id"], nerwy=char["nerwy"],
             zdarzenia=[t for _, t in lines])
    ui.show(lines)


def wound(char, nr):
    for w in char["rany"]:
        if w["id"] == nr:
            return w
    raise GameError(f"Postać nie ma rany #{nr}.")


def cmd_odkaz(camp, args):
    char = calm(camp)
    state = camp.state
    w = wound(char, args.rana)
    item = pick(state, None, ["odkazanie"], "środek do odkażania")
    lines = [("stan", body.consume(state, item) + ".")]
    w["odkazona"] = True
    lines.append(("cialo", f"Rana #{w['id']} odkażona: lepsze szanse w "
                           "najbliższym rzucie na zakażenie o świcie."))
    spend(camp, 10, 0, lines)
    camp.log("odkazenie", rana=w["id"], przedmiot=item["id"],
             zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_antybiotyk(camp, args):
    char = calm(camp)
    state = camp.state
    item = pick(state, None, ["antybiotyk"], "antybiotyk")
    lines = []
    if args.cel == "choroba":
        if not char.get("choroba") or char["choroba"]["poziom"] == 0:
            raise GameError("Postać nie ma objawów choroby.")
        body.day(char, state)["antybiotyk"] = True
        lines.append(("cialo", "Antybiotyk: lepsze szanse na poprawę "
                               "o świcie."))
        target = "choroba"
    else:
        w = wound(char, int(args.cel))
        if not w.get("zakazenie"):
            raise GameError(f"Rana #{w['id']} nie jest zakażona.")
        before = w["zakazenie"]
        w["zakazenie"] = max(0, before - body.ANTIBIOTIC_INFECTION)
        lines.append(("cialo", f"Antybiotyk: zakażenie rany #{w['id']} "
                               f"{before} → {w['zakazenie']}."))
        target = w["id"]
    lines.append(("stan", body.consume(state, item) + "."))
    spend(camp, 5, 0, lines)
    camp.log("antybiotyk", cel=target, zdarzenia=[t for _, t in lines])
    ui.show(lines)


def cmd_zysk(camp, args):
    calm(camp)
    state = camp.state
    where = state["lokacja"]["wezel"] if args.tutaj else "przy_sobie"
    item = inventory.add(state, args.id, args.ilosc, where)
    camp.log("zysk", przedmiot=args.id, ilosc=args.ilosc, gdzie=where,
             powod=args.powod)
    say(f"Zysk: {item['nazwa']} × {args.ilosc} "
        f"({'tutaj' if args.tutaj else 'przy sobie'}). Powód: {args.powod}")
    say("Zysk spoza tabel musi wynikać ze scenariusza albo z rzutu. "
        "Zapisano w logu.", "szary")


def cmd_strata(camp, args):
    calm(camp)
    state = camp.state
    item = by_number(state, args.nr)
    name = item["nazwa"]
    remove(state, item, args.ilosc)
    camp.log("strata", przedmiot=item["id"], ilosc=args.ilosc or "wszystko",
             powod=args.powod)
    say(f"Strata: {name}. Powód: {args.powod}")


def parse_pair(text):
    if ":" in text:
        a, b = text.split(":", 1)
        return a, int(b)
    return text, None


def cmd_wymien(camp, args):
    calm(camp)
    state = camp.state
    if args.wycena:
        q = state["wyceny"].get(str(args.wycena))
        if not q or q.get("status") != "zamknieta" \
                or q.get("stopien_koncowy") not in ("czysty", "koszt"):
            raise GameError(f"Wycena #{args.wycena} nie jest zamkniętym "
                            "sukcesem.")
    given = [(by_number(state, int(nr)), n)
             for nr, n in map(parse_pair, args.daj or [])]
    for item, n in given:
        if item.get("gdzie") != "przy_sobie":
            raise GameError(f"„{item['nazwa']}” nie jest przy postaci.")
    got = [(iid, n or 1) for iid, n in map(parse_pair, args.dostaje or [])]
    items = load_json("items.json")
    for iid, _ in got:
        if iid not in items:
            raise GameError(f"Nieznany przedmiot „{iid}”.")
    out_names = []
    for item, n in given:
        out_names.append(f"{item['nazwa']} × {n or item.get('ilosc', 1)}")
        remove(state, item, n)
    in_names = []
    for iid, n in got:
        it = inventory.add(state, iid, n)
        in_names.append(f"{it['nazwa']} × {n}")
    camp.log("wymiana", daje=out_names, dostaje=in_names, powod=args.powod,
             wycena=args.wycena)
    say("Oddane: " + (", ".join(out_names) or "nic"))
    say("Otrzymane: " + (", ".join(in_names) or "nic"))
    if not args.wycena:
        say("Bez numeru wyceny. Pierwsza prośba do NPC to test "
            "Kombinowania (Rules.md, NPC). Zapisano w logu.", "zolty")


def main():
    p = argparse.ArgumentParser(description="Ekwipunek i potrzeby ciała.")
    p.add_argument("kampania")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lista")
    for name in ("wez", "odloz"):
        sp = sub.add_parser(name)
        sp.add_argument("nr", type=int)
        sp.add_argument("--ilosc", type=int)
    sp = sub.add_parser("jedz")
    sp.add_argument("nr", type=int, nargs="?")
    sp = sub.add_parser("pij")
    sp.add_argument("nr", type=int, nargs="?")
    sp.add_argument("--litry", type=int, default=1)
    sp = sub.add_parser("gotuj")
    sp.add_argument("--litry", type=int, default=1)
    sub.add_parser("pal")
    sub.add_parser("alkohol")
    sp = sub.add_parser("odkaz")
    sp.add_argument("rana", type=int)
    sp = sub.add_parser("antybiotyk")
    sp.add_argument("cel")
    sp = sub.add_parser("zysk")
    sp.add_argument("id")
    sp.add_argument("--ilosc", type=int, default=1)
    sp.add_argument("--tutaj", action="store_true")
    sp.add_argument("--powod", required=True)
    sp = sub.add_parser("strata")
    sp.add_argument("nr", type=int)
    sp.add_argument("--ilosc", type=int)
    sp.add_argument("--powod", required=True)
    sp = sub.add_parser("wymien")
    sp.add_argument("--daj", nargs="*")
    sp.add_argument("--dostaje", nargs="*")
    sp.add_argument("--powod", required=True)
    sp.add_argument("--wycena", type=int)
    args = p.parse_args([a for a in sys.argv[1:] if a != "--no-color"])

    camp = Campaign(args.kampania)
    old_time = camp.state["czas"]
    globals()["cmd_" + args.cmd](camp, args)
    ui.finish(camp, old_time)


if __name__ == "__main__":
    run(main)
