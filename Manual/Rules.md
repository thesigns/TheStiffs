# Zasady gry

*Mechanika gry dla gracza i Mistrza Gry. Rozgrywka solo: jeden gracz-człowiek, Claude Code jako MG.*

Wszystkie liczby w tym dokumencie są wstępne. Skalibrują je symulacje (`sim.py`) i sesje testowe.

## Założenia

**Zwykły człowiek z bloku.** PRL wychowywał ludzi wszechstronnych z konieczności. Każdy sam naprawiał malucha, kombinował towar spod lady, przeszedł przysposobienie obronne w szkole i zasadniczą służbę w wojsku, uprawiał działkę. Postać gracza nie jest specjalistą, tylko „złotą rączką z bloku”, która każdą rzecz umie zrobić średnio. Brak specjalisty nadrabia się **czasem, narzędziami i przygotowaniem**, a nie kolegą innej profesji.

**Trzy waluty: czas, hałas, zasoby.** Statystyki mają mniejsze znaczenie niż to, ile coś trwa, ile robi hałasu i co zużywa.

**Gra we dwoje.** Postać nie potrzebuje drużyny. Każdy problem ma kilka dróg: siłą, sprytem, ciszą, czasem, narzędziem albo handlem. Trudność bierze się ze świata (hałasu, czasu, rozkładu, ran, braku zasobów), a nie z braku profesji. Towarzysze NPC są dozwoleni (zob. *Towarzysze*), ale nigdy nie są warunkiem przetrwania.

**Wszystko rozstrzygają skrypty.** Nikt nie rzuca kośćmi. Każdą losowość i każdą zmianę stanu gry obsługują skrypty z folderu `Scripts/`, więc mechanika może być bardziej złożona, niż pozwalałyby tradycyjne kości.

## Słowniczek

| Termin | Znaczenie | W `Stiffs.md` |
|---|---|---|
| sztywny, sztywni | ożywiony zmarły | stiff |
| świeżak | sztywny w etapie świeżym | fresh |
| gnilec | sztywny w etapie rozkładu | rotting |
| padły | sztywny, któremu zgnił mózg; zwykłe zwłoki | fallen |
| pochód | rosnący tłum sztywnych idący za dźwiękiem | stream |
| wymiana | jednostka czasu walki i pościgu, kilka sekund | – |
| jednostka | jednostka czasu działań, 10 minut | – |
| krok | modyfikator szansy, ±10 punktów procentowych | – |
| wycena | szansa i stawka testu wyliczone przez skrypt przed rzutem | – |
| węzeł | miejsce na mapie kampanii | – |
| uwaga | licznik tego, jak bardzo węzeł ściąga sztywnych | – |

## Źródła prawdy

Gra opiera się na trzech źródłach prawdy:

1. **Manual** (`Manual/`): świat i zasady.
2. **Skrypty i tabele** (`Scripts/`): każda losowość i każda zmiana stanu.
3. **Scenariusz kampanii** (`Campaigns/<nazwa>/scenario.md`): fabuła, lokacje, NPC i sekrety, przygotowane przed startem kampanii.

Kolejność pierwszeństwa przy sprzecznościach: **Manual > scenariusz > tabele.**

- Scenariusz nie może łamać zasad świata. Nie wolno na przykład wprowadzić w nim mówiącego sztywnego.
- Konkretna zawartość wpisana w scenariuszu ma pierwszeństwo przed tabelą.
- Tabela działa tam, gdzie scenariusz do niej odsyła (np. „skarb w magazynie: skrypt łupu”) albo milczy.
- **Skrypt sprzeczny z manualem to błąd skryptu.** Poprawia się skrypt, a nie narrację. Wynik, który już zapadł, zostaje.

## Uczciwość Mistrza Gry

AI ma skłonność do przypodobania się użytkownikowi. Ma też odwrotną skłonność: ostrzeżone przed słodzeniem, zaczyna dokładać arbitralne nieszczęścia. **MG nie dosładza i nie dosala.** Świat jest obojętny: nie sprzyja postaci i nie chce jej zabić.

### Zasady

- **MG nigdy nie wymyśla wyniku losowego** ani nie zmienia stanu gry ręcznie. Robią to skrypty.
- **MG nie decyduje, czy rzucać.** Obowiązkowe wyzwalacze testu (zob. *Kiedy test*) muszą skończyć się testem. W razie wątpliwości jest test. Gracz może zażądać testu w każdej chwili.
- **MG nie dobiera modyfikatorów.** Szansę liczy skrypt ze stanu gry. MG wybiera tylko akcję z katalogu, podejście i najwyżej jedną okoliczność ±1 krok z uzasadnieniem (zob. *Wycena*).
- **Jedna wycena, jeden rzut.** Nie wolno wycenić akcji, zobaczyć szansy, a potem wycenić jej inaczej. Każdy wynik w narracji cytuje numer wyceny, np. `[#41]`.
- **Czas zawsze płynie przez skrypt.** Nie ma „docierasz do apteki”. Każda czynność zajmująca czas przechodzi przez skrypt, także bez testu, więc zegar, uwaga, zmęczenie i spotkania liczą się same.
- **Interpretacja wyniku jest ograniczona.** Rodzaj kosztu i treść katastrofy losuje skrypt z katalogu akcji. MG ubiera je w słowa, ale nie wybiera.
- **Bez przerzutów i bez cofania wydarzeń.** Jedyny wyjątek to błąd w stosowaniu zasad, a nie niekorzystny wynik. Fart nie jest przerzutem (zob. *Fart*).
- **Konsekwencje wynikają z fikcji i z rzutów**, nigdy z tego, że graczowi będzie przykro, ani z tego, że „gra robi się za łatwa”.
- **MG nie ustępuje pod naciskiem.** Kiedy gracz się targuje, MG odpowiada uprzejmie, ale zostaje przy swoim. Spór o brzmienie zasad rozstrzyga *Precedens*, nie MG.
- **Świat żyje własnym rytmem.** NPC mają własne cele zapisane w scenariuszu, zegary zagrożeń tykają, hałas zawsze coś ściąga.
- **Śmierć postaci jest możliwa i ostateczna.** Postać, która zginie, wstaje jako sztywny.

### Rzuty zapieczętowane

Niektóre rzuty dotyczą rzeczy, których postać nie wie: czy w ciemności czeka zasadzka, kim naprawdę jest postać w półmroku, czy NPC kłamie. Skrypt zapisuje je w logu jako **zapieczętowane** i nie pokazuje wyniku w wycenie. MG narruje tylko to, co postać widzi. Pieczęć zdejmuje się, gdy prawda wyjdzie na jaw.

### Pytania o świat

Gdy odpowiedzi nie ma w żadnym źródle prawdy, rozstrzyga ją `act.py los "<pytanie>"`: 50/50 albo z szansą zapisaną w scenariuszu. Gdy odpowiedź jest tajemnicą (np. czy ktoś za zamkniętymi drzwiami żyje), rzut jest zapieczętowany: wynik trafia tylko do logu, a MG czyta go narzędziem Read *(skrypt: do zrobienia)*.

### Precedens

- Gdy zasada jest niejasna i gracz z MG się nie zgadzają, skrypt rozstrzyga 50/50. MG nie wybiera korzystnej dla siebie ani dla gracza interpretacji.
- Każde rozstrzygnięcie trafia do `rulings.md` kampanii i jest odtąd wiążące.

### Ciągłość

W długiej sesji Claude Code kompaktuje kontekst i MG może zapomnieć zasady. Dlatego na początku każdej sesji i po każdym kompaktowaniu MG uruchamia `resume.py`. Skrypt drukuje:
- stan gry,
- ostatnie wpisy z dziennika,
- listę kontrolną uczciwości.

## Pliki kampanii

```
Campaigns/<nazwa>/
  scenario.md   – scenariusz, przygotowany przed startem, potem zamrożony
  addenda.md    – dopiski do scenariusza po starcie, tylko przez skrypt
  state.json    – stan gry, zapisywany wyłącznie przez skrypty
  state.md      – czytelny widok stanu, generowany ze state.json
  journal.md    – kronika wydarzeń, tylko dopisywana
  rolls.log     – log skryptów, tylko dopisywany
  rulings.md    – precedensy
```

