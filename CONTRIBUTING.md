# Kehitysohjeet

Projektinhallintasimulaattoria kehitetään avoimesti Seinäjoen ammattikorkeakoulussa (SEAMK). Muutokset ja palaute ovat tervetulleita.

## Periaatteet

- Simulaattori on yksi tiedosto (`index.html`) ilman ulkoisia kirjastoja ja käännösvaihetta.
- Laskentamallia koskeva muutos vaatii kaksi asiaa:
  - testin tiedostoon `tests/test_validointi.py`
  - rivin tiedostoon `VALIDOINTI.md`

  Muutetun suureen opettajan validoinnin tila palautetaan arvoon *Ei validoitu*.
- Testin odotusarvo tulee käsinlaskusta tai riippumattomasta viitelaskennasta (`tests/viite.py`). Simulaattorin omia välituloksia ei käytetä odotusarvona.

## Koodin rakenne (index.html)

| Osa | Sisältö |
| --- | --- |
| `easter`, `holSet`, `cal`, `wdDate`, `idxOfDate` | Kalenteri ja arkipyhät |
| `parsePred`, `parseRes` | Riippuvuuksien ja resurssimerkintöjen jäsennys |
| `EX` | Esimerkkiprojektit ja niiden seurantatilanteet |
| `compute` | Kriittisen polun menetelmä, pelivarat, kriittinen ketju ja kustannukset |
| `loads`, `level` | Kuormitus ja resurssien tasoitus |
| `snap`, `evm` | Perustaso ja ansaittu arvo |
| `pert`, `monteCarlo` | Ennusteet |
| `drawGantt`, `drawNet`, `drawRes`, `drawEVM`, `drawMC` | Näkymät |
| `buildEx`, `renderEx` | Harjoitukset |
| `wFromEx`, `wToDef`, `wCheck`, `drawWizard` | Projektin luonti |
| `compactState`, `expandState` | Tallennusmuoto (esimerkeille vain muutokset) |
| `SimPalaute` | Palautekanava (sama moduuli kuin muissa simulaattoreissa; tekstit ja lomakepohja `1-laskenta.yml` annetaan init-kutsussa) |
| `window.PmSim` | Testirajapinta |

### Uusi esimerkkiprojekti

Lisää `EX`-taulukkoon nimi, kuvaus, alkupäivä, työpäivän pituus, tavoitteet (`dl`, `bf`), resurssit, tehtävät ja seurantatilanne (`scen`). Lisää esimerkin tunnus testien `EXAMPLES`-listaan, jolloin V01b, V05, V07, V10 ja V12b tarkistavat sen automaattisesti.

## Testit

```
pip install -r requirements-test.txt
python -m playwright install chromium
python -m pytest tests -v
```

Ajo kirjoittaa tiedoston `validointiraportti.md`.

## Palaute

Käytä issue-malleja (Laskentatulos ei vastaa odotusta, Virheilmoitus, Kehitysehdotus) tai simulaattorin Palaute-painiketta. Lomake liittää projektin JSON-muodossa, jotta tilanne voidaan toistaa.
