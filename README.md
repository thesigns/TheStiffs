# The Stiffs

Solowy system RPG o przetrwaniu w polskim mieście. Jeden gracz, a Mistrzem Gry jest [Claude Code](https://claude.com/claude-code).

W nocy z 21 na 22 marca 1990 roku zmarli wstają z grobów. Na całym świecie, w tej samej chwili. Polska dopiero co wychodzi z komunizmu: milicja wciąż chodzi po ulicach, w sklepach są kolejki, a w telewizji nikt jeszcze nie słyszał słowa „zombie”. Ludzie mówią na nich **sztywni**. Ty grasz zwykłym człowiekiem z bloku, który próbuje dożyć do rana.

Docelowo gra opisze kilka polskich miast do wyboru, np. Katowice i Łódź. Na razie gotowa jest Warszawa.

## O czym to jest

To nie jest strzelanka. To gra o tym, jak kończy się świat, który zna się na pamięć: klatka schodowa, sąsiedzi, tramwaj pod blokiem. Zmarli są dawnymi sąsiadami, kolejarzami i dziećmi z podwórka. Pierwszej nocy nikt nie rozumie, co się dzieje, a ugryzienie to dla wszystkich po prostu wścieklizna.

Postać nie jest bohaterem ani specjalistą, tylko „złotą rączką z bloku”, która każdą rzecz umie zrobić średnio. O przeżyciu decyduje nie siła, tylko trzy rzeczy:

- **czas**: co ile trwa i co dzieje się, gdy ktoś jest zbyt wolny,
- **hałas**: każdy dźwięk ściąga sztywnych, każdy strzał ściąga ich więcej,
- **zasoby**: woda, jedzenie, sen, amunicja, opatrunki.

Kampanię wymyśla MG: fabułę, cele, ludzi, miejsca i zwroty akcji. Zwykle chodzi o to, żeby dotrzeć do bliskich po drugiej stronie miasta. Nagrody nie są gwarantowane, a śmierć jest ostateczna: postać, która zginie, sama wstaje jako sztywny.

## Dlaczego tu nie da się oszukać

Modele językowe lubią przytakiwać graczowi. W tej grze to psuje wszystko, więc projekt jest zbudowany wokół jednej zasady: **MG nie ma władzy nad wynikami.**

- Nikt nie rzuca kośćmi. Każdą losowość i każdą zmianę stanu gry (czas, rany, ekwipunek, spotkania) obsługują skrypty w Pythonie.
- MG opisuje świat i opowiada wynik dokładnie taki, jaki podał skrypt. Nie dosładza i nie dosala.
- Prawdę ustalają trzy źródła: Manual (świat i zasady), skrypty i scenariusz, który MG pisze przed startem i potem zamraża.
- Część gry jest przed Tobą ukryta (scenariusz, losy bliskich, zasadzki). Wszystko leży w plikach i mógłbyś zajrzeć, ale wtedy oszukiwałbyś samego siebie.

## Jak się gra

1. Zainstaluj [Claude Code](https://claude.com/claude-code) i Pythona 3. Skrypty nie mają żadnych zależności.
2. Otwórz ten folder w Claude Code. Instrukcje dla MG są w [`AGENTS.md`](AGENTS.md).
3. Powiedz, że chcesz zacząć nową kampanię. MG zapyta o postać: imię, kim była, co umie, czego jej brakuje, kogo ma w mieście. Potem przygotuje scenariusz w tle, tak żebyś go nie zobaczył.
4. Gra toczy się jak rozmowa. MG opisuje, co postać widzi, i pyta: **„Co robisz?”** Odpowiadasz własnymi słowami. Gdy coś jest ryzykowne, skrypt podaje szansę, czas i hałas, losuje wynik, a MG go opowiada.

Zapis kampanii leży w `Campaigns/` i nie trafia do repozytorium. Dzięki kronice MG można przerwać grę i wrócić do niej w tym samym miejscu.

## Co jest w repozytorium

| Folder | Zawartość |
|---|---|
| [`Manual/`](Manual) | Świat i zasady gry |
| [`Scripts/`](Scripts) | Skrypty, które losują i zmieniają stan gry |
| `Campaigns/` | Zapisy kampanii (lokalnie, poza repozytorium) |

Manual najlepiej czytać w tej kolejności:

1. [`Game.md`](Manual/Game.md): o co chodzi w grze,
2. [`World.md`](Manual/World.md): Polska wiosną 1990 roku, fakty historyczne,
3. [`Stiffs.md`](Manual/Stiffs.md): jak działają zmarli i co ludzie o nich wiedzą w kolejnych dniach,
4. [`Rules.md`](Manual/Rules.md): pełna mechanika.

Pierwsze trzy pliki wystarczą, żeby zacząć grać. Ostrzeżenie: `Stiffs.md` zdradza rzeczy, których Twoja postać pierwszej nocy nie może wiedzieć (np. że ugryzienie nie zaraża). To normalne, gracz wie więcej niż postać.

## Stan projektu

Projekt jest we wczesnej fazie. Liczby w zasadach są wstępne i kalibruje je symulator (`Scripts/sim.py`) oraz sesje testowe. Niektóre zasady czekają jeszcze na skrypty i są w `Rules.md` oznaczone jako *(skrypt: do zrobienia)*. W takim wypadku MG gra według tego, co skrypty już umieją.

## Licencja

[MIT](LICENSE), Jakub W. Adamczyk.