- **`scenario.md`**: zob. *Scenariusz*. Po starcie nie zmienia się.
- **`addenda.md`**: dopiski, gdy gracz wyjdzie poza przygotowany materiał. Dopisuje je skrypt `addendum.py`, **zanim** postać wejdzie w dane miejsce, i odnotowuje to w logu. Dopiski mogą zawierać wyłącznie kolor i osobowości: wygląd miejsca, charakter NPC, historię. Mechanicznie istotną zawartość (typ miejsca, łup, zagrożenia, wyjścia) losuje skrypt.
- **`state.json`**: jedyne źródło stanu. Postać, ekwipunek, czas, pogoda, kryjówka, węzły mapy, pochody, zegary. Ekwipunek zmienia tylko skrypt (`inv.py`), zawsze z podanym powodem.
- **`state.md`**: skrypty generują go przy każdym zapisie stanu. Nie edytuje się go ręcznie.
- **`journal.md`**: kronika pisana przez MG. Wpisy tylko się dopisuje.
- **`rolls.log`**: każde wywołanie skryptu: znacznik czasu, numer wyceny, akcja, modyfikatory, stawka, wynik. Gracz może w każdej chwili sprawdzić, czy narracja zgadza się z rzutami.

Co MG może edytować w każdym z tych plików, określa `AGENTS.md`.

Gracz może czytać wszystkie pliki, w tym scenariusz. Nie robi tego, bo oszukiwałby sam siebie.

## Scenariusz

Scenariusz to przygoda RPG wymyślona przez MG. Poniższe zasady nie ograniczają jego pomysłów. Mają tylko sprawić, że przygoda nie będzie po cichu skrojona pod wygodę gracza.

### Ziarno scenariusza

Przed napisaniem scenariusza MG uruchamia `scenario_seed.py`. Skrypt losuje kilka parametrów, których MG nie wybiera, ale wplata je w przygodę:
- **3 zegary zagrożeń** z puli archetypów (np. „Jednostka na Bemowie się wycofuje”, „Banda ze Stadionu przejmuje Pragę”, „Woda w Filtrach staje się zatruta”),
- **2 wrogie frakcje albo NPC,**
- **poziom niedoboru** w okolicy,
- **los bliskich postaci** (żyją, nie żyją, nieznane), jako wynik zapieczętowany.

MG rozpisuje te parametry fabularnie.

### Obowiązkowe sekcje scenariusza

- **Zarys:** punkt wyjścia, główny wątek, cele i najważniejsze zwroty akcji.
- **Zegary zagrożeń:** każdy ma 4–8 segmentów, opis tego, co się dzieje przy kolejnych segmentach, i skutek pełnego zegara. Zegary tykają co dzień według rzutu skryptu, niezależnie od gracza. Działania postaci mogą je cofać albo przyspieszać.
- **NPC z agendą:** co chcą, czego się boją, co zrobią, jeśli postać się nie pojawi. Co najmniej jeden aktywnie wrogi i co najmniej jeden niepewny.
- **Mapa węzłów:** zob. *Mapa*.
- **Klatka schodowa postaci:** 4–6 sąsiadów z imienia, zawodu i jednego szczegółu. Każdy z nich może się pojawić jako żywy albo jako sztywny.
- **Lokacje kluczowe:** z konkretną zawartością albo z odesłaniem do tabel.
- **Oś czasu:** zdarzenia z godziną, które dzieją się bez względu na postać. Te, które mogą dotyczyć postaci (pukanie do drzwi, strzał pod oknem), MG rejestruje w stanie gry przed startem. Sen i czynności rutynowe zatrzymują się na nich same *(skrypt: do zrobienia)*.
- **Wiedza NPC:** kwestie i decyzje NPC zgodne z porą od pierwszej nocy (`Stiffs.md`, *Co wiedzą ludzie*).

## Czas

Gra ma trzy skale czasu:

| Skala | Długość | Do czego |
|---|---|---|
| wymiana | kilka sekund | walka, pościg |
| jednostka | 10 minut | działania, przeszukiwanie, podróż |
| dzień | od świtu do świtu | rozliczenie snu, głodu, zakażeń, zegarów |

Zegar kampanii prowadzi też porę dnia, światło i pogodę, w tym przymrozki o świcie do połowy kwietnia. Zimno nie spowalnia sztywnych, tylko ich rozkład; dokucza żywym (zob. `Stiffs.md`, *Zimno*).

## Przebieg gry

Gra nie ma narzuconej pętli. **Kampania to tradycyjna przygoda RPG**, którą wymyśla MG: fabuła, cele, miejsca, postacie i zwroty akcji. Grę napędza scenariusz, a nie stały rytm dnia.

Mechanika przetrwania tworzy tło i presję, a nie fabułę:
- głód, woda, rany i zmęczenie zmuszają postać do decyzji po drodze,
- bliscy postaci dają jej osobiste motywacje,
- zegary zagrożeń sprawiają, że świat zmienia się, także gdy postać zwleka.

### Rozliczenie doby

Doba trwa od wschodu do wschodu słońca. Gdy zegar przekroczy wschód, pierwsza komenda, po której nie trwa starcie, spotkanie ani decyzja o Farcie, sama rozlicza minioną dobę (`stiffs/body.py`; podgląd: `dawn.py stan`). MG niczego tu nie wywołuje ani nie pomija. Rozliczenie obejmuje:
- **pogodę:** temperaturę, niebo i przymrozek (do 15 kwietnia, 35% szans; trwa do 9:00),
- **sen:** czy minionej doby postać spała,
- **jedzenie i wodę,**
- **zakażenia ran, gojenie i choroby,**
- **stan krytyczny z sepsy, choroby albo pragnienia:** rzut na śmierć raz na dobę, 15%,
- **Fart:** w niedzielę +1, najwyżej 2.

Doba krótsza niż 12 godzin (początek kampanii, nowa postać) nie daje kar za sen, jedzenie i wodę.

Przymrozek nie zmienia zachowania sztywnych. Noc spędzona na dworze w przymrozek, bez ciepłego ubrania i ognia, daje postaci +1 zmęczenia *(skrypt: do zrobienia)*.

**Jeszcze bez skryptu:** zdarzenia przy kryjówce, ruch pochodów, zegary zagrożeń. Do czasu ich powstania MG ich nie rozgrywa.

### Sen

Sen to komenda `act.py spij --godziny N` albo `--do HH:MM`. Czas płynie co 10 minut, a w niepewnym miejscu spotkania losują się jak zwykle. Śpiąca postać ma −3 kroki do testu, kto zauważył pierwszy. Spotkanie przerywa sen.

Sen zatrzymuje się też na zdarzeniach z osi czasu scenariusza, które mogą obudzić postać. Wtedy `act.py los` rozstrzyga, czy postać się budzi.

Bezpieczne miejsce to kryjówka albo węzeł o gęstości 0 (zamknięte mieszkanie). Inne miejsca są niepewne.

| Sen | Skutek |
|---|---|
| co najmniej 6 h, bezpieczne miejsce | zmęczenie 0, nerwy −2, rozwój umiejętności |
| co najmniej 6 h, niepewne miejsce | zmęczenie −2 |
| 3–6 h | zmęczenie −1 |
| poniżej 3 h | nic |

Jeśli w dobie postać spała łącznie mniej niż 3 godziny, o świcie dostaje **noc bez snu**: zmęczenie +2 i nerwy +1. Czas snu nie liczy się do zmęczenia od aktywności.

### Koniec sesji

Sesja może się skończyć w dowolnym miejscu, bo skrypty zapisują stan na bieżąco. Na koniec MG dopisuje wpis w `journal.md`, żeby dało się podjąć grę w tym samym miejscu.

## Kryjówka

Postać nie musi mieć kryjówki, ale jeśli ją ma, jest to miejsce, które gracz chce chronić, a więc stawka. Gracz wyznacza ją komendą `encounter.py kryjowka on` w bieżącym węźle. Kryjówka ma w `state.json` własny stan:
- **zapasy,**
- **barykada:** siła 0–10 (zob. *Barykady*),
- **widoczność światła:** 0–2, czyli jak bardzo światło z kryjówki widać nocą,
- **wyjścia:** ile i jakie,
- **hałas tła:** stały poziom hałasu kryjówki, np. przez towarzyszy, piecyk albo generator.

## Mapa

Kampania ma mapę Warszawy z 30–60 węzłów. Każdy węzeł ma:
- **typ:** osiedle, szpital, stadion, zajezdnia, most itd.,
- **gęstość sztywnych:** bazowa szansa spotkania na jednostkę (0 = zamknięte miejsce bez losowych spotkań),
- **źródło sztywnych:** od niego zależy etap (zob. *Etap sztywnych*),
- **stopień splądrowania,**
- **uwagę:** zob. *Hałas i uwaga*,
- **sąsiadów** z czasem przejścia w jednostkach.

**Przejście.** Jawne przejście do sąsiedniego węzła to czynność bez testu: zajmuje czas z mapy, robi hałas 1, a spotkania losują się normalnie po drodze i na miejscu. Test Skradania (`act.py wycen przejscie`) jest tylko wtedy, gdy postać chce przejść niezauważona albo przechodzi obok widocznego zagrożenia. *(skrypt: do zrobienia)*: do czasu poprawki każde przejście idzie przez `act.py wycen przejscie`.

