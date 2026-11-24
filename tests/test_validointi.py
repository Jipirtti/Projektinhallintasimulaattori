"""Validointitestit V01–V12.

Odotusarvot tulevat käsinlaskusta (kirjattu testiin) tai riippumattomasta Python-viitelaskennasta
(tests/viite.py), joka ei käytä simulaattorin koodia. Ks. VALIDOINTI.md.
"""
import math
import pytest
import viite

EXAMPLES = ["ce", "robo", "halli", "tki", "sw"]


def two(typ, lag):
    """Kahden tehtävän verkko: A (5 pv) → B (3 pv) annetulla riippuvuudella."""
    return {"id": "t2", "n": ["V02", "V02"], "d": ["", ""], "start": "2027-01-04", "hpd": 8, "dl": 0, "bf": 1,
            "res": [["R", "R", "R", 1, 10]],
            "t": [["A", "A", "A", 5, 5, 5, "", "R:1", 0], ["B", "B", "B", 3, 3, 3, f"A {typ}{lag:+d}" if lag else f"A {typ}", "R:1", 0]]}


def test_V01_kriittinen_polku_kasinlasku(sim, logic, check):
    """CE-esimerkin aikaisimmat ja myöhäisimmät ajat käsinlaskusta."""
    sim.call("loadExample", "ce")
    s = sim.call("schedule")
    T = {t["id"]: t for t in s["tasks"]}
    hand = {"A": (0, 5, 0, 5), "B": (5, 9, 5, 9), "C": (7, 22, 7, 22), "D": (9, 21, 26, 38), "E": (13, 19, 32, 38),
            "F": (22, 42, 22, 42), "G": (21, 31, 38, 48), "H": (42, 54, 42, 54), "I": (48, 54, 48, 54),
            "J": (54, 62, 54, 62), "K": (62, 65, 62, 65), "L": (59, 67, 59, 67), "M": (67, 67, 67, 67)}
    check("V01", "CE kokonaiskesto", s["fin"], 67, 0, "työpv")
    for k, (es, ef, ls, lf) in hand.items():
        logic("V01", f"CE {k} ES/EF/LS/LF", (T[k]["ES"], T[k]["EF"], T[k]["LS"], T[k]["LF"]), (es, ef, ls, lf))
    logic("V01", "CE kriittinen ketju", s["chain"], ["A", "B", "C", "F", "H", "I", "J", "K", "L", "M"])


@pytest.mark.parametrize("ex", EXAMPLES)
def test_V01b_cpm_viitelaskenta(sim, logic, ex):
    """Kaikkien esimerkkien ES, EF, LS, LF, TF ja FF täsmäävät riippumattomaan viitelaskentaan."""
    sim.call("loadExample", ex)
    s = sim.call("schedule")
    r = viite.cpm(sim.call("exampleDef", ex))
    logic("V01b", f"{ex} kokonaiskesto", s["fin"], r["fin"])
    for t in s["tasks"]:
        i = t["id"]
        logic("V01b", f"{ex} {i} ES,EF,LS,LF,TF,FF",
              tuple(round(t[k], 6) for k in ("ES", "EF", "LS", "LF", "TF", "FF")),
              tuple(round(r[k][i], 6) for k in ("ES", "EF", "LS", "LF", "TF", "FF")))


@pytest.mark.parametrize("typ,lag,es,ef", [("FS", 2, 7, 10), ("FS", -2, 3, 6), ("SS", 2, 2, 5), ("FF", 2, 4, 7), ("SF", 2, 0, 3),
                                           ("LA", 0, 5, 8), ("AA", 0, 0, 3), ("LL", 0, 2, 5)])
def test_V02_riippuvuustyypit(sim, logic, typ, lag, es, ef):
    """Riippuvuustyypit ja viive käsinlaskusta: A 0–5, B kestää 3 pv."""
    sim.call("loadDef", two(typ, lag))
    B = sim.call("schedule")["tasks"][1]
    logic("V02", f"B:n ES, EF riippuvuudella A {typ}{lag:+d}", (B["ES"], B["EF"]), (es, ef))


def test_V03_pelivarat(sim, logic):
    """CE: kokonais- ja vapaa pelivara käsinlaskusta (D, E, G)."""
    sim.call("loadExample", "ce")
    T = {t["id"]: t for t in sim.call("schedule")["tasks"]}
    logic("V03", "D TF, FF", (T["D"]["TF"], T["D"]["FF"]), (17, 0))
    logic("V03", "E TF, FF", (T["E"]["TF"], T["E"]["FF"]), (19, 2))
    logic("V03", "G TF, FF", (T["G"]["TF"], T["G"]["FF"]), (17, 17))


