# The Stiffs

*O co chodzi w tej grze. Przeczytaj ten plik pierwszy.*

## Czym jest ta gra

**The Stiffs** to solowy system RPG: jeden gracz-człowiek i Claude Code jako Mistrz Gry (MG). Akcja dzieje się w Warszawie w marcu 1990 roku. W nocy z 21 na 22 marca zmarli wstają, na całym świecie naraz, i od tej chwili każdy, kto umrze, wstaje także. Gracz prowadzi jedną postać, zwykłego człowieka, który próbuje przeżyć, i zazwyczaj ma też cel: dotrzeć do bliskich, odnaleźć kogoś, wydostać się z miasta.

To nie jest strzelanka o zombie. To opowieść o przeżywaniu w mieście, w którym kończy się prąd, woda, jedzenie i zaufanie, a zmarli są dawnymi sąsiadami, kolejarzami i dziećmi z podwórka. Polacy nazywają ich **sztywnymi**.

## Jak się gra

Gra toczy się jak rozmowa. MG opisuje, co postać widzi, słyszy i czuje, i pyta: „Co robisz?”. Gracz mówi, co robi postać, własnymi słowami. MG nie decyduje za postać i nie podsuwa jej wyborów.

Kiedy działanie jest ryzykowne, do gry wchodzi mechanika:

1. MG wybiera z katalogu akcję, a skrypt **wycenia** ją: podaje szansę, czas, hałas i skutek porażki.
2. Skrypt **losuje** wynik. Nikt nie rzuca kośćmi.
3. MG opowiada wynik **dokładnie** taki, jaki podał skrypt. Porażka ma realne skutki.

Wszystko, co zajmuje czas, przechodzi przez skrypt, więc zegar gry, zmęczenie, głód, hałas i spotkania ze sztywnymi liczą się same. Nie ma „docierasz na miejsce” bez komendy.

## Co się liczy w tej grze

**Czas, hałas i zasoby.** Postać to nie specjalista, tylko zwykły człowiek z bloku, który każdą rzecz umie zrobić średnio. O przeżyciu decyduje nie to, ile umie, tylko ile coś trwa, ile robi hałasu i co zużywa. Hałas ściąga sztywnych, a każdy dzień kosztuje wodę, jedzenie i sen.

**Zagrożenia są prawdziwe, nagrody nie są gwarantowane.** Scenariusz nie jest skrojony pod wygodę postaci. Świat jest obojętny: nie sprzyja postaci i nie chce jej zabić.

**Śmierć jest ostateczna.** Postać, która zginie, wstaje jako sztywny. Kampania trwa dalej z nową postacią, a świat, zegary i scenariusz się nie zmieniają.

## Uczciwość Mistrza Gry

Modele językowe mają skłonność do przypodobania się graczowi, a ostrzeżone przed tym zaczynają dokładać arbitralne nieszczęścia. Dlatego **MG nie dosładza i nie dosala**:

- nie naciąga wyników, nie łagodzi skutków, nie ratuje postaci i nie ustępuje pod naciskiem,
- nie przerzuca rzutów i nie cofa wydarzeń (punkt Fartu, którym gracz może poprawić wynik o jeden stopień, nie jest przerzutem),
- nie wymyśla losowych wyników ani nie zmienia stanu gry ręcznie. Robią to skrypty z folderu `Scripts/`.

Prawdę w grze ustalają trzy źródła i nic poza nimi: **Manual** (świat i zasady), **skrypty i tabele** (każda losowość i zmiana stanu) oraz **scenariusz kampanii**, napisany przed startem i potem zamrożony. Jeśli odpowiedzi nie ma w żadnym z nich, rozstrzyga rzut 50/50 (`act.py los`). Przy sprzeczności pierwszeństwo ma Manual, potem scenariusz, potem tabele.

## Gracz i MG nie wiedzą tego samego

Gracz czyta Manual, więc wie rzeczy, których postać w pierwszych dniach nie ma skąd znać, na przykład że ugryzienie nie zaraża i że każdy, kto umrze, wstaje. Postać i NPC wiedzą tylko to, co mogli zobaczyć i usłyszeć do danej godziny (zob. `Stiffs.md`, *Co wiedzą ludzie*). Pierwszej nocy nikt nie mówi „zarażony” ani „żywe trupy”: ugryzienie to wścieklizna, a zmarły to pijany, chory albo szalony człowiek.

Część gry jest ukryta przed graczem: scenariusz, ziarno losu bliskich i sąsiadów oraz rzuty zapieczętowane (np. zasadzka). Gracz widzi czat i wyniki komend w terminalu. Mógłby zajrzeć do każdego pliku, ale wtedy oszukiwałby samego siebie. Przygotowanie kampanii robi agent w tle, który oddaje tylko informację „gotowe”.

## Jak wygląda kampania

1. **Postać.** Gracz tworzy ją w rozmowie z MG: imię, kim był, tagi, słabość, Rzecz, rozdanie punktów oraz adres i bliscy. Postać ma być ogólnym ocalałym, a nie specjalistą.
2. **Mapa i scenariusz.** MG wymyśla przygodę: fabułę, cele, miejsca, ludzi i zwroty akcji. Zegary zagrożeń tykają niezależnie od gracza. Po starcie kampanii scenariusz jest zamrożony.
3. **Sesje.** Gra toczy się rundami opisanymi wyżej. Pierwsza noc jest najbardziej chaotyczna, bo świat dopiero uczy się, że zmarli wstają. Z każdym dniem wiedza rośnie, a zasoby maleją.
4. **Zapis.** Kampania żyje w folderze `Campaigns/<kampania>/`. Stan zapisują wyłącznie skrypty, a MG prowadzi kronikę (`journal.md`), żeby po przerwie wrócić do gry w tym samym miejscu.

## Co jest w Manualu i w jakiej kolejności czytać

1. **`Game.md`** (ten plik): o co chodzi w grze.
2. **`World.md`**: Polska wiosną 1990 roku i fakty historyczne, z których korzysta gra. Do nocy z 21 na 22 marca to historia, potem fikcja.
3. **`Stiffs.md`**: sztywni, czyli jak działają zmarli, co wiedzą ludzie w kolejnych dniach, plotki i zasady prowadzenia sztywnych.
4. **`Rules.md`**: pełna mechanika: czas, wycena i szanse, postać, ciało, nerwy, hałas, walka, pościg, skrypty.

Pierwsze trzy pliki wystarczą, żeby zrozumieć świat i grę. `Rules.md` jest dłuższy i służy do sprawdzania, gdy gracz pyta o konkretną zasadę albo wycena wymaga wyjaśnienia.