**Mosty** to osobne węzły o wysokim ryzyku. Przez Wisłę jest tylko pięć mostów drogowych (zob. `World.md`), więc są wąskim gardłem.

## Rozstrzyganie akcji

### Kiedy test

Test jest **obowiązkowy**, gdy:
- postać działa ze sztywnym na wyciągnięcie ręki albo jest uchwycona,
- akcja robi hałas 2 lub więcej w węźle z uwagą powyżej 0,
- postać przeszukuje miejsce,
- postać pierwszy raz prosi NPC o coś, na czym mu zależy,
- postać się wspina albo skacze,
- postać otwiera coś zamkniętego,
- postać przechodzi między węzłami mapy ukradkiem albo przez miejsce, w którym widzi zagrożenie (zob. *Mapa*, *Przejście*),
- postać działa w pościgu.

Poza tym obowiązuje zasada: **w razie wątpliwości jest test.**

Czynności rutynowe bez ryzyka (jedzenie, rozmowa, marsz po kryjówce) też przechodzą przez skrypt jako `act.py <kampania> rutyna`: bez rzutu, ale z kosztem czasu i hałasu.

### Wycena

1. MG wybiera **akcję z katalogu** (`Scripts/data/actions.json`). Każda akcja w katalogu ma:
   - umiejętność,
   - czas i hałas bazowy,
   - wymagane i pomocne narzędzia,
   - domyślny skutek porażki,
   - tabelę kosztów i tabelę katastrof.
2. MG wybiera **podejście:** szybko, normalnie albo porządnie.
3. MG może dodać **najwyżej jedną okoliczność sytuacyjną** ±1 krok, z uzasadnieniem zapisanym w logu.
4. Skrypt liczy szansę ze stanu gry i wypisuje **wycenę z numerem**. Wycena podaje też **szansę spotkania na 10 minut** w bieżącym węźle, bo czas akcji to ryzyko *(skrypt: do zrobienia)*. Przykład:

   `[#41] Wyważenie drzwi (Majsterkowanie): 55% (niepewne). Czas: 1 j. Hałas: 4. Porażka: drzwi stoją, hałas 4.`
5. Gracz potwierdza albo rezygnuje. Rezygnacja jest odnotowana w logu, a ta sama akcja nie może być wyceniona ponownie w tej samej sytuacji.
6. Skrypt rzuca. Narracja cytuje `[#41]`.

**Automat.** Gracz może ustawić próg, np. 80%. Wyceny z szansą równą lub wyższą rzucają się bez pytania o potwierdzenie, żeby nie spowalniać gry.

### Szansa

**Szansa = 25% + 10% × umiejętność + 10% × suma kroków**, w granicach 5–95%.

Przy szansie 95% nie ma rzutu, ale koszty czasu i hałasu i tak się liczą.

**Kroki** (skrypt liczy je ze stanu, MG ich nie wybiera):

| Źródło | Kroki |
|---|---|
| podejście: szybko / porządnie | −1 / +1 |
| właściwe narzędzie | +1 |
| brak wymaganego narzędzia | −1 albo −2 (wg katalogu) |
| tag życiorysu pasujący do akcji | +1 (łącznie z tagów najwyżej +1) |
| książka lub instrukcja pasująca do akcji | +1 |
| pomoc towarzysza | +1 |
| poważna / krytyczna rana w pasującej części ciała | −1 / −2 |
| zmęczenie lub głód powyżej 2 (akcje fizyczne) | −1 za każdy poziom |
| nerwy 5–7 / 8+ (akcje precyzyjne) | −1 / −2 |
| półmrok / ciemność (akcje wzrokowe) | −1 / −2 |
| okoliczność MG (najwyżej jedna, z uzasadnieniem) | ±1 |

**Podejście zmienia też koszty:**
- **Szybko:** połowa czasu, hałas +1, więcej katastrof.
- **Porządnie:** podwójny czas, hałas −1 (najmniej 0).

**Gracz zna szansę przed rzutem.** Wycena pokazuje procent zaokrąglony do 5 i etykietę:

| Szansa | Etykieta |
|---|---|
| 5–25% | beznadziejne |
| 30–45% | ryzykowne |
| 50–65% | niepewne |
| 70–85% | dobre szanse |
| 90–95% | prawie pewne |

### Stopnie wyniku

Skrypt losuje liczbę 1–100 (*u*) i porównuje ją z szansą (*p*):

| Wynik | Stopień |
|---|---|
| u ≤ 0,6 × p | **czysty sukces:** postać osiąga cel |
| 0,6 × p < u ≤ p | **sukces z kosztem:** cel osiągnięty, koszt losowany z katalogu akcji (czas, hałas albo zużycie) |
| p < u ≤ p + 0,75 × (100 − p) | **porażka:** zapowiedziany w wycenie skutek porażki |
| powyżej | **katastrofa:** porażka plus wynik losowany z tabeli katastrof akcji |

Przy podejściu „szybko” współczynnik 0,75 spada do 0,6, więc katastrof jest więcej.

Przykład dla p = 55%: czysty sukces 1–33, sukces z kosztem 34–55, porażka 56–88, katastrofa 89–100.

### Fart

- Fart **przesuwa wynik o jeden stopień w górę**: katastrofa staje się porażką, porażka sukcesem z kosztem, sukces z kosztem czystym sukcesem.
- Gracz decyduje o użyciu po zobaczeniu wyniku. Tylko gracz, nigdy MG.
- Działa tylko na testy postaci. Nie działa na rzuty świata: powstawanie zmarłych, spotkania, zakażenia, zegary.
- Postać zaczyna z 1 punktem Fartu. Dostaje +1 w każdą niedzielę czasu gry, najwyżej 2.

## Postać

### Umiejętności

Postać ma dziewięć umiejętności w skali 1–5:

- **Walka:** wręcz i bronią białą.
- **Strzelanie.**
- **Skradanie.**
- **Czujność:** zmysły, intuicja, zauważanie.
- **Majsterkowanie:** naprawy, włamy, barykady, samochody.
- **Opatrywanie:** pierwsza pomoc na poziomie przysposobienia obronnego.
- **Kombinowanie:** handel, gadanie, załatwianie spraw.
- **Przetrwanie:** orientacja, jedzenie, woda, ogień.
- **Kondycja:** bieg, wspinaczka, dźwiganie, siła, odporność.

**Tworzenie postaci:**
- wszystkie umiejętności zaczynają na 1,
- gracz rozdziela 7 punktów,
- na starcie żadna umiejętność nie przekracza 3,
- w trakcie kampanii sufit to 5.

### Życiorys

Postać ma 2–3 **tagi życiorysu**. Katalog tagów jest w `Scripts/data/tags.json`, m.in.: *zasadnicza służba*, *tramwajarz*, *pielęgniarka*, *badylarz z działki*, *cinkciarz*, *harcerz*, *ministrant*, *hydraulik ze spółdzielni*, *kierowca*, *myśliwy*, *milicjant*, *ekspedientka*. Gracz może też zaproponować własny tag; wtedy musi on spełniać te same warunki co tagi z katalogu.

Każdy tag ma:
- **listę 3–5 akcji lub miejsc**, w których daje +1 krok,
- **1–2 dostępy fabularne:** tramwajarz zna zajezdnię, cinkciarz zna ludzi ze Stadionu,
- **listę rzeczy**, spośród których gracz wybiera Rzecz postaci,
- opcjonalnie **dodatkowe przedmioty** losowane do mieszkania.

Lista akcji zostaje zapisana w `state.json` i zamrożona. MG nie decyduje w trakcie gry, czy tag „pasuje”.

### Kim jest postać

Oprócz liczb każda postać ma:
- **Adres:** osiedle, blok i klatkę. To miejsce startu, wiedza o okolicy i sąsiedzi wpisani do scenariusza.
- **Bliskich:** 1–2 osoby, które postać chce odnaleźć albo ochronić, na przykład żonę na nocnej zmianie w Szpitalu Bródnowskim albo matkę na Pradze za rzeką. Ich los losuje ziarno scenariusza.
- **Słabość:** jedna z katalogu `Scripts/data/weaknesses.json` (krótkowzroczność, astma, wiek, chore kolano, niedosłuch, nałóg nikotynowy lub alkoholowy, lęk przed ciemnością). Ma skutek mechaniczny w określonych sytuacjach, np. bez okularów −2 kroki do Czujności i Strzelania.
- **Rzecz:** jeden przedmiot związany z życiorysem, wybrany z listy rzeczy jednego z tagów postaci, np. drąg do zwrotnic tramwajarza, dwururka myśliwego, maluch kierowcy.

### Ekwipunek

