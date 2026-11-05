# Tworzenie postaci

Postać powstaje w rozmowie, zanim powstanie scenariusz. MG zadaje graczowi pytania, gracz odpowiada własnymi słowami, a MG ewentualnie dopytuje, uzupełnia luki i zapisuje odpowiedzi w folderze kampanii w pliku `Character.md` tworzonym na podstawie szablonu `CharacterTemplate.md`. Scenariusz zawsze powstaje dopiero po stworzeniu postaci.

## Opis postaci

Na początku MG prosi gracza o opis postaci. Gracz opisuje swoją postać dowolnie dokładnie. To mogą być dwa zdania, akapit albo strona tekstu, ale gracz MUSI podać poniższe trzy fakty o swojej postaci. Jeśli któregoś nie wymienił, MG dopytuje o niego.

1. Jak ma na imię i nazwisko?
2. Ile ma lat?
3. Jaki ma zawód i gdzie pracuje?

Poniższe fakty też są potrzebne. Jeśli gracz nie uwzględnił ich w opisie, MG sam uzupełnia te informacje tak, aby były spójne z opisem postaci gracza, przedstawiając je do akceptacji graczowi. Gracz może skorygować każdy z tych faktów.

1. W jakiej dzielnicy mieszka postać?
2. W jakim rodzaju budynku i na którym piętrze?
3. Z kim mieszka? Kim są bliscy postaci?
4. Co postać robiła w środę 21 marca 1990 roku tuż przed północą?
5. Jak była ubrana i co miała przy sobie?

### Kiedy MG może się nie zgodzić z opisem postaci

MG może odmówić zaakceptowania opisu postaci gracza **wyłącznie z powodu niezgodności z lore świata lub wewnętrznych sprzeczności**, a nie dlatego, że postać byłaby przez to za mocna albo za wygodna. Odmawiając, MG wskazuje konkretny powód (sprzeczność w opisie albo `World.md` i `Stiffs.md`) i od razu proponuje realistyczną wersję.

W sporze o to, czy odpowiedź mieści się w świecie, MG nie ustępuje pod naciskiem, a gracz nie musi się zgadzać. MG i gracz przedstawiają swoje stanowisko po jednym razie, bez dalszej dyskusji, po czym rozstrzyga rzut 50/50 (`coin.py`). Skrypt wskazuje, kto ma rację, a opis postaci zostaje zapisany tak, jak chciał zwycięzca. Wynik jest wiążący do końca kampanii i trafia do `rulings.md`.

## Determinacja, słabości i zalety

Następnie określone są słabości, zalety i Punkty Determinacji (PDT) postaci.

Postać gracza ma domyślnie 20 PDT. Słabości zwiększają liczbę PDT, a zalety zmniejszają. Postać może mieć dowolną liczbę słabości i zalet, pod warunkiem że PDT mieści się w przedziale od 10 do 30 punktów. Przykładowo: gracz określił tyle zalet, że ma 8 PDT. Musi więc dodać sobie jakąś słabość tak, żeby PDT wzrosło do co najmniej 10.

W obliczaniu końcowego PDT postaci MG posługuje się poniższymi tabelami słabości i zalet. Jeśli jakiejś słabości lub zalety nie ma w tabeli, MG sam określa jej skutki dla gry oraz ile PDT daje lub odbiera, wzorując wartości na przykładach z tabel.

Postać nie może mieć jednocześnie słabości i zalety, które się wykluczają. Dotyczy to na pewno par: Silny i Cherlak; Wytrzymały i Astmatyk, Otyły albo Kulawy; Odporny i Chorowity; Czujny i Krótkowidz, Niedosłyszący albo Niewidomy; Niewidomy i Krótkowidz, Dobry strzelec albo Dobry kierowca; Cichy i Niezdara; Spłukany i Forsiasty albo Zapobiegliwy. Jeśli gracz wybierze taką parę, MG każe mu zrezygnować z jednej z nich. Przy innych parach, które wydają się sprzeczne, rozstrzyga zdrowy rozsądek MG, a w sporze rzut `coin.py`.

### Tabela słabości

