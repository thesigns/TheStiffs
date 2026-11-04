"""Kampania: ścieżki, stan, log, losowość i wyjście na ekran.

Stan gry (state.json) i log (rolls.log) zapisują wyłącznie skrypty
przez ten moduł.
"""

import datetime as _dt
import json
import os
import random
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Scripts" / "data"
CAMPAIGNS = Path(os.environ.get("STIFFS_CAMPAIGNS", ROOT / "Campaigns"))

WIDTH = 80


class GameError(Exception):
    """Błąd zgłaszany użytkownikowi bez śladu stosu."""


# --- wejście/wyjście -------------------------------------------------------

def setup_io():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


_COLORS = {
    "zielony": "32", "zolty": "33", "czerwony": "31", "alarm": "97;41",
    "szary": "90", "jasny": "1", "niebieski": "36",
}


def use_color():
    if os.environ.get("NO_COLOR") or "--no-color" in sys.argv:
        return False
    return sys.stdout.isatty()


def c(text, color):
    if not use_color() or color not in _COLORS:
        return text
    return f"\033[{_COLORS[color]}m{text}\033[0m"


def wrap(text, indent=""):
    return textwrap.fill(text, width=WIDTH, initial_indent=indent,
                         subsequent_indent=indent)


def say(text="", color=None, indent=""):
    """Wypisuje tekst zawinięty do 80 znaków, opcjonalnie w kolorze."""
    if not text:
        print()
        return
    for line in text.split("\n"):
        if not line:
            print()
            continue
        for part in wrap(line, indent).split("\n"):
            print(c(part, color) if color else part)


# --- losowość ----------------------------------------------------------------

_rng = None


def rng():
    """Generator losowy. STIFFS_SEED ustawia ziarno tylko do testów."""
    global _rng
    if _rng is None:
        seed = os.environ.get("STIFFS_SEED")
        _rng = random.Random(seed) if seed else random.SystemRandom()
    return _rng


def d100():
    return rng().randint(1, 100)


# --- kampania ------------------------------------------------------------------

def new_state(name, start):
    return {
        "wersja": 1,
        "kampania": name,
        "rozpoczeta": False,
        "czas": start,
        "pogoda": {"temperatura": 4},
        "postac": None,
        "ekwipunek": [],
        "lokacja": {"wezel": None},
        "wezly": {},
        "towarzysze": [],
        "ustawienia": {"automat": None},
        "liczniki": {"wycena": 0, "log": 0, "rana": 0},
        "wyceny": {},
        "czeka_fart": None,
        "czeka_swit": False,
    }


class Campaign:
    def __init__(self, name):
        self.name = name
        self.path = CAMPAIGNS / name
        self.state_file = self.path / "state.json"
        self.log_file = self.path / "rolls.log"
        if not self.state_file.exists():
            raise GameError(f"Nie ma kampanii „{name}” ({self.path}).")
        with open(self.state_file, encoding="utf-8") as f:
            self.state = json.load(f)

    @staticmethod
    def create(name, start):
        path = CAMPAIGNS / name
        if path.exists():
            raise GameError(f"Kampania „{name}” już istnieje.")
        path.mkdir(parents=True)
        state = new_state(name, start)
        with open(path / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        (path / "rolls.log").write_text("", encoding="utf-8")
        (path / "journal.md").write_text(
            f"# Kronika kampanii „{name}”\n", encoding="utf-8")
        (path / "rulings.md").write_text(
            f"# Precedensy kampanii „{name}”\n", encoding="utf-8")
        camp = Campaign(name)
        camp.log("kampania_utworzona", start=start)
        camp.save()
        return camp

    # Stan zapisujemy atomowo, a poprzednią wersję zostawiamy obok.
    def save(self):
        tmp = self.state_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        if self.state_file.exists():
            os.replace(self.state_file, self.path / "state.prev.json")
        os.replace(tmp, self.state_file)
        from . import render
        (self.path / "state.md").write_text(render.state_md(self.state),
                                            encoding="utf-8")

    def log(self, event, /, **data):
        # Najpierw zdarzenia zgłoszone przez silniki (zachowuje kolejność).
        for entry in self.state.pop("_do_logu", []):
            entry = dict(entry)
            self._write(entry.pop("zdarzenie"), entry)
        self._write(event, data)

    def _write(self, event, data):
        counters = self.state["liczniki"]
        counters["log"] += 1
        entry = {
            "n": counters["log"],
            "real": _dt.datetime.now().isoformat(timespec="seconds"),
            "gra": self.state["czas"],
            "zdarzenie": event,
            **data,
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def next_id(self, counter):
        self.state["liczniki"][counter] += 1
        return self.state["liczniki"][counter]


_json_cache = {}


def load_json(name):
    """Dane z Scripts/data. Wynik jest współdzielony: nie modyfikować."""
    if name not in _json_cache:
        with open(DATA / name, encoding="utf-8") as f:
            _json_cache[name] = json.load(f)
    return _json_cache[name]


def run(main):
    """Uruchamia main() z czytelną obsługą błędów gry."""
    setup_io()
    try:
        main()
    except GameError as e:
        print(c(f"BŁĄD: {e}", "czerwony"), file=sys.stderr)
        sys.exit(1)