Reszta **ekwipunku startowego** to to, co postać ma przy sobie i w mieszkaniu. Losuje to skrypt raz, przy tworzeniu postaci, z tabel w `Scripts/data/household.json` i z dodatkowych przedmiotów tagów. Postaci nie tworzy się od nowa, żeby przelosować ekwipunek.

Każdy przedmiot ma miejsce: **przy sobie** albo **w węźle mapy** (np. w mieszkaniu, w kryjówce, przy zwłokach). Postać może korzystać tylko z przedmiotów przy sobie i z tych, które leżą w węźle, w którym właśnie jest.

Każda zmiana ekwipunku idzie przez skrypt:
- łup z przeszukania dodaje `act.py` (tabele),
- branie i odkładanie rzeczy: `inv.py wez` / `odloz`,
- **zysk** spoza tabel (`inv.py zysk --powod`) tylko wtedy, gdy przedmiot stoi w scenariuszu (np. opisana zawartość lokacji) albo wynika z rzutu; nigdy dlatego, że przydałby się postaci,
- **strata** (`inv.py strata --powod`) wtedy, gdy wynika z rzutu albo z decyzji gracza,
- **wymiana** z NPC (`inv.py wymien`) po teście Kombinowania; jego numer podaje się w `--wycena`.

Przedmioty zużywane porcjami (papierosy, alkohol, środki odkażające, cukier, zapałki) mają licznik napoczętej sztuki.

### Tworzenie postaci krok po kroku

1. MG zakłada węzeł mapy z mieszkaniem postaci (`campaign.py wezel`).
2. Gracz poznaje możliwości: `character.py opcje`.
3. MG pyta gracza o postać i wpisuje odpowiedzi do karty `Campaigns/<kampania>/postac.json` (pusta karta: `character.py szablon`). Gracz może też wypełnić kartę sam.
4. `character.py sprawdz` pokazuje błędy albo podsumowanie.
5. `character.py utworz` losuje ekwipunek i zapisuje postać do stanu gry. Karta zostaje przeniesiona do `postac.<numer>.json`.

Po śmierci postaci tworzy się następną tak samo. Rzeczy zmarłego zostają przy jego zwłokach.

### Rozwój

Nie ma punktów doświadczenia. Postać uczy się przez używanie:
- skrypt stawia **znacznik** umiejętności po każdym teście z szansą 70% lub niższą, niezależnie od wyniku (porażka też uczy),
- przy śnie w kryjówce: jeśli umiejętność ma znaczników co najmniej 3 × aktualny poziom, rośnie o 1, a jej znaczniki się zerują.

**Tagi zdobyte.** Gra może dać postaci nowy tag z tabeli wyzwalaczy, na przykład za przeżycie pochodu, zabicie dziesięciu świeżaków albo pochowanie bliskiego. Każdy zdobyty tag ma jedną zaletę i jeden koszt. Przykład: *przeżył pochód*: +1 krok do Kondycji przy ucieczce przed tłumem, ale +1 nerwów przy dźwięku dużej grupy.

### Wiedza jako przedmiot

Książki i instrukcje to ważny łup. Przykłady:
- „Poradnik pierwszej pomocy”,
- „Samochód Fiat 126p. Naprawa”,
- mapa sztabowa.

Zasady:
- Książka daje +1 krok do akcji wymienionych w jej opisie, jeśli postać ma ją przy sobie i poświęci jednostkę na zajrzenie do niej.
- **Przestudiowanie** w kryjówce (2 godziny, raz na książkę) daje 3 znaczniki rozwoju w pasującej umiejętności.
- Książka ma wagę i zajmuje miejsce w plecaku, więc konkuruje z jedzeniem.

### Wiedza gracza a wiedza postaci

Gracz czyta `Stiffs.md` i wie rzeczy, których postać w pierwszych dniach wiedzieć nie może, na przykład że ugryzienie nie zaraża.
- Postać może działać według wiedzy gracza.
- NPC działają według swoich przekonań z sekcji *Co wiedzą ludzie* w `Stiffs.md`, zgodnie z porą od pierwszej nocy. Pierwszej nocy nikt nie mówi o zarażaniu ani o żywych trupach: ugryzienie to dla ludzi szaleniec albo wścieklizna.
- Ugryziona postać dostaje widoczny znacznik *ugryziony*. Do czasu, aż przekonanie o zarażaniu minie, NPC reagują na niego strachem: odmawiają handlu, przeganiają, czasem atakują.

## Ciało

### Zmęczenie i głód

Dwa tory w skali 0–5. Każdy poziom powyżej 2 daje −1 krok do akcji fizycznych. Na poziomie 5 postać nie może biec ani walczyć skutecznie.

**Zmęczenie** rośnie:
- +1 za każdą wymianę biegu w pościgu,
- +1 za każde 6 godzin aktywności,
- +2 za noc bez snu.

**Zmęczenie** spada przy śnie (zob. *Sen*).

**Głód:**
- +1 za każdą dobę bez posiłku,
- każdy posiłek (`inv.py jedz`, 15 minut) obniża głód o 1, najwyżej 2 posiłki na dobę,
- surowe jedzenie (ziemniaki) trzeba ugotować: ogień, 45 minut, hałas 1, zużywa zapałkę.

### Woda

- Woda to zasób liczony w litrach, z jakością: **czysta** albo **surowa** (`inv.py pij`, 5 minut).
- Postać potrzebuje 2 litrów na dobę (chora: 3). Mniej niż norma, ale co najmniej litr: zmęczenie +1.
- Gotowanie (`inv.py gotuj`) zmienia wodę surową w czystą: 30 minut plus 10 na litr, hałas 1, zapałka, dym i światło ognia.
- Picie surowej wody: zapieczętowany rzut na chorobę, 20%. Objawy pojawiają się o najbliższym świcie.
- Doba bez wody (poniżej litra): zmęczenie +2. Od trzeciej takiej doby z rzędu: stan krytyczny.

### Choroba

Czerwonka (70%) albo dur brzuszny (30%). Tor ma poziomy 1–2:
- poziom 1: −1 krok do wszystkiego, potrzeba 3 litrów wody,
- poziom 2: −2 kroki do wszystkiego, stan krytyczny.

Co świt: zmęczenie +1 i rzut. Pogorszenie przy wyniku 30 lub mniej. Poprawa przy wyniku powyżej 100 − P, gdzie P = 30, +15 przy wypitych 3 litrach czystej wody, +40 po antybiotyku w tej dobie (`inv.py antybiotyk choroba`). Spadek do 0 oznacza wyzdrowienie.

### Rany

Nie ma punktów życia. Każda rana ma miejsce (głowa, tułów, ręka, noga) i ciężkość:

| Ciężkość | Skutek | Krwawienie |
|---|---|---|
| draśnięcie | brak kary, ryzyko zakażenia | brak |
| poważna | −1 krok do pasujących akcji | lekkie |
| krytyczna | −2 kroki do pasujących akcji | silne |

Kara z ran liczy się według najgorszej rany w miejscu, którego dotyczy akcja. To, że ran jest wiele, mierzy tor utraty krwi.

**Utrata krwi** to tor 0–10 *(skrypt: do zrobienia)*:
- nowa rana: poważna +1, krytyczna +2 (draśnięcie 0),
- co jednostkę każda nieopatrzona rana dokłada: lekkie krwawienie +1, silne +2,
- lekkie krwawienie bez opatrunku przez 6 jednostek przechodzi w silne (rana poważna staje się krytyczna), a postać dostaje +2 zmęczenia,
- opatrunek (test Opatrywania) zatrzymuje krwawienie tej rany,
- tor spada o 1 o świcie, jeśli żadna rana nie krwawi, a postać w minionej dobie spała co najmniej 6 godzin, jadła i wypiła normę wody.

| Utrata krwi | Skutek |
|---|---|
| 0–3 | brak |
| 4–6 | −1 krok do akcji fizycznych |
| 7–9 | −2 kroki do wszystkiego, stan krytyczny |
| 10 | śmierć z wykrwawienia |

**Stan krytyczny:** skrypt co jednostkę (przy utracie krwi) albo co dzień (przy chorobie, sepsie albo pragnieniu) rzuca na śmierć, 10%, dopóki stan nie zostanie opanowany.

### Zakażenie

Ugryzienie nie zamienia w sztywnego (zob. `Stiffs.md`), ale rana może się jątrzyć. Każda rana ma tor zakażenia 0–4:

| Poziom | Stan | Skutek |
|---|---|---|
| 0 | czysta | – |
| 1 | zaczerwienienie | – |
| 2 | gorączka | −1 krok do wszystkiego |
| 3 | sepsa | −2 kroki do wszystkiego, stan krytyczny |
| 4 | śmierć | – |

Skrypt co świt rzuca d100 dla każdej rany:

