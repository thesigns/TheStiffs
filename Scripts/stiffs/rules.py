"""Stałe i wzory z Manual/Rules.md."""

SKILLS = {
    "walka": "Walka",
    "strzelanie": "Strzelanie",
    "skradanie": "Skradanie",
    "czujnosc": "Czujność",
    "majsterkowanie": "Majsterkowanie",
    "opatrywanie": "Opatrywanie",
    "kombinowanie": "Kombinowanie",
    "przetrwanie": "Przetrwanie",
    "kondycja": "Kondycja",
}

# Akcje zaplanowane, ale jeszcze nieobecne w katalogu. Tagi mogą się do nich
# odwoływać już teraz.
PLANNED_ACTIONS = {
    "atak", "strzal", "bieg", "wyrwanie", "zgubienie", "zamkniecie_drzwi",
    "przeszukanie", "handel", "rozpalenie_ognia", "orientacja",
    "szukanie_jedzenia", "gotowanie_wody", "prowadzenie",
}

# Tworzenie postaci (Rules.md, *Umiejętności*).
SKILL_START = 1
SKILL_POINTS = 7
SKILL_START_MAX = 3
SKILL_MAX = 5
TAGS_MIN, TAGS_MAX = 2, 3
RELATIVES_MIN, RELATIVES_MAX = 1, 2
START_FART = 1

# Umiejętności, w których przeszkadzają nerwy (Rules.md, *Nerwy*).
NERVE_SKILLS = {"strzelanie", "skradanie", "opatrywanie", "kombinowanie"}

APPROACHES = {
    "szybko": {"kroki": -1, "czas": 0.5, "halas": 1, "katastrofa": 0.6},
    "normalnie": {"kroki": 0, "czas": 1.0, "halas": 0, "katastrofa": 0.75},
    "porzadnie": {"kroki": 1, "czas": 2.0, "halas": -1, "katastrofa": 0.75},
}

GRADES = ["katastrofa", "porazka", "koszt", "czysty"]
GRADE_NAMES = {
    "czysty": "CZYSTY SUKCES",
    "koszt": "SUKCES Z KOSZTEM",
    "porazka": "PORAŻKA",
    "katastrofa": "KATASTROFA",
}
GRADE_COLORS = {
    "czysty": "zielony", "koszt": "zolty",
    "porazka": "czerwony", "katastrofa": "alarm",
}

NOISE_POINTS = [0, 1, 2, 4, 8, 16]
SHOT_NEIGHBOR_POINTS = 8
NIGHT_LIGHT_POINTS = 2

ATTITUDES = {"wrogi": -2, "nieufny": -1, "obojetny": 0, "przyjazny": 1}

PLACE_NAMES = {"glowa": "głowa", "tulow": "tułów", "reka": "ręka",
               "noga": "noga"}
SEVERITY_NAMES = {"drasniecie": "draśnięcie", "powazna": "poważna",
                  "krytyczna": "krytyczna"}


def wound_name(w):
    return (f"{PLACE_NAMES.get(w['miejsce'], w['miejsce'])}, "
            f"{SEVERITY_NAMES.get(w['ciezkosc'], w['ciezkosc'])}")


LIGHT_NAMES = {"dzien": "dzień", "polmrok": "półmrok", "ciemnosc": "ciemność"}

MARK_THRESHOLD = 70  # test z szansą ≤ 70% daje znacznik rozwoju

# Krwawienie (minuty bez opatrunku do pogorszenia).
BLEED_LIMIT = {"lekkie": 60, "silne": 20}
DEFAULT_BLEEDING = {"drasniecie": None, "powazna": "lekkie",
                    "krytyczna": "silne"}
CRITICAL_DEATH_CHANCE = 10  # % na jednostkę w stanie krytycznym
WOUND_STEPS = {"powazna": -1, "krytyczna": -2}


def clamp(value, low, high):
    return max(low, min(high, value))


def chance(skill_level, steps):
    return clamp(25 + 10 * skill_level + 10 * steps, 5, 95)


def label(p):
    if p <= 25:
        return "beznadziejne"
    if p <= 45:
        return "ryzykowne"
    if p <= 65:
        return "niepewne"
    if p <= 85:
        return "dobre szanse"
    return "prawie pewne"


def grade(u, p, approach="normalnie"):
    """Stopień wyniku dla rzutu u (1–100) przy szansie p."""
    if p >= 95:
        return "czysty"
    if u <= 0.6 * p:
        return "czysty"
    if u <= p:
        return "koszt"
    factor = APPROACHES[approach]["katastrofa"]
    if u <= p + factor * (100 - p):
        return "porazka"
    return "katastrofa"


def grade_up(g):
    i = GRADES.index(g)
    return GRADES[min(i + 1, len(GRADES) - 1)]


def signed(n):
    return f"+{n}" if n > 0 else ("±0" if n == 0 else f"−{-n}")


# Nieświadomi hałasujący (Rules.md, *Nieświadomi hałasujący*).
# rodzaj: (szansa na jednostkę, poziom hałasu); dziecko liczy się z wieku.
NOISY_KINDS = {
    "dziecko": (None, 3), "pies": (10, 3), "kot": (8, 2),
    "ptak_cichy": (3, 1), "ptak_glosny": (10, 3),
}
CHILD_BASE_CHANCE = 20
CHILD_CHANCE_PER_YEAR = 2
CHILD_MAX_AGE = 9            # od 10 lat dziecko jest zwykłym NPC
NOISY_LOUD_BONUS = 10        # w minionej jednostce w węźle był hałas ≥ 3
NOISY_LOUD_LEVEL = 3
AMBIENT_NOISE_CHANCE = 5
AMBIENT_NOISE_LEVEL = 3
AMBIENT_NODE_TYPES = ("osiedle", "blok", "ulica")
