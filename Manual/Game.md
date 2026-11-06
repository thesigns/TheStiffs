# The Stiffs

*O co chodzi w tej grze. Przeczytaj ten plik pierwszy.*

## Czym jest ta gra

**The Stiffs** to solowy system RPG: jeden gracz-człowiek i Claude Code jako Mistrz Gry (MG). Akcja dzieje się w Warszawie w marcu 1990 roku. W nocy z 21 na 22 marca zmarli wstają, na całym świecie naraz, i od tej chwili każdy, kto umrze, wstaje także. Gracz prowadzi jedną postać, zwykłego człowieka, który próbuje przeżyć, i zazwyczaj ma też cel: dotrzeć do bliskich, odnaleźć kogoś, wydostać się z miasta.

To nie jest strzelanka o zombie. To opowieść o przeżywaniu w mieście, w którym kończy się prąd, woda, jedzenie i zaufanie, a zmarli są dawnymi sąsiadami, kolejarzami i dziećmi z podwórka. Polacy nazywają ich **sztywnymi**.

## Jak się gra

Gra toczy się jak rozmowa. MG opisuje, co postać widzi, słyszy i czuje, i pyta: „Co robisz?”. Gracz mówi, co robi postać, własnymi słowami. MG nie decyduje za postać i nie podsuwa jej wyborów.

## Co się liczy w tej grze

**Czas, hałas i zasoby.** Postać to nie specjalista, tylko zwykły człowiek z bloku, który każdą rzecz umie zrobić średnio. O przeżyciu decyduje nie to, ile umie, tylko ile coś trwa, ile robi hałasu i co zużywa. Hałas ściąga sztywnych, a każdy dzień kosztuje wodę, jedzenie i sen.

**Zagrożenia są prawdziwe, nagrody nie są gwarantowane.** Scenariusz nie jest skrojony pod wygodę postaci. Świat jest obojętny: nie sprzyja postaci i nie chce jej zabić.

**Śmierć jest ostateczna.** Postać, która zginie, wstaje jako sztywny. Kampania trwa dalej z nową postacią, a świat, zegary i scenariusz się nie zmieniają.

## Uczciwość Mistrza Gry

Modele językowe mają skłonność do przypodobania się graczowi, a ostrzeżone przed tym zaczynają dokładać arbitralne nieszczęścia. Dlatego **MG nie dosładza i nie dosala**:

- nie naciąga wyników, nie łagodzi skutków, nie ratuje postaci i nie ustępuje pod naciskiem,
- nie przerzuca rzutów i nie cofa wydarzeń (punkt Fartu, którym gracz może poprawić wynik o jeden stopień, nie jest przerzutem),
- nie wymyśla losowych wyników ani nie zmienia stanu gry ręcznie. Robią to skrypty z folderu `Scripts/`.

## Gracz i MG nie wiedzą tego samego

Gracz czyta Manual, więc wie rzeczy, których postać w pierwszych dniach nie ma skąd znać, na przykład że ugryzienie nie zaraża i że każdy, kto umrze, wstaje. Postać i NPC wiedzą tylko to, co mogli zobaczyć i usłyszeć do danej godziny (zob. `Stiffs.md`, *Co wiedzą ludzie*). Pierwszej nocy nikt nie mówi „zarażony” ani „żywe trupy”: ugryzienie to wścieklizna, a zmarły to pijany, chory albo szalony człowiek.

Część gry jest ukryta przed graczem: scenariusz, ziarno losu bliskich i sąsiadów oraz rzuty zapieczętowane (np. zasadzka). Gracz widzi czat i wyniki komend w terminalu. Mógłby zajrzeć do każdego pliku, ale wtedy oszukiwałby samego siebie. Przygotowanie kampanii robi agent w tle, który oddaje tylko informację „gotowe”.

## Jak wygląda kampania

1. **Postać.** Gracz tworzy ją w rozmowie z MG: imię, kim był, tagi, słabość, Rzecz, rozdanie punktów oraz adres i bliscy. Postać ma być ogólnym ocalałym, a nie specjalistą. MG zawsze pyta też o **noc zero**: gdzie postać była i co robiła od wieczora w środę 21 marca do północy. Od tego zależy, gdzie zaczyna się gra (w domu, w szpitalu, w pracy, gdziekolwiek) i w jakim stanie postać wchodzi w tę noc.
2. **Mapa i scenariusz.** MG wymyśla przygodę: fabułę, cele, miejsca, ludzi i zwroty akcji. Zegary zagrożeń tykają niezależnie od gracza. Po starcie kampanii scenariusz jest zamrożony.
3. **Sesje.** Gra toczy się rundami opisanymi wyżej. Pierwsza noc jest najbardziej chaotyczna, bo świat dopiero uczy się, że zmarli wstają. Z każdym dniem wiedza rośnie, a zasoby maleją.
4. **Zapis.** Kampania żyje w folderze `Campaigns/<kampania>/`. Stan zapisują wyłącznie skrypty, a MG prowadzi kronikę (`journal.md`), żeby po przerwie wrócić do gry w tym samym miejscu.