| Szansa pogorszenia (+1) | % |
|---|---|
| podstawa | 10 |
| rana poważna / krytyczna | +5 / +10 |
| ugryzienie | +15 |
| rana nieopatrzona | +15 |
| rana odkażona od ostatniego świtu (`inv.py odkaz`) | −10 |

Rana już zakażona może się też poprawić (−1) przy wyniku powyżej 100 − P, gdzie P = 20, +15 przy opatrunku i +10 po odkażeniu. Odkażenie zużywa porcję spirytusu albo wody utlenionej i działa do najbliższego świtu.

Antybiotyk (`inv.py antybiotyk <nr rany>`) od razu cofa zakażenie o 2 poziomy i zużywa opakowanie.

**Gojenie.** Opatrzona rana z zakażeniem 0–1 goi się o jeden dzień na każdy świt. Po 3 dniach draśnięcie znika. Po 10 dniach rana poważna staje się draśnięciem, a krytyczna poważną.

### Śmierć

- Śmierć postaci jest ostateczna.
- Skrypt `rise.py` od razu losuje, po ilu minutach postać wstanie jako świeżak. Wstaje w miejscu śmierci, z całym ekwipunkiem.
- Kampania trwa dalej. Nowa postać to NPC, którego gracz już spotkał (jeśli żyje), albo losowy ocalały w pobliżu. Świat, zegary i scenariusz się nie zmieniają.

## Nerwy

Nerwy to tor psychiki w skali 0–10.

**Co podnosi nerwy** (MG wybiera pozycję z katalogu, skrypt dolicza wartość):

| Wyzwalacz | Nerwy |
|---|---|
| noc bez snu | +1 |
| strzał w zamkniętym pomieszczeniu | +1 |
| zabicie świeżaka, który wyglądał jak żywy | +2 |
| sztywny, którego postać znała | +2 |
| śmierć towarzysza | +3 |
| śmierć bliskiego | +4 |

**Skutki:**
- **od 5:** −1 krok do Strzelania, Skradania, Opatrywania i Kombinowania,
- **od 8:** −2 kroki do tych umiejętności, a przy każdym nowym wyzwalaczu skrypt rzuca na **załamanie**.

**Załamanie** losuje skrypt z tabeli:
- zamarcie na jedną wymianę,
- panika i ucieczka,
- krzyk (hałas 3),
- uparta głupota.

Każde załamanie zostawia **stały tik**, czyli tag-traumę z kosztem.

**Co obniża nerwy:**

| Sposób | Nerwy | Koszt |
|---|---|---|
| papieros (`inv.py pal`) | −1 | zużywa papierosa (20 w paczce); działa najwyżej raz na godzinę; nocą na zewnątrz żar widać z daleka |
| rozmowa z żywym człowiekiem | −1 | – |
| alkohol (`inv.py alkohol`) | −2 | zużywa porcję; +1 zmęczenia, −1 krok do wszystkiego przez 2 godziny |
| modlitwa w kościele | −2 | raz dziennie |
| sen w bezpiecznym miejscu | −2 | – |

## Hałas i uwaga

Każda akcja ma **poziom hałasu** od 0 do 5. Poziom hałasu dodaje punkty do **uwagi** węzła:

| Poziom | Przykład | Uwaga |
|---|---|---|
| 0 | cisza | 0 |
| 1 | kroki | +1 |
| 2 | rozmowa, uderzenie | +2 |
| 3 | tłuczone szkło, krzyk | +4 |
| 4 | silnik, wyważanie drzwi | +8 |
| 5 | strzał | +16 |

Dodatkowo:
- strzał dodaje +8 uwagi każdemu sąsiedniemu węzłowi (zob. `Stiffs.md`: strzały słychać przez kilka przecznic),
- światło widoczne w nocy: +2 za każdą jednostkę,
- uwaga spada o 1 za każdą jednostkę.

**Progi uwagi** decydują o tym, co przychodzi przy spotkaniu:
- **4+:** pojedynczy sztywny,
- **8+:** grupa,
- **16+:** powstaje **pochód**.

Strzał zawsze kosztuje. Broń palna rozwiązuje problem tu i teraz, a za dziesięć minut tworzy większy.

### Pochód

Pochód to obiekt w `state.json`: pozycja, liczebność, kierunek. Co jednostkę:
- przesuwa się o jeden węzeł w stronę ostatniego głośnego dźwięku,
- rośnie o gęstość mijanych węzłów.

Gdy nie ma już za czym iść, rozprasza się i podnosi gęstość węzła, w którym stanął.

### Nieświadomi hałasujący

Niemowlę, małe dziecko, pies, kot i ptak nie rozumieją, że trzeba być cicho. Postać może ich nieść, ukrywać z sobą albo słyszeć w okolicy, a każdy z nich w złym momencie może się odezwać. Gracz tego nie kontroluje: o tym decyduje rzut.

**Z postacią.** Dotyczy każdego niemowlęcia, dziecka lub zwierzęcia, które postać niesie (ręce, plecak, torba) albo ukrywa z sobą (szafa, schowek, zamknięte mieszkanie). Co jednostkę (10 minut), gdy postać się ukrywa albo jest w węźle z uwagą powyżej 0, skrypt rzuca na hałasującego. Postać ukrywa się po udanym `fight.py zgub` i po udanym uniku (`encounter.py unik`), a przestaje, gdy przejdzie do innego węzła, wda się w starcie albo gracz powie, że wychodzi z ukrycia:

| Hałasujący | Szansa na jednostkę | Hałas |
|---|---|---|
| dziecko (płacz, wołanie) | 20% − 2% za każdy ukończony rok życia | 3 |
| pies (szczeknięcie, skomlenie) | 10% | 3 |
| kot (miauknięcie) | 8% | 2 |
| ptak cichy (gołąb, kanarek) | 3% | 1 |
| ptak głośny (papuga) | 10% | 3 |

- **Dziecko:** noworodek ma 20%, roczne 18%, pięciolatek 10%, dziewięciolatek 2%. Od ukończonych 10 lat dziecko rozumie, co się dzieje, jest zwykłym NPC i tej tabeli nie podlega. Wiek podaje scenariusz albo rzut, nie MG.
- Szansa (inna niż 0) rośnie o 10 punktów, jeśli w minionej jednostce w tym węźle był hałas 3 lub większy (strzał, wyważone drzwi, krzyk).
- Trafienie to jawny hałas o podanym poziomie w węźle postaci. Skutki liczą się według *Hałas i uwaga*.
- Postać nie wie z góry, kiedy to się stanie. Wie tylko, że opiekuje się kimś, kto nie wie, że ma milczeć.

**W okolicy.** W węzłach z ludźmi (osiedle, blok, ulica) hałasujący nie musi iść z postacią: gdzieś może szczekać pies albo płakać niemowlę zamknięte w mieszkaniu. Scenariusz może wskazać takiego hałasującego w konkretnym węźle (`halasujacy.py dodaj --wezel`); rzuca, gdy postać jest w tym węźle, według tej samej tabeli. Poza tym raz na jednostkę, gdy postać jest w węźle typu osiedle, blok albo ulica i nie śpi, skrypt rzuca 5%: pies szczeka albo dziecko płacze gdzieś w pobliżu (hałas 3 w tym węźle, jak w tabeli wyżej).

Sztywni idą za dźwiękiem niezależnie od jego źródła (zob. `Stiffs.md`, *Zmysły i zachowanie*). Pies, który hałasuje po drugiej stronie podwórza, może odciągnąć sztywnych od postaci albo ściągnąć ich w jej okolicę. O tym rozstrzyga zwykła uwaga węzła.

**Skrypt `halasujacy.py`.** Hałasującego dodaje się, gdy pojawia się przy postaci albo w scenariuszu: `halasujacy.py dodaj "<opis>" --rodzaj dziecko|pies|kot|ptak_cichy|ptak_glosny [--wiek N] [--wezel <id>]`. Bez `--wezel` jest z postacią. Wiek dziecka podaje scenariusz albo rzut. `ukryj` i `wyjdz` ręcznie ustawiają ukrycie (np. gdy postać chowa się, zanim cokolwiek się wydarzy), `usun` usuwa hałasującego (zginął, odszedł). Rzuty idą w tle i zapisują się w logu, a gracz widzi tylko trafienie, czyli dźwięk i hałas w węźle.

## Sztywni w skryptach

### Etap sztywnych

Etap sztywnego nie jest globalny. Zależy od:
- **źródła:** szpitale, kostnice i mieszkania z pierwszej nocy dają świeżaki; Cmentarz Północny daje zmarłych z zimy, w większości już gnilców; każda nowa śmierć daje nowego świeżaka,
- **czasu od śmierci,**
- **temperatury:** zimno spowalnia rozkład.

Skrypt liczy rozkład w **dniach rozkładu** ważonych temperaturą:

