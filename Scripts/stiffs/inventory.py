"""Dodawanie i odejmowanie przedmiotów w stanie gry."""

from .core import GameError, load_json


def add(state, item_id, qty=1, where="przy_sobie"):
    items = load_json("items.json")
    if item_id not in items:
        raise GameError(f"Nieznany przedmiot „{item_id}”.")
    for item in state["ekwipunek"]:
        if item.get("id") == item_id and item.get("gdzie") == where \
                and not item.get("przy_zwlokach") and "zaladowane" not in item:
            item["ilosc"] = item.get("ilosc", 1) + qty
            return item
    spec = items[item_id]
    item = {"id": item_id, "nazwa": spec["nazwa"], "ilosc": qty,
            "daje": list(spec.get("daje", [])), "gdzie": where}
    if spec.get("akcje"):
        item["akcje"] = list(spec["akcje"])
    state["ekwipunek"].append(item)
    return item
