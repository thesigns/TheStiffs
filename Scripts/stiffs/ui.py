"""Wspólne zakończenie komendy: zdarzenia po upływie czasu, log, wydruk."""

from . import body, encounter, fight as F
from .core import say

COLORS = {
    "naglowek": "jasny", "sukces": "zielony", "koszt": "zolty",
    "porazka": "czerwony", "katastrofa": "alarm", "alarm": "alarm",
    "zagrozenie": "czerwony", "cialo": "czerwony", "fart": "jasny",
    "info": None, "czas": "szary", "stan": "niebieski", "swit": "jasny",
}


def show(lines):
    for kind, text in lines:
        if text == "":
            say()
        else:
            say(text, COLORS.get(kind))


def flush_log(camp):
    for entry in camp.state.pop("_do_logu", []):
        event = entry.pop("zdarzenie")
        camp.log(event, **entry)


def dawn(camp):
    """Rozlicza dobę, gdy zegar minął świt i nic nie czeka na decyzję."""
    state = camp.state
    if not state.get("czeka_swit") or state.get("starcie")             or state.get("spotkanie") or state.get("czeka_fart"):
        return []
    lines, data = body.settle_dawn(state)
    say()
    show(lines)
    say()
    camp.log("swit", **data, przebieg=[t for _, t in lines])
    return lines


def finish(camp, old_time, show_fight=True):
    """Po każdej komendzie: ciała, spotkania, log, stan starcia, zapis."""
    state = camp.state
    dawn(camp)
    lines = encounter.after(state, old_time)
    show(lines)
    if lines:
        camp.log("po_czasie", przebieg=[t for _, t in lines])
    flush_log(camp)
    if show_fight and state.get("starcie"):
        show(F.status_lines(state))
    elif state.get("spotkanie"):
        say()
        say("Trwa spotkanie. Dalej: encounter.py unik albo walcz.", "jasny")
    camp.save()