| Średnia temperatura dnia | Dni rozkładu |
|---|---|
| poniżej 0°C | 0,25 |
| 0–10°C | 0,5 |
| 10–20°C | 1 |
| powyżej 20°C | 2 |

Progi: **świeżak** do 10 dni rozkładu, **gnilec** do 60, później **padły**.

### Spotkania

Spotkania losują się **same** po każdej komendzie, która przesunęła czas, w każdym skrypcie. MG ich nie wywołuje. Raz na każdą jednostkę (10 minut) poza kryjówką skrypt sprawdza:

**Szansa spotkania** = gęstość węzła + 5% × uwaga węzła (najwyżej 90%).

- Węzeł o gęstości 0 (np. zamknięte mieszkanie) nie ma losowych spotkań. Zagrożeniem są w nim tylko ciała, które wstaną w środku.
- W węźle oznaczonym jako kryjówka gracza (`encounter.py kryjowka on`) nie ma losowych spotkań. Zdarzenia przy kryjówce rozliczy `dawn.py`.
- Kiedy sprawdzanie musi poczekać (trwa starcie, spotkanie albo decyzja o Farcie), żadna jednostka nie przepada. Skrypt nadrobi je później.

**Liczebność** zależy od uwagi węzła: poniżej 4 jeden sztywny, 4–7 jeden lub dwóch, 8–15 grupa (2–4), od 16 **pochód** (6–12, startuje „daleko”).

**Etap** zależy od źródła sztywnych w węźle (szpital, mieszkania, mieszane, cmentarz) i od dni rozkładu (zob. *Etap sztywnych*).

**Strefa startowa** zależy od światła: za dnia zwykle „daleko”, w półmroku i ciemności „blisko” albo „na wyciągnięcie ręki”.

**Kto zauważył pierwszy** to mechaniczna wersja zasady „telegrafuj” ze `Stiffs.md`:
- postać rzuca test Czujności z +3 krokami (z karami za światło),
- każdy świeżak ma zapieczętowany rzut na zasadzkę (30%); zaczajony świeżak daje −3 kroki,
- **postać zauważa pierwsza:** gracz wybiera `encounter.py unik` (test Skradania: −1 przy świeżakach, +1 gdy są daleko, −1 gdy tuż obok) albo `encounter.py walcz`,
- **zauważyli ją pierwsi:** od razu starcie; przy zasadzce świeżak atakuje z bliska i ma wolną wymianę.

Rzuty spotkania nie korzystają z Fartu.

**Broń w ręku.** `encounter.py bron <rodzaj>` ustala, co postać trzyma, chodząc po mieście. Z tym zaczyna każde starcie.

**Tożsamość.** Skrypt losuje dla każdego sztywnego, kim był i jeden szczegół (`Scripts/data/people.json`), bez powtórek w jednym spotkaniu. Pierwszeństwo mają:
1. ciała, które wstały w tym węźle (także poprzednia postać gracza),
2. znajomi ze scenariusza przypisani do węzła (`campaign.py znajomy`), z losem „martwy” albo „nieznany”, z szansą 25%.

Rozpoznanie kogoś znajomego: nerwy +2. Każdy sztywny był człowiekiem (zob. `Stiffs.md`).

### Wątpliwość

Gdy postać widzi kogoś w półmroku albo z daleka, skrypt rzuca zapieczętowany test Czujności. Wynik nie brzmi „to sztywny”, tylko podaje **pewność**:
- „chyba żywy”,
- „nie wiesz”,
- „raczej martwy”.

Gracz musi zdecydować, czy uderzyć pierwszy.

### Powstawanie zmarłych

Każdą śmierć MG rejestruje w `rise.py dodaj`, a skrypt od razu losuje, po ilu minutach (od 10 do 60) ciało wstanie. MG nigdy nie wybiera tego momentu sam. Moment jest zapieczętowany: jest w logu, ale nie na ekranie. Śmierć postaci gracza rejestruje się sama.

**Śmierć, która niszczy mózg.** Ciało nie wstaje, gdy sama śmierć zniszczyła mózg. Rozstrzyga to zasada, nie narracja MG. Mózg niszczy śmierć (dla NPC rejestruje się to przez `rise.py dodaj --bez-mozgu`; śmierć postaci gracza rejestruje się sama i skrypt rozpoznaje flagę `mozg_zniszczony`, ale żadna obecna śmierć postaci jej nie ustawia, bo ugryzienia, krwawienie, choroba i rozszarpanie mózgu nie niszczą):
- od rany głowy zadanej bronią palną, siekierą, saperką, łomem albo młotkiem,
- od zmiażdżenia głowy (przejechanie, przygniecenie, upadek z wysokości na głowę),
- od wybuchu albo spalenia całego ciała.

Każda inna śmierć mózgu nie niszczy, także od rany głowy zadanej nożem, pałką albo gołymi rękami. Takie ciało rejestruje się zwykle. Gdy przypadek nie pasuje do żadnego punktu, rozstrzyga `act.py los`. Ciało zniszczone śmiercią rejestruje się przez `rise.py dodaj --bez-mozgu`.

- Ciało, które wstaje w miejscu, gdzie jest postać, od razu zaczyna starcie „na wyciągnięcie ręki” albo dołącza do trwającego.
- Ciało, które wstaje gdzie indziej, czeka w swoim węźle i pojawi się w najbliższym spotkaniu tam.
- Ciała zwykłych sztywnych zniszczonych w walce nie wstają.

**Co zrobić z ciałem.** Gracz wybiera:

| Opcja | Komenda | Koszt |
|---|---|---|
| przebić mózg | `rise.py zniszcz` | 1 minuta, hałas 2, nerwy +1 (+2, jeśli postać znała zmarłego) |
| związać | `rise.py zwiaz` | sznur lub lina, 10 minut, hałas 1; ciało wstanie, ale w więzach |
| zamknąć w pomieszczeniu | – | potrzebne drzwi z zamkiem |
| spalić | `rise.py spal` | ogień, 30 minut, dym: uwaga +4 |
| zostawić | – | ciało wstanie według rzutu |

## Walka

### Dystans

Walka toczy się w czterech strefach:
1. **daleko,**
2. **blisko,**
3. **na wyciągnięcie ręki,**
4. **uchwycony.**

Prędkość sztywnego zależy od etapu rozkładu. Świeżak przebiega strefę w jedną wymianę, gnilec potrzebuje kilku.

### Wymiana

Walka toczy się wymianami po około 6 sekund (`fight.py`). W każdej wymianie gracz podejmuje **jedną decyzję**, a skrypt rozgrywa najpierw akcję postaci, potem ruchy wszystkich sztywnych.

- Po każdej wymianie skrypt pokazuje położenie sztywnych i **możliwe akcje z szansami**, więc gracz zna szansę przed decyzją.
- Akcje z testem: atak, strzał, odepchnięcie, wyrwanie się, bieg, zgubienie pościgu, zatrzaśnięcie drzwi, ucieczka w górę.
- Akcje bez testu (zajmują wymianę): czekanie, przeładowanie, zmiana lub podniesienie broni, wyciągnięcie zaklinowanej broni.
- Fart działa jak w zwykłych testach: wymiana czeka na decyzję gracza, a następna komenda oznacza przyjęcie wyniku.
- **Czas płynie w trakcie starcia:** wymiana to 6 sekund, a utrata krwi i rzuty na śmierć działają tak jak poza walką *(skrypt: do zrobienia)*.
- Starcie kończy się, gdy nie zostanie żaden sztywny (pokonany, zgubiony albo za drzwiami) albo gdy postać zginie.
- **Poddanie się.** Gracz może ogłosić, że postać przestaje się bronić. Skrypt rozgrywa wtedy `czekaj` aż do końca starcia. Sztywni nie przyjmują kapitulacji.
- W trakcie starcia `act.py` jest zablokowany.

**Zasadzka.** Gdy zapieczętowany rzut na zasadzkę wypadnie na niekorzyść postaci, sztywni mają wolną wymianę, zanim postać zareaguje.

### Cel to mózg

Atak to test Walki (albo Strzelania) z krokami z właściwości broni. Wobec gnilca test ma +1 krok, wobec świeżaka −2 kroki.

| Wynik | Skutek |
|---|---|
| czysty sukces | mózg zniszczony |
| sukces z kosztem | mózg zniszczony, ale broń może się zaklinować (szansa z tabeli broni), a jeśli nie, cios jest głośniejszy; przy strzale idzie dodatkowy nabój |
| porażka | trafienie poza mózg. Długa broń odrzuca sztywnego na „blisko”; inaczej sztywny jest okaleczony (wolniejszy) albo cios nic nie daje |
| katastrofa | broń wypada z rąk albo sztywny chwyta postać; broń palna się zacina |

