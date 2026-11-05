# Zasady gry

*Nowe zasady, w trakcie pisania. Stare są w `RulesOld.md` i nie obowiązują.*

## Tworzenie postaci

Postać powstaje w rozmowie, zanim powstanie scenariusz. MG zadaje graczowi poniższe pytania, **wszystkie i w tej kolejności**. Gracz odpowiada własnymi słowami, a MG zapisuje odpowiedzi. Scenariusz powstaje dopiero potem i wychodzi z tego, co gracz powiedział o postaci, jej bliskich i jej nocy.

### Pytania

**Kim jest**
1. Jak ma na imię i nazwisko?
2. Ile ma lat i jak wygląda?
3. Jaki ma zawód i gdzie pracuje?
4. Co umie dobrze (hobby, wojsko, harcerstwo, sport, sztuki walki), a czego wcale?
5. Jakie ma słabości i ograniczenia: zdrowie, nałogi, wzrok, wiek, lęki?

**Dom i bliscy**
6. W jakiej dzielnicy albo na jakim osiedlu mieszka (np. Wola, Bemowo, Jelonki, Sielce)? Gracz nie musi podawać dokładnego adresu swojej postaci.
7. W jakim rodzaju budynku (np. jedenastopiętrowy blok z wielkiej płyty z lat 70., kamienica z lat 50., dom jednorodzinny) i ile ma pięter?
8. Na którym piętrze mieszka?
9. Z kim mieszka?
10. Kim są jej bliscy: imię, relacja, czy mieszka z nimi?

**Noc zero**
11. Co robiła wieczorem w środę 21 marca 1990 roku przed północą?
12. Gdzie była o północy i z kim? To jest miejsce startu.
13. W co była ubrana?
14. Co miała przy sobie (kieszenie, torba, plecak) i co ma w domu na wypadek, że tam wróci?
15. W jakim była stanie: zmęczona, głodna, pijana, zdenerwowana?

### Kiedy MG może się nie zgodzić

MG może odmówić przyjęcia odpowiedzi **wyłącznie z powodu świata**, a nie dlatego, że postać byłaby przez to za mocna albo za wygodna. Powody są trzy:

- coś, czego w Polsce w 1990 roku nie ma albo co nie istnieje w tym świecie (minigun, internet, trzy metry wzrostu, nadprzyrodzone zdolności),
- coś niemożliwego dla tej konkretnej osoby, np. broń palna u kogoś, kto jej nie mógł mieć (mają ją myśliwi, milicjanci, żołnierze i kolekcjonerzy z pozwoleniem),
- sprzeczność w opowieści (dyżur w szpitalu o północy i jednocześnie sen w domu).

Odmawiając, MG:
1. wskazuje konkretny powód ze świata (`World.md`, `Stiffs.md`),
2. od razu proponuje realistyczną wersję (np. zamiast kałasznikowa: dwururka po dziadku, która stoi w szafie na wsi),
3. zapisuje decyzję w `rulings.md`, żeby ta sama sytuacja zawsze kończyła się tak samo.

W sporze o to, czy odpowiedź mieści się w świecie, MG nie ustępuje pod naciskiem, a gracz nie musi się zgadzać: wtedy rozstrzyga rzut 50/50 (`act.py los`), a wynik jest wiążący do końca kampanii.

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
