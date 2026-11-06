
### Przedmioty

Nie ma limitu liczby przedmiotów ani katalogu, z którego trzeba wybierać. Przy sobie postać ma to, co mieści w kieszeniach i torbie i co ma sens dla jej zawodu i wieczoru: pielęgniarka na dyżurze ma torbę z lekami i opatrunkami, a nie rewolwer. MG pyta „gdzie to nosisz?” i patrzy, czy się to mieści. To samo kryterium stosuje do wszystkich postaci.

Rzeczy, które postać ma w domu, zostają w domu, w miejscu, do którego może wrócić.

## Rzut monetą (50/50)

Rzut monetą to najważniejsza zasada tej gry. Kiedy nie ma innej odpowiedzi, rozstrzyga **rzut monetą: 50% na TAK, 50% na NIE**. Moneta nie ma stronnictwa. Nie zależy od tego, co wypada narracyjnie, ani od tego, kto się bardziej upiera. Rzut wykonuje skrypt (`act.py los "<pytanie>"`), a MG i gracz przyjmują wynik.

### Kiedy rzucamy

1. **Spór między graczem a MG.** MG przedstawia swoje stanowisko i jego powód jeden raz, gracz przedstawia swoje jeden raz. Jeśli się nie zgadzają, nie ma dalszej dyskusji: rzucamy. Dotyczy to interpretacji zasad, tego, czy odpowiedź gracza mieści się w świecie, i każdego innego sporu.
2. **Pytanie o świat, na które nie ma odpowiedzi** w Manualu, w scenariuszu ani w tabelach: czy ktoś za zamkniętymi drzwiami żyje, czy w sklepie zostało jeszcze mleko, czy ktoś się obudzi od hałasu.
3. **Reakcja NPC, której nie rozstrzyga jego agenda** w scenariuszu.
4. **Gracz prosi o rzut.** Gracz może zażądać rzutu monetą zawsze, gdy uważa, że MG naginął wynik.

Jeśli scenariusz podaje szansę (np. „60%, że ktoś usłyszy”), rzucamy z tą szansą zamiast 50/50 (`act.py los --szansa N`). Jeśli odpowiedź jest w Manualu, scenariuszu albo tabeli, nie rzucamy.

### Jak rzucamy

- **Pytanie zadajemy przed rzutem**, w formie, na którą TAK i NIE oznaczają dwie jasno różne rzeczy. MG formułuje je neutralnie, bez podpowiadania wyniku. W sporze TAK oznacza wersję gracza, a NIE wersję MG.
- **Wynik jest wiążący.** Nie przerzucamy go i nie pytamy o to samo drugi raz w tej samej sytuacji. Fart (punkt, którym gracz może poprawić wynik testu) nie zmienia rzutu monetą.
- **Wynik dla sporu o zasady** trafia do `rulings.md` jako precedens i obowiązuje do końca kampanii. Wynik dla pytania o świat zapisuje się w logu i od tej chwili jest prawdą w świecie.
- **MG opowiada wynik dokładnie**, bez łagodzenia, i bez dopisywania, że „na szczęście”.

### Czego nie robimy

- MG nie używa rzutu monetą, żeby uniknąć decyzji, którą powinien podjąć na podstawie Manuala albo scenariusza.
- MG nie zadaje rzutu w formie, która przemyca korzyść jednej strony (np. „czy mimo to znajdziesz broń”).
- Gracz nie prosi o rzut tylko dlatego, że wynik poprzedniego mu się nie podobał.

## Hałas

Hałas to główny sposób, w jaki świat reaguje na postać. Sztywni idą za dźwiękiem (zob. `Stiffs.md`, *Zmysły i zachowanie*), więc każda czynność ma cenę w hałasie. Hałas liczy się prosto: **jeden hałas to jeden rzut**, bez kumulowania.

### Stopnie hałasu

Stopień to liczba całkowita od 0 do 5. Poniższe przykłady nie są zamkniętą listą: MG dopasowuje stopień do tego, co gracz opisuje.

| Stopień | Przykłady |
|---|---|
| 0 | cisza, bezruch i płytki oddech |
| 1 | skradanie się, szept, dyszenie ze zmęczenia |
| 2 | normalne chodzenie, zamknięcie drzwi, zwykła rozmowa, pukanie do drzwi |
| 3 | walka wręcz, trzaśnięcie drzwiami, przewrócenie czegoś na podłogę, bieg po schodach |
| 4 | krzyk, stłuczenie szyby, wyważanie drzwi, silnik samochodu albo motocykla |
| 5 | strzał z broni palnej, syrena, helikopter |