**Długa broń trzyma na dystans, krótka sprawdza się w zwarciu.** To główna różnica taktyczna między łomem a nożem.

**Odcięta głowa wciąż gryzie.** Zniszczony musi być mózg.

### Cel: oczy

Zamiast w mózg można uderzyć albo strzelić w oczy (`fight.py atak --oczy`, `fight.py strzal --oczy`). Trafić łatwiej niż w mózg (+1 krok), ale to nie rozstrzyga starcia: sztywny nie pada, tylko ślepnie.

- **Skutek sukcesu:** sztywny jest **ślepy** do końca starcia. Nie widzi światła ani ruchu i kieruje się tylko słuchem (zob. `Stiffs.md`, *Zmysły i zachowanie*). Ślepy sztywny nie ślepnie drugi raz.
- **Ślepy sztywny w starciu:** zbliża się o strefę z szansą o połowę mniejszą, a chwyta z szansą mniejszą o 25 punktów. Przy biegu gubi się jak gnilec (sukces z kosztem wystarcza, żeby zyskać strefę). Do `zgub` nie liczy się jako pościg „blisko”.
- **Koszty i porażki:** jak przy celu w mózg (zaklinowanie, głośniejszy cios, dodatkowy nabój, upuszczona broń). Porażka to trafienie poza oczy.
- Ślepota nie zabija ani nie zmienia etapu. Ciało nie jest zniszczone, a ślepy sztywny dalej gryzie, jeśli kogoś trzyma.

### Uchwycenie

- Na koniec każdej wymiany każdy sztywny, który był na wyciągnięcie ręki, próbuje chwycić postać. Sztywny odepchnięty albo odrzucony w tej wymianie nie chwyta.
- Uchwycona postać może:
  - **wyrwać się:** test Kondycji, −1 krok za każdego dodatkowego sztywnego, który ją trzyma,
  - **walczyć z bliska:** krótką bronią bez kary; długa broń daje −2 kroki.
- Przy chwycie sztywny może ugryźć od razu. Potem w każdej wymianie każdy trzymający sztywny rzuca na **ugryzienie**. Ugryzienie to rana poważna w losowym miejscu, a twarz lub szyja to rana krytyczna. Każde ugryzienie: nerwy +1.
- **Ubranie chroni.** Gruba odzież (kożuch, skórzana kurtka, waciak, zimowy mundur) chroni ręce i tułów: ugryzienie w te miejsca ma 1 szansę na 3, że nie przebije materiału i nie zostawi rany. Kurtka ortalionowa, sweter i piżama nie chronią. Ochronę zapisuje się przy przedmiocie *(skrypt: do zrobienia)*.
- Gdy postać trzyma trzech lub więcej sztywnych, skrypt co wymianę rzuca na **rozszarpanie**, czyli śmierć (zob. `Stiffs.md`: kilku sztywnych potrafi rozerwać dorosłego mężczyznę).

| Szansa na wymianę | Świeżak | Gnilec |
|---|---|---|
| ruch o strefę bliżej | 100% | 50% (okaleczony: połowa) |
| chwyt | 75% | 50% (okaleczony: −15) |
| ugryzienie przy chwycie | 60% | 30% |
| ugryzienie, gdy trzyma | 50% | 35% |
| rozszarpanie (3+ trzymających) | 25% | 25% |

### Broń

Dane broni są w `Scripts/data/weapons.json`:

| Broń | Hałas | Strefy | Mózg | Klinowanie | Krótka |
|---|---|---|---|---|---|
| gołe ręce | 2 | 3–4 | −3 | – | tak |
| łom | 2 | 3 | 0 | 5% | nie |
| siekiera | 2 | 3 | +1 | 25% | nie |
| młotek | 2 | 3–4 | 0 | 5% | tak |
| saperka | 2 | 3 | 0 | 10% | nie |
| pałka | 2 | 3 | −1 | – | nie |
| nóż | 1 | 3–4 | −1 w strefie 3, +1 w strefie 4 | 15% | tak |
| dwururka | 5 | 2–3 | +1 w strefie 3 | – | nie; 2 naboje, potem przeładowanie |
| kałach | 5 | 1–3 | 0 (seria +1, 3 naboje) | – | nie; magazynek 30 |
| pistolet P-64 | 5 | 2–3 | −1 | – | tak; magazynek 6 |

**Otoczenie jako broń.** W zwarciu (strefa 4) postać może uderzyć głową sztywnego o kant stopnia, kaloryfer, krawężnik albo ścianę: mózg −2, broń krótka. Dostępne w węzłach z twardymi krawędziami (blok, piwnica, ulica, osiedle). Decyduje typ węzła, nie MG *(skrypt: do zrobienia)*.

Bez broni świeżak jest śmiertelnym zagrożeniem. To zamierzone: postać, która wychodzi z gołymi rękami, ryzykuje życie.

- **Mózg** to kroki do testu ataku.
- **Klinowanie** to szansa, że przy sukcesie z kosztem broń utknie w czaszce. Wyciągnięcie jej zajmuje wymianę.
- **Amunicja** jest liczona co do sztuki. Broń palna użyta wręcz to kolba (−2).
- Wytrzymałości broni jeszcze nie ma.

### Etap sztywnego zmienia zasady

- **Gnilce** są groźne w masie. Nie otwierają drzwi, nie chowają się.
- **Świeżak** jest groźny sam w sobie. Otwiera drzwi za klamkę, wchodzi po schodach i drabinach, potrafi czekać w ukryciu.

### Ogień

- Płonący sztywny idzie dalej, dopóki ogień nie dotrze do mózgu. Skrypt losuje, ile wymian to trwa.
- Każdy kontakt z płonącym sztywnym grozi podpaleniem postaci albo otoczenia.
- Palenie ciał, które jeszcze nie wstały, i ciał padłych działa (zob. *Co zrobić z ciałem*).

## Pościg

Sztywni się nie męczą, a świeżak biega prawie jak żywy. Długiego biegu postać ze świeżakiem nie wygra (zob. `Stiffs.md`). Trzeba go zgubić, ukryć się albo zamknąć drzwi.

Pościg to ten sam mechanizm co walka (`fight.py`), w strefach 1–4. Sztywny, który zgubi postać, wypada ze starcia. W każdej wymianie gracz może wybrać:

- **Biec** (Kondycja):
  - wobec gnilców: sukces daje +1 strefę dystansu,
  - wobec świeżaka: czysty sukces daje +1 strefę, sukces z kosztem i porażka nie zmieniają dystansu,
  - katastrofa: każdy sztywny o strefę bliżej, upadek i draśnięcie nogi,
  - każda wymiana biegu: +1 zmęczenia.
  - Dystans większy niż „daleko” oznacza zgubienie pościgu.
- **Zgubić** (Skradanie):
  - możliwe tylko w węźle z kryjówkami (cecha węzła, domyślnie tak),
  - w strefie 2: −2 kroki; w strefach 3 i 4: niemożliwe.
- **Zamknąć drzwi** (Majsterkowanie, podejście szybko):
  - możliwe tylko w węźle z drzwiami (cecha węzła: brak, zwykłe albo z zamkiem),
  - gnilce zostają za drzwiami,
  - drzwi zwykłe zatrzymują świeżaka na 1 wymianę, potem otwiera je klamką,
  - drzwi zamknięte na zamek zatrzymują także świeżaka (zob. *Barykady*).
- **Wspiąć się** (Kondycja): gnilce zostają na dole. Świeżaki wspinają się za postacią, ale tracą strefę dystansu.

## Barykady

- Barykada ma siłę 0–10. Buduje się ją Majsterkowaniem, a kosztuje czas i materiały.
- Co jednostkę naporu skrypt rzuca, czy barykada puszcza. **Szansa = 5% × liczba napierających − 8% × siła barykady**, najmniej 0. Świeżak liczy się za dwóch napierających.
- Świeżak sam otwiera każde drzwi, które nie są zamknięte na zamek.

## Przeszukiwanie

Przeszukanie to zwykła akcja `act.py wycen przeszukanie` (Czujność, 30 minut, hałas 2), z wyceną, rzutem i Fartem. Typ miejsca to typ węzła z mapy. MG go nie wybiera.

Wynik przeszukania zależy od:
- **typu miejsca:** tabele łupu w `Scripts/data/loot.json` dla mieszkania, klatki bloku, piwnicy, sklepu, kiosku Ruchu, apteki, Pewexu, działek, komisariatu MO, jednostki wojskowej, szpitala, zajezdni, kościoła i osiedla,
- **stopnia wyniku:** czysty sukces daje 3 rzuty na łup, sukces z kosztem 2, porażka 1, katastrofa 0,
- **podejścia:** porządnie to lepsza szansa, ale dwa razy dłużej, więc więcej jednostek i więcej spotkań,
- **stopnia splądrowania:** wartość bazowa dla typu miejsca, +3% za każdy dzień od apokalipsy, +25% za każde wcześniejsze przeszukanie (najwyżej 95%). Każdy rzut na łup przepada z tą szansą.

