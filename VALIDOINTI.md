# Validointisuunnitelma

Simulaattorin tulokset validoidaan kahdella tasolla:

1. **Automaattinen regressiovalidointi:** testit kansiossa `tests/` vertaavat simulaattorin tuloksia käsinlaskuihin ja riippumattomaan Python-viitelaskentaan (`tests/viite.py`). Viitelaskenta ei käytä simulaattorin koodia, ja sen CPM-algoritmi on toteutettu eri tavalla (relaksaatio ilman topologista järjestystä). GitHub Actions ajaa testit jokaisesta muutoksesta ja maanantaisin.
2. **Opettajan validointi:** vastuuopettaja tarkistaa jokaisen rivin simulaattorissa käsinlaskulla tai toisella työkalulla. Tulos kirjataan tähän tiedostoon (päivämäärä, validoija, menetelmä). Validointikierros avautuu issueksi automaattisesti 15.1. ja 15.8.

Kun laskentamallia muutetaan, muutoksen koskemat rivit palautetaan tilaan *Ei validoitu*.

Simulaattorissa ei ole kalibroituja vakioita: kaikki tulokset seuraavat suoraan alla olevista määritelmistä ja syötetiedoista.

## Mallit ja määritelmät

| Suure | Määritelmä | Huomio |
| --- | --- | --- |
| Aika | Kokonaiset työpäivät. Päivä 0 = ensimmäisen työpäivän alku; tehtävä varaa päivät ES … EF − 1 | Loppupäivämäärä = päivän EF − 1 päivämäärä |
| Riippuvuudet | LA/FS: ES_j ≥ EF_i + v; AA/SS: ES_j ≥ ES_i + v; LL/FF: EF_j ≥ EF_i + v; AL/SF: EF_j ≥ ES_i + v | v = viive (negatiivinen = limitys) |
| Eteenpäinlaskenta | ES_j = max(0, max ehdot) + aloitusviive + tasoitusviive; EF = ES + kesto | Kesto = M + lisäkesto |
| Taaksepäinlaskenta | LF_i = min(projektin loppu, seuraajien ehdot); LS = LF − kesto | |
| Kokonaispelivara | TF = LS − ES; kriittinen, kun TF = 0 | |
| Vapaa pelivara | FF = min seuraajien ehtojen jousto, enintään TF; ilman seuraajia projektin loppu − EF | |
| Kriittinen ketju | Lopusta alkuun niiden kriittisten edeltäjien kautta, joiden ehto määrää tehtävän ES:n | |
| Kalenteri | Ma–pe (tai 7 pv); valinnaisesti uudenvuodenpäivä, loppiainen, pitkäperjantai, pääsiäispäivä, 2. pääsiäispäivä, vappu, helatorstai, helluntaipäivä, juhannusaatto ja -päivä, pyhäinpäivä, itsenäisyyspäivä, jouluaatto, joulupäivä ja tapaninpäivä | Pääsiäinen gregoriaanisella algoritmilla (Meeus/Jones/Butcher). Juhannus- ja jouluaatto ovat vakiintuneita vapaapäiviä, eivät lakisääteisiä arkipyhiä. |
| Kustannus | Σ yksiköt · kesto · h/pv · €/h + kiinteä | Lisäkesto kasvattaa työkustannusta, kiinteä kustannus ei muutu |
| Kuormitus | Päivän kuorma = samanaikaisten tehtävien yksiköiden summa; ylikuormitus, kun kuorma > kapasiteetti | |
| Tasoitus | Sarjallinen ajoitus: valitaan tehtävä, jonka edeltäjät on ajoitettu ja jonka LS on pienin; sijoitetaan ensimmäiseen ajankohtaan, jossa kapasiteetti riittää | Heuristiikka; ei takaa lyhintä aikataulua. Tehtävää, jonka yksiköt ylittävät kapasiteetin, ei voi tasoittaa |
| Valmiusaste | Automaattisesti (ES … EF tasainen) tai käsin | |
| Ansaittu arvo | PV = Σ BAC_i · perustason valmius(t); EV = Σ BAC_i · valmius; AC = Σ nykyinen kustannus_i · valmius · toteutuneet/suunniteltu | BAC_i perustasosta |
| Indeksit ja ennusteet | SV = EV − PV, CV = EV − AC, SPI = EV/PV, CPI = EV/AC; EAC = BAC/CPI, AC + (BAC − EV) tai AC + (BAC − EV)/(CPI·SPI); ETC = EAC − AC; VAC = BAC − EAC; TCPI = (BAC − EV)/(BAC − AC) | |
| Ansaittu aikataulu | ES = hetki, jolloin perustason PV = EV (puolitushaku); SPI(t) = ES/AT; IEAC(t) = perustason kesto / SPI(t) | |
| PERT | tₑ = (O + 4M + P)/6, σ = (P − O)/6 kriittisen ketjun tehtäville; Tₑ = deterministinen loppu + Σ(tₑ − M); P = Φ((tavoite − Tₑ)/σ) | Ei huomioi rinnakkaisten polkujen yhdistymistä |
| Monte Carlo | Kesto kolmiojakaumasta (O, M, P) käänteisen kertymäfunktion avulla; mulberry32-satunnaislukugeneraattori, kiinteä siemenluku | Lisäkesto siirtää myös O:ta ja P:tä |

