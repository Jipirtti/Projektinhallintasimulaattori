# Muutosloki

## Julkaisematon

- Kopioi kuva: kuvan otsikko ja PNG-tiedoston nimi valitulla kielellä (aiemmin piirikaavion ja oskilloskoopin otsikko jäi suomeksi englannin- ja saksankielisessä kuvassa). Uusi testi KV10 tarkistaa, että jokaisen kaavion kuvassa on vain valitun kielen tekstejä.
- Saksankielinen käyttöliittymä (FI | EN | DE -valitsin, `?lang=de`, selaimen kieli de). Termit tarkistettu saksalaisista standardeista ja alan termistöstä. Kielitestit tarkistavat, ettei saksankielisessä näkymässä ole kääntämättömiä rivejä.
- Käyttöohje englanniksi (`docs/user-manual.md`) ja saksaksi (`docs/bedienungsanleitung.md`) omilla kuvakaappauksilla (`docs/kuvat/en/`, `docs/kuvat/de/`). `tools/rakenna_ohje.py` rakentaa kaikki kolme HTML-sivua, ja simulaattorin Käyttöohje-linkki avaa valitun kielen ohjeen.
- Kopioi kuva -painike jokaiseen kaavioon: kaavio leikepöydälle PNG-kuvana vaalealla taustalla ja kaksinkertaisella tarkkuudella, otsikon, selitteen ja lähdemerkinnän kanssa. Jos selain estää kopioinnin, kuva avautuu ikkunaan tallennettavaksi. Yhteinen SimKuva-moduuli kaikissa simulaattoreissa. Testit KV01–KV04.

## 1.0.0 – 2026-11-24

- Ensimmäinen julkaisu.
- Gantt-kaavio, kriittinen polku, perustaso, pelivarat, palkkien vetäminen ja myöhästymisen vaikutuskuvaaja.
- Verkkokaavio ja CPM-taulukko, riippuvuustyypit LA, AA, LL ja AL viiveineen.
- Resurssien kuormitus ja tasoitus.
- Kustannukset, ansaittu arvo ja ansaittu aikataulu.
- PERT ja Monte Carlo -ennuste, kriittisyysindeksi.
- Viisi esimerkkiprojektia, harjoitukset (ratkaisu avautuu vastauksen jälkeen) ja seurantatilanteet.
- Oman projektin luonti kuuden vaiheen kyselyllä, vienti ja tuonti.
- Suomi ja englanti, Palaute-painike, käyttöohje.
- Validointitestit V01–V12, kielitestit K01–K03, käyttötestit U01–U10 ja palautetestit P01–P07.
