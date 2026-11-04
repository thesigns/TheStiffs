# Zasady gry

*Nowe zasady, w trakcie pisania. Stare są w `RulesOld.md` i nie obowiązują.*

## Tworzenie postaci

Postać powstaje w rozmowie, zanim powstanie scenariusz. MG zadaje graczowi poniższe pytania, **wszystkie i w tej kolejności**. Gracz odpowiada własnymi słowami, a MG zapisuje odpowiedzi. Scenariusz powstaje dopiero potem i wychodzi z tego, co gracz powiedział o postaci, jej bliskich i jej nocy.

### Pytania

**Kim jest**
1. Jak ma na imię i nazwisko?
2. Ile ma lat i jak wygląda (kilka zdań)?
3. Jaki ma zawód i gdzie pracuje? Na jakiej zmianie?
4. Co umie dobrze (hobby, wojsko, harcerstwo, sport, sztuki walki), a czego wcale?
5. Jakie ma słabości i ograniczenia: zdrowie, nałogi, wzrok, wiek, lęki?

**Dom i bliscy**
6. W jakiej dzielnicy albo na jakim osiedlu mieszka (np. Wola, Bemowo, Jelonki, Sielce)? Gracz nie podaje ulicy ani numeru: ulicę i okolicę dobiera MG w scenariuszu.
7. W jakim rodzaju budynku (np. jedenastopiętrowy blok z wielkiej płyty z lat 70., kamienica z lat 50., dom jednorodzinny) i ile ma pięter?
8. Na którym piętrze mieszka (parter, środek, ostatnie)?
9. Z kim mieszka?
10. Kim są jej bliscy (1–3 osoby): imię, relacja, gdzie byli o północy, czego od nich chce albo się o nich boi?
11. Których sąsiadów i znajomych zna z imienia?

**Noc zero**
12. Co robiła wieczorem w środę 21 marca 1990 roku przed północą?
13. Gdzie była o północy i z kim? To jest miejsce startu.
14. W co była ubrana?
15. Co miała przy sobie (kieszenie, torba, plecak) i co ma w domu na wypadek, że tam wróci?
16. W jakim była stanie: zmęczona, głodna, pijana, zdenerwowana?

**Co ją pcha**
17. Czego chce przez tę noc i kolejne dni (jedna rzecz)? Czego się boi?
18. Czy są wątki, które gracz chce poprowadzić, albo takie, których woli uniknąć?

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
