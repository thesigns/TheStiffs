"""Nieświadomi hałasujący: niemowlęta, dzieci i zwierzęta.

Dane i szanse (Rules.md, *Nieświadomi hałasujący*). Sam rzut co jednostkę
czasu robi world._tick, a lista hałasujących leży w state["halasujacy"].
"""

from . import rules
from .core import GameError

KIND_NAMES = {"dziecko": "dziecko", "pies": "pies", "kot": "kot",
              "ptak_cichy": "ptak cichy", "ptak_glosny": "ptak głośny"}

# Zdarzenie, gdy rzut trafia (opis hałasującego wstawiany z przodu).
HIT_TEXT = {"dziecko": "zaczyna płakać", "pies": "szczeka", "kot": "miauczy",
            "ptak_cichy": "gruchnął", "ptak_glosny": "drze się"}


def chance(h, loud=False):
    """Szansa (%) na jednostkę dla hałasującego h."""
    base, _level = rules.NOISY_KINDS[h["rodzaj"]]
    if h["rodzaj"] == "dziecko":
        base = max(0, rules.CHILD_BASE_CHANCE
                   - rules.CHILD_CHANCE_PER_YEAR * h["wiek"])
    return base + (rules.NOISY_LOUD_BONUS if loud and base else 0)


def level(h):
    return rules.NOISY_KINDS[h["rodzaj"]][1]


def validate(kind, age):
    if kind not in rules.NOISY_KINDS:
        raise GameError("Rodzaj: " + ", ".join(rules.NOISY_KINDS) + ".")
    if kind == "dziecko":
        if age is None:
            raise GameError("Dziecko wymaga wieku (--wiek N, w latach).")
        if not 0 <= age <= rules.CHILD_MAX_AGE:
            raise GameError("Od 10 lat dziecko jest zwykłym NPC i nie "
                            "podlega tej tabeli (wiek 0–9).")
    elif age is not None:
        raise GameError("Wiek podaje się tylko dla dziecka.")
