# The Stiffs

> **Projekt w budowie (WIP).** Zasady są obecnie zmieniane i pisane od nowa,
> a podział na pliki w `Manual/` jeszcze się zmienia. Skrypty też się zmienią:
> na razie zatwierdzony jest tylko `coin.py`. Gra w obecnym stanie nie jest
> gotowa do prowadzenia kampanii.

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

- Losowość obsługują skrypty w Pythonie, a nie MG. Docelowo będą też obsługiwać zmiany stanu gry. Na razie gotowy jest tylko `coin.py` (rzut monetą 50/50), który rozstrzyga sporne sprawy.
- MG opisuje świat i opowiada wynik dokładnie taki, jaki podał skrypt. Nie dosładza i nie dosala.
- Prawdę ustalają Manual (świat i zasady) i skrypty. Tego, co jest w tych źródłach, MG nie nagina pod gracza.
- Szczegóły (m.in. co jest ukryte przed graczem, jak powstaje scenariusz) zależą od nowych zasad, które dopiero powstają.

## Jak się gra (docelowo)

Ta sekcja opisuje zamierzony przebieg gry. Nie wszystko z niej działa, dopóki
zasady i skrypty są w przebudowie.

1. Zainstaluj [Claude Code](https://claude.com/claude-code) i Pythona 3. Skrypty nie mają żadnych zależności.
2. Otwórz ten folder w Claude Code. Instrukcje dla MG są w [`AGENTS.md`](AGENTS.md).
3. Powiedz, że chcesz zacząć nową kampanię. MG zapyta o postać (imię i nazwisko, wiek, zawód, a resztę uzupełni i da do akceptacji; zob. [`CharacterCreation.md`](Manual/CharacterCreation.md)). Następnie ustalicie słabości i zalety, które wyznaczają Punkty Determinacji. Dopiero potem powstaje scenariusz.
4. Gra toczy się jak rozmowa. MG opisuje, co postać widzi, i pyta: **„Co robisz?”** Odpowiadasz własnymi słowami. Szczegóły mechaniki ryzyka i testów są w przebudowie.

Zapis kampanii leży w `Campaigns/` i nie trafia do repozytorium.

## Co jest w repozytorium

| Folder | Zawartość |
|---|---|
| [`Manual/`](Manual) | Świat i zasady gry |
| [`Scripts/`](Scripts) | Skrypty (w przebudowie; zatwierdzony tylko `coin.py`) |
| `Campaigns/` | Zapisy kampanii (lokalnie, poza repozytorium) |

Manual najlepiej czytać w tej kolejności:

1. [`Game.md`](Manual/Game.md): o co chodzi w grze,
2. [`World.md`](Manual/World.md): Polska wiosną 1990 roku, fakty historyczne,
3. [`Stiffs.md`](Manual/Stiffs.md): jak działają zmarli i co ludzie o nich wiedzą w kolejnych dniach,
4. [`Rules.md`](Manual/Rules.md): mechanika (w trakcie przepisywania),
5. [`CharacterCreation.md`](Manual/CharacterCreation.md) i
   [`CharacterTemplate.md`](Manual/CharacterTemplate.md): tworzenie postaci.

Stare zasady są w [`RulesOld.md`](Manual/RulesOld.md) i nie obowiązują.
`WIP.md` to roboczy brudnopis autora, nie część zasad.

Ostrzeżenie: `Stiffs.md` zdradza rzeczy, których Twoja postać pierwszej nocy nie może wiedzieć (np. że ugryzienie nie zaraża). To normalne, gracz wie więcej niż postać.

## Stan projektu

Projekt jest w budowie (WIP). Zasady są aktualnie zmieniane, więc opisy w
`Manual/` mogą być niespójne lub niepełne. Skrypty w `Scripts/` będą
przepisywane; na razie jedynym zatwierdzonym jest `coin.py`, a reszta to
pozostałość po starych zasadach.

## Licencja

[MIT](LICENSE), Jakub W. Adamczyk.