def test_V04_kalenteri(sim, logic):
    """Pääsiäinen, Suomen arkipyhät ja työpäivien laskenta."""
    for y, d in [(2026, "2026-04-05"), (2027, "2027-03-28"), (2028, "2028-04-16")]:
        logic("V04", f"pääsiäispäivä {y}", sim.call("easter", y), d)
    logic("V04", "vapaapäivät 2027", sim.call("holidays", 2027),
          ["2027-01-01", "2027-01-06", "2027-03-26", "2027-03-28", "2027-03-29", "2027-05-01", "2027-05-06", "2027-05-16",
           "2027-06-25", "2027-06-26", "2027-11-06", "2027-12-06", "2027-12-24", "2027-12-25", "2027-12-26"])
    sim.call("loadExample", "ce")  # alku ma 11.1.2027
    logic("V04", "työpäivä 0", sim.call("workday", 0), "2027-01-11")
    logic("V04", "työpäiviä 11.–31.1.2027", sim.call("idxOfDate", "2027-01-31"), 15)
    sim.call("loadExample", "halli")  # alku ma 1.3.2027, pitkäperjantai ja 2. pääsiäispäivä vapaita
    logic("V04", "työpäiviä 1.–31.3.2027", sim.call("idxOfDate", "2027-03-31"), 21)
    logic("V04", "työpäivä 19 (pääsiäisen jälkeen)", sim.call("workday", 19), "2027-03-30")
    sim.call("set", "hol", False)
    logic("V04", "työpäiviä 1.–31.3.2027 ilman arkipyhiä", sim.call("idxOfDate", "2027-03-31"), 23)


@pytest.mark.parametrize("ex", EXAMPLES)
def test_V05_kustannukset(sim, check, ex):
    """Tehtävien kustannukset ja BAC riippumattomasta viitelaskennasta."""
    sim.call("loadExample", ex)
    s = sim.call("schedule")
    ref = viite.costs(sim.call("exampleDef", ex))
    for t in s["tasks"]:
        if ref[t["id"]]:
            check("V05", f"{ex} {t['id']} kustannus", t["cost"], ref[t["id"]], 1e-9, "€")
    check("V05", f"{ex} BAC", s["total"], sum(ref.values()), 1e-9, "€")


def test_V05b_kustannus_kasinlasku(sim, check):
    """CE tehtävä A: 5 pv · 1 · 7,5 h · 85 €/h + 5 pv · 0,5 · 7,5 h · 75 €/h = 4593,75 €."""
    sim.call("loadExample", "ce")
    check("V05b", "CE A kustannus", sim.call("schedule")["tasks"][0]["cost"], 4593.75, 1e-9, "€")


def test_V06_resurssikuormitus(sim, logic):
    """CE: asentajat (AS, kapasiteetti 2) H 42–54 kahdella ja I 48–54 yhdellä → 6 ylikuormitettua päivää, huippu 3."""
    sim.call("loadExample", "ce")
    lo = sim.call("loads")
    logic("V06", "AS ylikuormitetut päivät", lo["over"]["AS"], 6)
    logic("V06", "AS huippukuorma", lo["peak"]["AS"], 3)
    logic("V06", "AS kuorma päivinä 47, 48, 53, 54", [lo["L"]["AS"][d] for d in (47, 48, 53, 54)], [2, 3, 3, 0])


@pytest.mark.parametrize("ex", EXAMPLES)
def test_V07_tasoitus(sim, logic, ex):
    """Tasoituksen jälkeen kapasiteetti ei ylity, riippuvuudet pysyvät voimassa eikä projekti lyhene."""
    sim.call("loadExample", ex)
    fin0 = sim.call("schedule")["fin"]
    sim.call("level")
    s = sim.call("schedule")
    logic("V07", f"{ex} ylikuormitetut päivät tasoituksen jälkeen", sim.call("loads")["overDays"], 0)
    logic("V07", f"{ex} loppu ei aikaistu", s["fin"] >= fin0, True)
    T = {t["id"]: t for t in s["tasks"]}
    bad = []
    for t in sim.call("exampleDef", ex)["t"]:
        for i, typ, lag in viite.parse_pred(t[6]):
            a, b = T[i], T[t[0]]
            need = {"FS": a["EF"] + lag <= b["ES"], "SS": a["ES"] + lag <= b["ES"], "FF": a["EF"] + lag <= b["EF"], "SF": a["ES"] + lag <= b["EF"]}[typ]
            if not need:
                bad.append(f"{i}→{t[0]}")
    logic("V07", f"{ex} rikkoutuneet riippuvuudet", bad, [])


def test_V08_pert(sim, check):
    """PERT kahden tehtävän ketjulle: A (4, 5, 8), B (2, 3, 6)."""
    d = two("FS", 0)
    d["t"][0][4:6] = [4, 8]
    d["t"][1][4:6] = [2, 6]
    sim.call("loadDef", d)
    p = sim.call("pert")
    te = 8 + ((4 + 20 + 8) / 6 - 5) + ((2 + 12 + 6) / 6 - 3)
    sd = math.sqrt((4 / 6) ** 2 + (4 / 6) ** 2)
    dl = sim.call("deadlineIdx")
    check("V08", "tₑ(A)", p["chain"][0]["te"], 32 / 6, 1e-9, "pv")
    check("V08", "Tₑ", p["Te"], te, 1e-9, "pv")
    check("V08", "σ", p["sd"], sd, 1e-9, "pv")
    check("V08", "P(T ≤ tavoite)", p["P"], viite.phi((dl - te) / sd), 1e-4)


