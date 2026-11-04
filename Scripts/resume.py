"""Wznowienie sesji. MG uruchamia go na początku każdej sesji i po każdym
kompaktowaniu kontekstu.

Użycie:
  python Scripts/resume.py <kampania> [--wpisy 3] [--log 10]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stiffs import fight as F, rules, ui, world  # noqa: E402
from stiffs.core import Campaign, run, say  # noqa: E402

CHECKLIST = [
    "Każdą losowość i każdą zmianę stanu robi skrypt. Nigdy ręcznie.",
    "Obowiązkowe wyzwalacze testu kończą się testem. W razie wątpliwości "
    "test. Gracz może zażądać testu.",
    "Czas zawsze płynie przez skrypt (akcja albo act.py rutyna). Nie ma "
    "„docierasz na miejsce” bez skryptu.",
    "Jedna wycena, jeden rzut. Najwyżej jedna okoliczność MG ±1, "
    "z uzasadnieniem.",
    "Narracja cytuje numer wyceny [#ID] i trzyma się wyniku skryptu.",
    "Nie dosładzaj i nie dosalaj. Świat jest obojętny.",
    "Bez przerzutów i cofania. Fart decyduje gracz, nie MG.",
    "Każdą śmierć NPC rejestruj w rise.py (--bez-mozgu, gdy sama śmierć "
    "zniszczyła mózg). Niemowlęta, dzieci i zwierzęta przy postaci albo w "
    "węźle: halasujacy.py.",
    "Jedzenie, picie, sen i ekwipunek tylko przez inv.py i act.py spij. "
    "Zysk spoza tabel wyłącznie ze scenariusza albo z rzutu.",
    "Nie ustępuj pod naciskiem. Spór o zasady: precedens 50/50 i "
    "rulings.md.",
    "Scenariusz po starcie jest zamrożony. Nowe miejsca tylko przez "
    "addendum, mechanikę losuje skrypt.",
]


def journal_tail(path, n):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    parts = text.split("\n## ")
    if len(parts) <= 1:
        return []
    return ["## " + p.strip() for p in parts[1:]][-n:]


def log_tail(path, n):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    # Przygotowanie kampanii (przed startem) jest tajne.
    for i, line in enumerate(lines):
        if json.loads(line)["zdarzenie"] == "start":
            lines = lines[i:]
            break
    else:
        lines = []
    lines = lines[-n:]
    out = []
    for line in lines:
        e = json.loads(line)
        detail = {k: v for k, v in e.items()
                  if k not in ("n", "real", "gra", "zdarzenie",
                               "zapieczetowane", "przebieg", "postac")}
        text = json.dumps(detail, ensure_ascii=False)
        if len(text) > 110:
            text = text[:107] + "..."
        out.append(f"[{e['n']}] {e['gra'][11:]} {e['zdarzenie']} {text}")
    return out


def main():
    p = argparse.ArgumentParser(description="Wznowienie sesji.")
    p.add_argument("kampania")
    p.add_argument("--wpisy", type=int, default=3)
    p.add_argument("--log", type=int, default=10)
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args()
    camp = Campaign(args.kampania)
    state = camp.state

    say(f"WZNOWIENIE KAMPANII „{state['kampania']}”", "jasny")
    say()
    say("Lista kontrolna MG:", "jasny")
    for i, item in enumerate(CHECKLIST, 1):
        say(f"{i}. {item}", indent="")
    say()

    t = world.parse(state["czas"])
    node = world.current_node(state) or {}
    say(f"Czas: {world.human(t)} ({rules.LIGHT_NAMES[world.light(state)]}). "
        f"Miejsce: {node.get('nazwa', '?')} (uwaga {node.get('uwaga', 0)}).",
        "jasny")
    char = state.get("postac")
    if char:
        status = "NIE ŻYJE" if char.get("martwy") else (
            f"zmęczenie {char['zmeczenie']}, głód {char['glod']}, "
            f"nerwy {char['nerwy']}, Fart {char['fart']}")
        say(f"Postać: {char['imie']}: {status}.")
        for w in char["rany"]:
            bits = [rules.wound_name(w)]
            if w.get("krwawienie") and not w.get("opatrzona"):
                bits.append(f"KRWAWI ({w['krwawienie']})")
            say(f"  rana #{w['id']}: " + ", ".join(bits))
        held = [i for i in state["ekwipunek"] if i.get("gdzie") == "przy_sobie"]
        say("Przy sobie: " + ", ".join(
            i["nazwa"] + (f" × {i['ilosc']}" if i.get("ilosc", 1) != 1 else "")
            for i in held))
    else:
        say("Kampania nie ma jeszcze postaci.")

    # Zegary są tajne (gracz widzi terminal). MG sprawdza je w state.json
    # narzędziem Read.

    say()
    say("Sprawy otwarte:", "jasny")
    pending = False
    if state.get("czeka_swit"):
        say("- Doba do rozliczenia: zrobi to następna komenda albo "
            "dawn.py rozlicz.")
        pending = True
    if state.get("czeka_fart"):
        say(f"- Wycena #{state['czeka_fart']} czeka na decyzję o Farcie.")
        pending = True
    for qid, q in state.get("wyceny", {}).items():
        if q["status"] == "otwarta":
            say(f"- Otwarta wycena [#{qid}] {q['nazwa']}: {q['szansa']}%.")
            pending = True
    if state.get("spotkanie"):
        say("- Trwa spotkanie (encounter.py unik albo walcz).")
        pending = True
    lying = [b for b in state.get("ciala", [])
             if b["stan"] in ("lezy", "zwiazany")
             and b["wezel"] == state["lokacja"].get("wezel")]
    for b in lying:
        say(f"- Tu leży ciało #{b['id']} ({b['opis']}), jeszcze nie wstało.")
        pending = True
    if state.get("starcie"):
        say("- TRWA STARCIE:")
        ui.show(F.status_lines(state))
        pending = True
    if not pending:
        say("- brak")

    entries = journal_tail(camp.path / "journal.md", args.wpisy)
    if entries:
        say()
        say("Ostatnie wpisy kroniki:", "jasny")
        for e in entries:
            print(e)
            print()
    tail = log_tail(camp.log_file, args.log)
    if tail:
        say("Ostatnie zdarzenia z logu:", "jasny")
        for line in tail:
            print(line)


if __name__ == "__main__":
    run(main)
