"""Czytelny widok stanu (state.md). Generowany, nie edytuje się go ręcznie."""

from . import rules, world


def state_md(state):
    t = world.parse(state["czas"])
    lines = [
        f"# Stan kampanii „{state['kampania']}”",
        "",
        "*Plik generowany ze state.json przez skrypty. Nie edytuj ręcznie.*",
        "",
        f"- **Czas:** {world.human(t)} ({rules.LIGHT_NAMES[world.light(state)]})",
    ]
    node = world.current_node(state)
    if node:
        lines.append(f"- **Miejsce:** {node['nazwa']} (uwaga {node.get('uwaga', 0)}"
                     + (f", barykada {node['barykada']}"
                        if node.get("barykada") else "") + ")")
    pog = state.get("pogoda", {})
    if pog.get("niebo"):
        frost = (f", przymrozek do {pog['przymrozek_do'][11:]}"
                 if pog.get("przymrozek_do") else "")
        lines.append(f"- **Pogoda:** {pog['niebo']}, {pog['temperatura']}°C"
                     + frost)
    if state.get("czeka_swit"):
        lines.append("- **Czeka:** rozliczenie doby (następna komenda)")
    char = state.get("postac")
    if char:
        lines += ["", f"## Postać: {char.get('imie', '?')}", ""]
        if char.get("martwy"):
            lines.append(f"**NIE ŻYJE** (zgon: {char.get('zgon')})")
            lines.append("")
        lines.append("| Umiejętność | Poziom | Znaczniki |")
        lines.append("|---|---|---|")
        for sid, name in rules.SKILLS.items():
            marks = char.get("znaczniki", {}).get(sid, 0)
            lines.append(f"| {name} | {char['umiejetnosci'][sid]} | {marks} |")
        lines += [
            "",
            f"- **Zmęczenie:** {char['zmeczenie']}/5  "
            f"**Głód:** {char['glod']}/5  **Nerwy:** {char['nerwy']}/10  "
            f"**Fart:** {char['fart']}/2",
        ]
        if char.get("krytyczny"):
            lines.append("- **STAN KRYTYCZNY**")
        if char.get("choroba") and char["choroba"]["poziom"] > 0:
            lines.append(f"- **Choroba:** {char['choroba']['nazwa']} "
                         f"(poziom {char['choroba']['poziom']})")
        d = char.get("doba")
        if d and not char.get("martwy"):
            lines.append(f"- **Ta doba** (od {d['od'][11:]} {d['od'][8:10]}."
                         f"{d['od'][5:7]}): posiłki {d['posilki']}, woda "
                         f"{d['woda_l'] + d['woda_surowa_l']} l, sen "
                         f"{d['sen_min']} min")
        timed = [m for m in char.get("modyfikatory", []) if m.get("do")
                 and m["do"] > state["czas"]]
        for m in timed:
            lines.append(f"- **{m['zrodlo']}:** {m['kroki']:+d} krok do "
                         f"{m['do'][11:]}")
        if char.get("zawod"):
            lines.append(f"- **Kim jest:** {char.get('wiek', '?')} lat, "
                         f"{char['zawod']}")
        if char.get("tagi"):
            lines.append("- **Tagi:** " + ", ".join(t["nazwa"] for t in char["tagi"]))
        if char.get("slabosc"):
            lines.append(f"- **Słabość:** {char['slabosc']['nazwa']}")
        if char.get("bliscy"):
            lines.append("- **Bliscy:** " + "; ".join(
                f"{b['imie']} ({b['relacja']})" for b in char["bliscy"]))
        if char["rany"]:
            lines += ["", "### Rany", ""]
            for w in char["rany"]:
                bits = [rules.wound_name(w)]
                if w.get("krwawienie"):
                    bits.append(f"krwawienie {w['krwawienie']}")
                if w.get("opatrzona"):
                    bits.append("opatrzona")
                if w.get("zakazenie"):
                    bits.append(f"zakażenie {w['zakazenie']}")
                if w.get("ugryzienie"):
                    bits.append("ugryzienie")
                lines.append(f"- #{w['id']}: " + ", ".join(bits))
    if state["ekwipunek"]:
        lines += ["", "## Ekwipunek"]
        groups = {}
        for item in state["ekwipunek"]:
            groups.setdefault(item.get("gdzie", "przy_sobie"), []).append(item)
        order = sorted(groups, key=lambda g: (g != "przy_sobie", str(g)))
        for where in order:
            if where == "przy_sobie":
                title = "Przy sobie"
            else:
                title = "W: " + state["wezly"].get(where, {}).get("nazwa", str(where))
            lines += ["", f"### {title}", ""]
            for item in groups[where]:
                qty = item.get("ilosc", 1)
                extra = (f" (przy zwłokach: {item['przy_zwlokach']})"
                         if item.get("przy_zwlokach") else "")
                if "napoczete" in item:
                    extra += f" (napoczęte: zostało {item['napoczete']})"
                lines.append(f"- {item['nazwa']}"
                             + (f" × {qty}" if qty != 1 else "") + extra)
    if state.get("halasujacy"):
        lines += ["", "## Hałasujący (zwierzęta, dzieci)", ""]
        for h in state["halasujacy"]:
            where = ("z postacią" if h.get("wezel") is None else
                     "w: " + state["wezly"].get(h["wezel"], {}).get("nazwa",
                                                                      h["wezel"]))
            lines.append(f"- #{h['id']} {h['opis']} ({h['rodzaj']}"
                         + (f", {h['wiek']} lat" if "wiek" in h else "")
                         + f"), {where}")
        if state.get("ukrycie"):
            lines.append("- Postać się ukrywa.")
    open_q = [(k, q) for k, q in state["wyceny"].items()
              if q["status"] in ("otwarta", "czeka_na_fart")]
    if open_q:
        lines += ["", "## Otwarte wyceny", ""]
        for k, q in open_q:
            lines.append(f"- [#{k}] {q['nazwa']}: {q['szansa']}% ({q['status']})")
    return "\n".join(lines) + "\n"