Znalezione przedmioty trafiają do rzeczy postaci.

W trakcie przeszukania skrypt może wylosować zdarzenie (15% + 2% za każdy punkt uwagi, najwyżej 50%):
- sztywny w pobliżu, czyli spotkanie „na wyciągnięcie ręki”,
- świeże zwłoki, które wstaną (trafiają do `rise.py`),
- łoskot (hałas 3),
- odcięta głowa w wannie (nerwy +1),
- skaleczenie o szkło,
- notatka zostawiona przez mieszkańców.

Łup pasuje do 1990 roku: konserwy turystyczne, Vibovit, ocet, świece, baterie R20, dolary, Marlboro (waluta!), spirytus, leki z apteki, książki.

## NPC

### Reakcje i handel

- Pierwsza prośba do NPC to test Kombinowania. Kroki zależą od nastawienia NPC (wrogi −2, nieufny −1, obojętny 0, przyjazny +1) i od tego, czy postać oferuje coś, czego NPC potrzebuje.
- Kłamstwa i ukryte zamiary NPC to rzuty zapieczętowane.
- Zachowanie NPC po rzucie wynika z jego agendy w scenariuszu, a nie z tego, czego chce gracz.
- Handel opiera się na barterze za dolary, papierosy, wódkę i amunicję.

### NPC w starciu

NPC obecny przy starciu nie stoi bezczynnie z woli MG. W każdej wymianie skrypt rzuca na jego reakcję *(skrypt: do zrobienia)*:

| Nastawienie do postaci | Pomaga | Inaczej |
|---|---|---|
| przyjazny | 50% | stoi, krzyczy albo ucieka |
| obojętny | 25% | stoi, krzyczy albo ucieka |
| nieufny | 10% | stoi albo ucieka |
| wrogi | 0% | może przeszkodzić (10%) albo odejść |

- **Pomoc:** NPC atakuje sztywnego swoją bronią (test jak postaci z umiejętnością 2 i krokami broni) albo pomaga postaci się wyrwać (+1 krok).
- **Ucieczka:** po dwóch wymianach bez pomocy NPC ucieka z szansą 50%.
- Towarzysze działają według swoich zasad (lojalność, nerwy).
- Do czasu skryptu MG rozstrzyga reakcję każdego NPC w każdej wymianie przez `act.py los` z szansą z tabeli.

### Towarzysze

Postać może mieć towarzyszy NPC:
- pomoc towarzysza daje +1 krok do akcji, w której pomaga,
- towarzysz zjada racje, pije wodę i podnosi hałas tła kryjówki,
- ma własne nerwy i lojalność; jego decyzje w kryzysie (uciec, zostać, zdradzić) losuje skrypt,
- może zginąć i wstać, co daje postaci +3 nerwów,
- nie zastępuje testów postaci gracza i nie ratuje jej z opresji, chyba że wynika to z rzutu.

## Skrypty

Zestaw skryptów (✔ = gotowy):

| Skrypt | Zadanie |
|---|---|
| `campaign.py` ✔ | zakładanie kampanii, węzły i połączenia, znajomi (los losuje skrypt), sztywni ze scenariusza, start, zegary zagrożeń (+1/−1 z powodem), podgląd stanu, próg automatu |
| `character.py` ✔ | kreator postaci: katalogi, sprawdzenie karty, losowanie ekwipunku, nowa postać po śmierci poprzedniej |
| `act.py` ✔ | wycena i rzut akcji, Fart, czynności rutynowe, sen, światło, `los` (pytanie o świat: 50/50 albo szansa ze scenariusza); koszty czasu i hałasu; krwawienie i stan krytyczny (dalej: automatyczne spotkania) |
| `fight.py` ✔ | walka i pościg: wymiany, chwyt, ugryzienia, broń, amunicja, zasadzka, drzwi, wspinaczka; cel w oczy (`--oczy`) |
| `sim.py` ✔ | symulacje Monte Carlo starć do kalibracji liczb |
| `inv.py` ✔ | ekwipunek (lista, weź, odłóż), jedzenie, picie, gotowanie wody, papierosy, alkohol, odkażanie, antybiotyk; zysk, strata i wymiana z powodem |
| `encounter.py` ✔ | spotkania (losowane samoczynnie), kto zauważył pierwszy, zasadzki, unik, tożsamość sztywnych, broń w ręku, kryjówka |
| ~~`stiff_people.py`~~ | wbudowany w spotkania (`stiffs/encounter.py`, `data/people.json`) |
| ~~`search.py`~~ | przeszukanie to akcja w `act.py` (`stiffs/loot.py`, `data/loot.json`) |
| `rise.py` ✔ | rejestr ciał, moment powstania, zniszczenie, związanie, spalenie; `--bez-mozgu` dla śmierci, która sama zniszczyła mózg |
| `halasujacy.py` ✔ | nieświadomi hałasujący (dzieci, zwierzęta): rejestr, ukrycie postaci; rzuty w tle co jednostkę czasu |
| `dawn.py` ✔ | podgląd doby; rozliczenie świtu dzieje się samo (`stiffs/body.py`), sen to `act.py spij` |
| `scenario_seed.py` ✔ | ziarno scenariusza: 3 zegary, 2 frakcje, niedobór, los bliskich; raz na kampanię, wynik tajny |
| `addendum.py` | dopiski do scenariusza |
| ~~`status.py`~~ | niepotrzebny: `state.md` generuje się przy każdym zapisie stanu |
| `resume.py` ✔ | wznowienie sesji: lista kontrolna, stan, sprawy otwarte, kronika, log |

**Wersja minimalna** do pierwszej sesji testowej jest gotowa. Zegary zagrożeń tykają o świcie (50% na segment). Brakuje jeszcze: `addendum.py`, zdarzeń przy kryjówce, pochodów jako obiektów na mapie, katalogu wyzwalaczy nerwów i załamań oraz Wątpliwości.

## Otwarte kwestie

- **Zasady opisane, skrypt jeszcze nie** (oznaczone *(skrypt: do zrobienia)*): czas i utrata krwi w starciu, poddanie się, przejście jawne bez testu, szansa spotkania w wycenie, ubranie chroniące przed ugryzieniem, otoczenie jako broń, NPC w starciu, tajny `los`, zdarzenia z osi czasu zatrzymujące sen, załamania przy nerwach 8+. Do czasu poprawki MG nie stosuje ich ręcznie, tylko gra według obecnych skryptów i mówi o tym graczowi. Wyjątek to NPC w starciu: rozstrzyga je `act.py los` według tabeli.
- **Skrypt robi coś, czego zasady już nie mają:** `stiffs/encounter.py` wciąż obcina o połowę szansę spotkania przy przymrozku. Do usunięcia przy synchronizacji skryptów.
- **Kalibracja po zmianach:** tor utraty krwi i ubranie zmienią wyniki `sim.py`. Trzeba je policzyć od nowa.

- **Kalibracja liczb.** Cel: postać z łomem i Walką 2 wychodzi cało ze starcia z 1 gnilcem w około 85–90% przypadków, z 3 gnilcami w około 50%, z 1 świeżakiem w zasadzce w około 40%. Wynik `sim.py --tabela` (za dnia, z 1 punktem Fartu):

  | Starcie | Cało | Ranny (w tym krytycznie) | Martwy |
  |---|---|---|---|
  | 1 gnilec | 98% | 2% (1%) | 0% |
  | 3 gnilce | 53% | 45% (19%) | 2% |
  | 5 gnilców | 7% | 47% (28%) | 47% |
  | 1 świeżak, widziany z dystansu | 94% | 6% (3%) | 0% |
  | 1 świeżak w zasadzce | 45% | 55% (19%) | 0% |
  | 1 świeżak + 2 gnilce | 38% | 51% (23%) | 12% |

  Pojedynczy gnilec jest łatwiejszy niż cel, co zgadza się ze `Stiffs.md` („jeden gnilec to kłopot”). Symulacja nie liczy śmierci z krwawienia po walce, a rana krytyczna bez szybkiego opatrunku często zabija.
- **Katalog akcji:** około 30 akcji z kosztami, skutkami porażki i tabelami katastrof.
- **Tabele:** łup według typu miejsca, tożsamość sztywnych, zdarzenia przy przeszukaniu, załamania, tagi zdobyte, archetypy zegarów zagrożeń.
- **Mapa Warszawy:** wybór węzłów, gęstość, źródła sztywnych i czasy przejścia.
- **Wartości barterowe** towarów.