def test_V09_monte_carlo(sim, check, logic):
    """Kolmiojakauman keskiarvo ja mediaani analyyttisesti; O = M = P antaa deterministisen tuloksen."""
    d = two("FS", 0)
    d["t"] = [["A", "A", "A", 10, 5, 20, "", "R:1", 0]]
    sim.call("loadDef", d)
    m = sim.call("monteCarlo", 5000)
    check("V09", "keskiarvo tri(5, 10, 20) = 35/3", m["mean"], 35 / 3, 0.01, "pv")
    check("V09", "mediaani 20 − √75", m["p50"], 20 - math.sqrt(75), 0.02, "pv")
    logic("V09", "toistettavuus (sama siemenluku)", sim.call("monteCarlo", 500)["mean"], sim.call("monteCarlo", 500)["mean"])
    sim.call("loadExample", "ce")
    de = sim.call("exampleDef", "ce")
    for t in de["t"]:
        t[4] = t[5] = t[3]
    sim.call("loadDef", de)
    m = sim.call("monteCarlo", 200)
    logic("V09", "O = M = P: min ja max = deterministinen kesto", (m["min"], m["max"]), (67, 67))


@pytest.mark.parametrize("ex", EXAMPLES)
def test_V10_ansaittu_arvo(sim, check, ex):
    """Harjoitusten seurantatilanne: PV, EV, AC, SPI, CPI, SPI(t) ja EAC riippumattomasta viitelaskennasta."""
    sim.call("loadExample", ex)
    sc = sim.call("scenario", ex)
    sim.call("loadScenario")
    e = sim.call("evm")
    r = viite.evm(sim.call("exampleDef", ex), sc["dev"], sc["st"])
    for k in ("BAC", "PV", "EV", "AC", "SPI", "CPI", "ESt", "SPIt", "EAC"):
        check("V10", f"{ex} {k}", e[k], r[k], 1e-6)
    check("V10", f"{ex} loppu poikkeamien jälkeen", sim.call("schedule")["fin"], r["fin"], 0, "työpv")


def test_V11_ansaittu_aikataulu_kasinlasku(sim, check):
    """Yksi tehtävä 10 pv, 1000 €; tilannepäivä 5, valmius 40 %, toteutuneet kustannukset 125 %."""
    d = two("FS", 0)
    d["hpd"] = 10
    d["t"] = [["A", "A", "A", 10, 8, 14, "", "R:1", 0]]
    sim.call("loadDef", d)
    sim.call("set", "status", 5)
    sim.call("set", "auto", False)
    sim.call("setTask", "A", {"prog": 40, "acf": 1.25})
    e = sim.call("evm")
    exp = {"BAC": 1000, "PV": 500, "EV": 400, "AC": 500, "SPI": 0.8, "CPI": 0.8, "ESt": 4, "SPIt": 0.8, "IEACt": 12.5,
           "EAC": 1250, "ETC": 750, "VAC": -250, "TCPI": 1.2}
    for k, v in exp.items():
        check("V11", k, e[k], v, 1e-6)


def test_V12_myohastymisen_vaikutus(sim, check):
    """CE: D (TF 17) myöhästyy 20 pv → +3 pv; kriittisen B:n aloitus +2 pv → +2 pv."""
    sim.call("loadExample", "ce")
    sim.call("setTask", "D", {"extra": 20})
    check("V12", "D +20 pv: projektin kesto", sim.call("schedule")["fin"], 70, 0, "työpv")
    sim.call("setTask", "D", {"extra": 0})
    sim.call("setTask", "B", {"slip": 2})
    check("V12", "B aloitus +2 pv: projektin kesto", sim.call("schedule")["fin"], 69, 0, "työpv")


@pytest.mark.parametrize("ex", EXAMPLES)
def test_V12b_pelivaran_kaytto(sim, logic, ex):
    """Pelivaran mittainen viive ei siirrä loppua; kriittisen tehtävän 1 pv aloitusviive siirtää loppua 1 pv."""
    sim.call("loadExample", ex)
    s0 = sim.call("schedule")
    for t in s0["tasks"]:
        if t["D"] <= 0:
            continue
        if not t["crit"]:
            for k in ("extra", "slip"):
                sim.call("setTask", t["id"], {k: t["TF"]})
                logic("V12b", f"{ex} {t['id']} {k} = TF", sim.call("schedule")["fin"], s0["fin"])
                sim.call("setTask", t["id"], {k: 0})
        else:
            sim.call("setTask", t["id"], {"slip": 1})
            logic("V12b", f"{ex} {t['id']} kriittinen +1 pv", sim.call("schedule")["fin"], s0["fin"] + 1)
            sim.call("setTask", t["id"], {"slip": 0})