## V. Automaattisesti testatut suureet (tests/test_validointi.py)

| ID | Suure | Odotusarvon lähde | Odotettu | Tol. | Opettajan validointi |
| --- | --- | --- | --- | --- | --- |
| V01 | CE-esimerkin ES, EF, LS, LF jokaiselle tehtävälle, kokonaiskesto ja kriittinen ketju | Käsinlasku | Kesto 67 työpv; ketju A → B → C → F → H → I → J → K → L → M | täsmälleen | Ei validoitu |
| V01b | Kaikkien esimerkkien ES, EF, LS, LF, TF ja FF | Python-viitelaskenta | – | 10⁻⁶ | Ei validoitu |
| V02 | Riippuvuustyypit LA, AA, LL, AL ja viive (myös negatiivinen) | Käsinlasku, A 0–5 → B 3 pv | esim. LA+2: B 7–10; LL+2: B 4–7; AL+2: B 0–3 | täsmälleen | Ei validoitu |
| V03 | Kokonais- ja vapaa pelivara (CE: D, E, G) | Käsinlasku | D 17 / 0, E 19 / 2, G 17 / 17 pv | täsmälleen | Ei validoitu |
| V04 | Pääsiäinen 2026–2028, vapaapäivät 2027, työpäivien laskenta | Käsinlasku kalenterista | Pääsiäinen 5.4.2026, 28.3.2027, 16.4.2028; maaliskuu 2027: 21 työpäivää | täsmälleen | Ei validoitu |
| V05 | Tehtävien kustannukset ja BAC kaikissa esimerkeissä; CE tehtävä A | Python-viitelaskenta; käsinlasku | CE A 4593,75 € | 10⁻⁹ | Ei validoitu |
| V06 | Resurssikuormitus (CE: asentajat) | Käsinlasku | 6 ylikuormitettua päivää, huippu 3 | täsmälleen | Ei validoitu |
| V07 | Tasoitus: kapasiteetti ei ylity, riippuvuudet voimassa, loppu ei aikaistu | Ominaisuustesti kaikissa esimerkeissä | 0 ylikuormitettua päivää | täsmälleen | Ei validoitu |
| V08 | PERT: tₑ, Tₑ, σ ja todennäköisyys | Käsinlasku (A 4/5/8, B 2/3/6) | Tₑ = 8,667 pv, σ = 0,943 pv | 10⁻⁹ | Ei validoitu |
| V09 | Monte Carlo: kolmiojakauman keskiarvo ja mediaani, toistettavuus, O = M = P | Analyyttinen tri(5, 10, 20) | keskiarvo 11,667 pv, mediaani 11,340 pv | 1 % / 2 % | Ei validoitu |
| V10 | Seurantatilanteen BAC, PV, EV, AC, SPI, CPI, ES, SPI(t), EAC ja loppu kaikissa esimerkeissä | Python-viitelaskenta | – | 10⁻⁶ | Ei validoitu |
| V11 | Ansaittu arvo ja ansaittu aikataulu yhdelle tehtävälle | Käsinlasku (10 pv, 1000 €, tilanne 5, valmius 40 %, kustannukset 125 %) | SPI 0,8, CPI 0,8, ES 4, IEAC(t) 12,5 pv, EAC 1250 €, TCPI 1,2 | 10⁻⁶ | Ei validoitu |
| V12 | Myöhästymisen vaikutus (CE: D +20 pv, B aloitus +2 pv) | Käsinlasku | 70 ja 69 työpv | täsmälleen | Ei validoitu |
| V12b | Pelivaran mittainen viive ei siirrä loppua; kriittisen tehtävän +1 pv siirtää 1 pv | Ominaisuustesti kaikissa esimerkeissä | – | täsmälleen | Ei validoitu |

Harjoitusten vastaukset lasketaan samoilla funktioilla; testi U07 varmistaa, että jokainen harjoitus hyväksyy oikean vastauksen.

## Opettajan validoinnin kirjaus

| Päivämäärä | Validoija | Tunnukset | Menetelmä | Huomiot |
| --- | --- | --- | --- | --- |
| | | | | |