Ta sama skala obejmuje hałas, którego nie robi postać: płacz niemowlęcia, szczekanie psa, pochód, inni ludzie.

### Zagęszczenie sztywnych

Każde miejsce w scenariuszu ma w każdej porze **zagęszczenie** sztywnych w okolicy: *pusto*, *rzadko*, *sporo* albo *tłum*. Podaje je scenariusz, MG go nie zmienia. Zagęszczenie zmienia się z porą (noc, dzień) i z biegiem wydarzeń, jeśli scenariusz tak mówi.

### Protokół

Kiedy postać hałasuje:

1. **MG ustala stopień** na podstawie opisu gracza. Jeśli gracz się nie zgadza, spór rozstrzyga rzut monetą (zob. *Rzut monetą*).
2. **MG koryguje stopień** o najwyżej ±1:
   - −1 przy zamkniętych drzwiach, murze, piwnicy albo innej przegrodzie między hałasem a okolicą,
   - +1 w nocy na otwartej przestrzeni, gdzie miasto jest cichsze i dźwięk niesie się dalej.
   Stopień nie wychodzi poza 0–5.
3. **MG odczytuje szansę** z tabeli dla stopnia i zagęszczenia w tym miejscu.
4. **Skrypt rzuca** (`act.py los --szansa N`) i odpowiada: *ktoś usłyszał* albo *nikt*.
5. **Skutek** zależy od zagęszczenia i scenariusza: przy *pusto* i *rzadko* przychodzi jeden sztywny, przy *sporo* grupa, przy *tłum* pochód. Kiedy i skąd się pojawią, ustala odległość i scenariusz, a MG tego nie dopowiada.

Jedna czynność to jeden rzut, według jej najgłośniejszego momentu. Długa czynność (dłuższa niż dziesięć minut) rzuca się osobno co dziesięć minut. Hałas nie kumuluje się: cisza po hałasie nie "odrabia" wcześniejszego rzutu i na odwrót.

### Tabela zauważenia

Szansa, że **co najmniej jeden** sztywny usłyszy hałas:

| Stopień | pusto | rzadko | sporo | tłum |
|---|---|---|---|---|
| 0 | 0% | 2% | 5% | 15% |
| 1 | 0% | 5% | 15% | 35% |
| 2 | 0% | 15% | 35% | 65% |
| 3 | 5% | 35% | 65% | 90% |
| 4 | 15% | 65% | 90% | 100% |
| 5 | 35% | 90% | 100% | 100% |

Liczby są wstępne i będą kalibrowane na sesjach.





Sekcje „Postać”, „Zalety i słabości” oraz „Dom i bliscy” po utworzeniu
postaci są stałe. Reszta zmienia się w grze.*

## Postać

- **Imię i nazwisko:**
- **Wiek i wygląd:**
- **Zawód i miejsce pracy:**
- **Co umie dobrze:**
- **Czego nie umie wcale:**
- **Słabości i ograniczenia (opis):** zdrowie, nałogi, wzrok, wiek, lęki

## Zalety i słabości

Determinacja bazowa: 20. Po zsumowaniu musi mieścić się w przedziale 10–30.

| Nazwa | Rodzaj | Skutek | Determinacja |
|---|---|---|---|
| (np. Krótkowidz) | słabość | bez okularów słabo widzi, łatwiej pomylić świeżaka z człowiekiem | +3 |

**Maksimum Determinacji:** 20 ± suma = ...

## Determinacja

**Bieżąca / maksimum:** ... / ...

Dziennik zmian (MG dopisuje na końcu, nie poprawia wcześniejszych wpisów):

| Kiedy (czas gry) | Zmiana | Powód | Po zmianie |
|---|---|---|---|

## Dom i bliscy

- **Dzielnica lub osiedle:**
- **Budynek i liczba pięter:**
- **Piętro:**
- **Z kim mieszka:**
- **Bliscy:** imię, relacja, czy mieszka z postacią

## Noc zero

- **Wieczór 21 marca 1990:**
- **Miejsce i towarzystwo o północy (start):**
- **Ubranie:**
- **Przy sobie:**
- **W domu:**
- **Stan (zmęczenie, głód, upojenie, nerwy):**

## Rany i stan

- **Rany:**
- **Choroby i zakażenie:**
- **Głód, pragnienie, zmęczenie:**

## Ekwipunek

| Przedmiot | Gdzie jest (kieszeń, torba, dom) |
|---|---|