| Słabość         | Skutek                                                                                    | PDT |
|-----------------|-------------------------------------------------------------------------------------------|-----|
| Niewidomy       | Nie widzi wcale; orientuje się dotykiem i słuchem                                         | +9  |
| Krótkowidz      | Bez okularów słabo widzi, np. może łatwiej pomylić człowieka ze świeżakiem                | +2  |
| Niedosłyszący   | Słabo słyszy: później zauważa kroki, hałas i zbliżających się sztywnych                   | +2  |
| Jednoręki       | Ma trudności z czynnościami wymagającymi 2 rąk, np. wspinaczka                            | +3  |
| Kulawy          | Utyka, biega wolno i nie ucieknie nikomu, kto go goni                                     | +3  |
| Astmatyk        | Szybko traci oddech przy biegu i wysiłku, źle znosi dym i kurz                            | +2  |
| Otyły           | Ciężki i mało sprawny: szybko się męczy, gorzej się wspina i przeciska                    | +2  |
| Cherlak         | Mało siły: trudniej mu z ciężarami, w walce wręcz i przy wyważaniu drzwi                  | +2  |
| Chorowity       | Łatwiej łapie choroby i wolniej goi rany                                                  | +2  |
| Cukrzyk         | Potrzebuje insuliny i regularnych posiłków; bez nich szybko słabnie, a potem umiera       | +4  |
| Starość         | Ponad 60 lat: wolniejszy, słabszy i szybciej się męczy                                    | +3  |
| Tchórz          | Łatwiej wpada w panikę i traci głowę w niebezpieczeństwie                                 | +2  |
| Klaustrofob     | Lęk przed ciasnymi, zamkniętymi miejscami (piwnica, winda, szafa)                         | +1  |
| Wybuchowy       | Łatwo traci panowanie nad sobą, kłóci się z ludźmi i trudno mu o zaufanie                 | +1  |
| Niezdara        | Częściej coś upuszcza, potyka się i niechcący hałasuje                                    | +2  |
| Twardy sen      | Bardzo trudno go obudzić: śpi, gdy wokół jest głośno                                      | +2  |
| Nałogowy palacz | Musi palić; kaszel i dym zdradzają jego obecność                                          | +1  |
| Alkoholik       | Musi się napić, inaczej trzęsą mu się dłonie                                              | +2  |
| Skompromitowany | Ludzie w okolicy go nie lubią i niechętnie mu pomagają (np. znany donosiciel)             | +2  |
| Spłukany        | Nie ma grosza przy duszy, poza paroma drobnymi                                            | +1  |

### Tabela zalet

| Zaleta          | Skutek                                                                        | PDT |
|-----------------|-------------------------------------------------------------------------------|-----|
| Mistrz karate   | O wiele lepiej radzi sobie walcząc wręcz i ma ogólnie dobrą sprawność         | -3  |
| Silny           | Dużo siły: łatwiej mu z ciężarami, w walce wręcz i przy wyważaniu drzwi       | -2  |
| Akrobata        | Doskonale radzi sobie w sytuacjach wymagających zręczności i równowagi        | -2  |
| Wytrzymały      | Dobra kondycja (np. biegacz): dużo wolniej się męczy i dłużej utrzymuje tempo | -2  |
| Odporny         | Rzadko choruje i szybciej goi rany                                            | -2  |
| Opanowany       | Nie wpada w panikę                                                            | -3  |
| Czujny          | Dobry wzrok i słuch: wcześniej zauważa zagrożenie                             | -2  |
| Cichy           | Porusza się i działa cicho, trudniej go usłyszeć                              | -2  |
| Dobry strzelec  | Celnie strzela; nie daje broni ani amunicji                                   | -2  |
| Posiadacz broni | Ma legalnie w domu strzelbę myśliwską z kilkunastoma nabojami                 | -2  |
| Sanitariusz     | Zna pierwszą pomoc: lepiej opatruje rany i rozpoznaje zakażenia               | -2  |
| Złota rączka    | Naprawia i majsterkuje, np. rower, zamek, instalację                          | -2  |
| Włamywacz       | Umie otwierać zamki i drzwi bez klucza                                        | -2  |
| Surwiwalista    | Umie przetrwać w trudnych warunkach: ogień, woda, orientacja w terenie        | -2  |
| Znawca miasta   | Zna Warszawę, skróty, podwórka i przejścia (np. taksówkarz, listonosz)        | -2  |
| Znajomości      | Zna w mieście ludzi, którzy mogą oddać przysługę (np. dozorca, milicjant)     | -2  |
| Dobry kierowca  | Świetnie prowadzi pojazdy; samochodu nie daje                                 | -1  |
| Pływak          | Dobrze pływa: bezpieczniej przeprawi się przez rzekę                          | -1  |
| Zapobiegliwy    | Ma w domu zapas jedzenia i wody na kilka dni                                  | -1  |
| Forsiasty       | Ma znaczną ilość gotówki przy sobie lub w znanym sobie miejscu                | -1  |

