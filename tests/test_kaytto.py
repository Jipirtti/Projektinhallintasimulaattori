"""Käytettävyystestit U01–U10: esimerkit, välilehdet, tallennus, vetäminen, kumoaminen, harjoitukset ja projektin luonti."""
import json


def test_U01_esimerkit_ja_valilehdet(sim):
    """Jokainen esimerkki latautuu ja jokainen välilehti piirtyy ilman virheitä."""
    for e in sim.call("examples"):
        assert sim.call("loadExample", e["id"])
        for t in ["gantt", "net", "res", "evm", "mc", "ex"]:
            assert sim.call("setTab", t)
            assert sim.js(f"document.querySelector('#p-{t}').classList.contains('on')")
        assert sim.js("document.querySelectorAll('#kpis .kpi').length") == 5
    assert not sim.call("setTab", "xx")


def test_U02_tallennus_ja_lataus(sim):
    sim.call("loadExample", "halli")
    sim.call("setTask", "C", {"extra": 3})
    s = sim.call("serialize")
    sim.call("loadExample", "ce")
    assert sim.call("load", s)
    d = json.loads(sim.call("serialize"))
    assert d["ex"] == "halli" and d["compact"] == 1 and d["dev"] == {"C": {"e": 3}}
    assert d["version"] == sim.js("PmSim.version")
    st = sim.call("state")
    assert [t for t in st["tasks"] if t["id"] == "C"][0]["extra"] == 3 and sim.call("schedule")["fin"] == 68
    assert not sim.call("load", "{rikki")
    # Rakenteeltaan muutettu esimerkki tallennetaan kokonaan.
    sim.call("setTask", "C", {"d": 9})
    full = json.loads(sim.call("serialize"))
    assert "tasks" in full and "compact" not in full
    assert sim.call("load", json.dumps(full)) and sim.call("schedule")["fin"] == sim.call("schedule")["fin"]


def test_U03_ohjauskentta_paivittaa(sim):
    """Lisäkesto-kentän muutos päivittää valmistumisen."""
    sim.call("loadExample", "ce")
    sim.page.select_option("#tSel", "C")
    sim.page.fill("#tExtra", "4")
    sim.page.press("#tExtra", "Enter")
    assert sim.call("schedule")["fin"] == 71
    assert "71" in sim.js("document.querySelector('#kpis').innerText")


def test_U04_palkin_vetaminen(sim):
    """Palkin vetäminen oikealle lisää aloitusviiveen; oikean pään vetäminen lisää kestoa."""
    sim.call("loadExample", "ce")
    sim.page.wait_for_timeout(100)
    g = sim.js("(()=>{const c=document.querySelector('#cvG').getBoundingClientRect();return {x:c.left,y:c.top}})()")
    dw = sim.js("document.querySelector('#cvG').width") and None
    box = sim.page.locator("#cvG").bounding_box()
    # Rivi D (indeksi 3): palkki alkaa päivästä 9.
    geo = sim.js("(()=>{const s=PmSim.schedule();return s})()")
    sim.page.mouse.move(box["x"] + 5, box["y"] + 5)
    info = sim.js("(()=>{const c=document.querySelector('#cvG');return {w:c.clientWidth}})()")
    # Lasketaan koordinaatit samoin kuin piirto: vasen sarake 300 px, otsikko 38 px, rivi 28 px.
    left, head, row = 300, 38, 28
    dw = (info["w"] - left - 10) / (max(geo["fin"], sim.call("deadlineIdx"), sim.call("state")["status"]) + 3)
    y = box["y"] + head + 3 * row + row / 2
    x = box["x"] + left + (9 + 6) * dw
    sim.page.mouse.move(x, y)
    sim.page.mouse.down()
    sim.page.mouse.move(x + 5 * dw, y, steps=5)
    sim.page.mouse.up()
    D = [t for t in sim.call("state")["tasks"] if t["id"] == "D"][0]
    assert D["slip"] == 5, f"U04: aloitusviive {D['slip']}"
    x2 = box["x"] + left + (9 + 5 + 12) * dw - 2
    sim.page.mouse.move(x2, y)
    sim.page.mouse.down()
    sim.page.mouse.move(x2 + 3 * dw, y, steps=5)
    sim.page.mouse.up()
    D = [t for t in sim.call("state")["tasks"] if t["id"] == "D"][0]
    assert D["extra"] == 3, f"U04: lisäkesto {D['extra']}"


def test_U05_kumoa(sim):
    sim.call("loadExample", "ce")
    sim.page.select_option("#tSel", "C")
    sim.page.fill("#tExtra", "4")
    sim.page.press("#tExtra", "Enter")
    assert sim.call("schedule")["fin"] == 71
    sim.page.click("#undoBtn")
    assert sim.call("schedule")["fin"] == 67


def test_U06_ratkaisu_vasta_vastauksen_jalkeen(sim):
    """Ratkaisu on piilossa ennen vastausta; tyhjä vastaus ei avaa sitä; väärä vastaus avaa."""
    sim.call("loadExample", "ce")
    sim.call("setTab", "ex")
    ex = sim.page.locator(".ex").first
    assert ex.locator("details").count() == 0
    assert "Ratkaisu avautuu" in ex.locator(".solnote").inner_text()
    ex.locator("button[data-chk]").click()
    assert ex.locator(".fb").inner_text() == "Kirjoita vastaus ensin."
    assert ex.locator("details").count() == 0
    ex.locator("input").fill("1")
    ex.locator("button[data-chk]").click()
    assert ex.locator(".fb").inner_text().startswith("Ei vielä oikein")
    assert ex.locator("details").count() == 1


def test_U07_oikeat_vastaukset_hyvaksytaan(sim):
    """Jokaisen esimerkin jokainen harjoitus hyväksyy oikean vastauksen (desimaalipilkulla)."""
    for e in sim.call("examples"):
        sim.call("loadExample", e["id"])
        sim.call("setTab", "ex")
        res = sim.js("""(()=>{const out=window.__exOut;return out.map((o,j)=>{const ins=[...document.querySelectorAll(`[data-k$=":${j}"]`)];
          if(o.type==='set')ins[0].value=o.ans.join(', ');else if(o.type==='pair')o.ans.forEach((v,m)=>ins[m].value=v.toFixed(2).replace('.',','));
          else ins[0].value=(o.rtol?Math.round(o.ans):Math.round(o.ans*10)/10).toString().replace('.',',');
          ins.forEach(i=>i.dispatchEvent(new Event('input',{bubbles:true})));document.querySelector(`[data-chk="${j}"]`).click();
          return document.querySelector(`[data-chk="${j}"]`).parentElement.querySelector('.fb').classList.contains('ok')})})()""")
        assert len(res) >= 10 and all(res), f"U07 ({e['id']}): {res}"


def _wizard_project(sim):
    sim.page.select_option("#exSel", "__new")
    assert sim.js("document.querySelector('#mbox').dataset.wz") == "1"
    assert sim.js("document.querySelector('#exSel').value") == "ce"
    sim.page.fill('[data-w="name"]', "Testiprojekti")
    for _ in range(3):
        sim.page.click("#wNext")
    sim.page.click('[data-wadd="res"]')
    sim.page.fill('[data-wr="res"][data-i="1"][data-f="id"]', "AS")
    sim.page.fill('[data-wr="res"][data-i="1"][data-f="name"]', "Asentaja")
    sim.page.click("#wNext")
    sim.page.fill('[data-wr="tasks"][data-i="0"][data-f="name"]', "Suunnittelu")
    for i, (n, d, pr, rs) in enumerate([("Hankinnat", 10, "A", "PM:0.2"), ("Asennus", 8, "B", "AS:1"),
                                        ("Dokumentointi", 6, "A AA+2", "PM:0.5"), ("Luovutus", 0, "C, D", "")], start=1):
        sim.page.click('[data-wadd="tasks"]')
        for f, v in (("name", n), ("d", str(d)), ("pred", pr), ("res", rs)):
            sim.page.fill(f'[data-wr="tasks"][data-i="{i}"][data-f="{f}"]', v)


def test_U08_projektin_luonti(sim):
    """Kysely luo projektin, joka laskee oikein, tallentuu ja saa harjoitukset."""
    _wizard_project(sim)
    sim.page.click("#wNext")
    assert not sim.page.is_disabled("#wCreate")
    sim.page.click("#wCreate")
    s = sim.call("schedule")
    # A 0–5, B 5–15, C 15–23, D 2–8, E 23: kesto 23; kustannus 5·7,5·80 + 10·0,2·7,5·80 + 8·7,5·60 + 6·0,5·7,5·80 = 9600 €
    assert s["fin"] == 23 and abs(s["total"] - 9600) < 1e-6 and s["chain"] == ["A", "B", "C", "E"]
    assert sim.call("customs")[0]["n"] == "Testiprojekti"
    assert len(sim.call("exercises")) >= 10
    sim.page.reload()
    sim.page.wait_for_function("window.PmSim !== undefined")
    assert sim.js("document.querySelector('#exSel').selectedOptions[0].textContent") == "Testiprojekti"
    sim.page.click("#wDel")
    sim.page.click("#wDel")
    assert sim.call("customs") == [] and sim.call("state")["ex"] == "ce"


def test_U09_kysely_estaa_virheet(sim):
    """Tuntematon edeltäjä, tuntematon resurssi ja silmukka estävät luonnin."""
    _wizard_project(sim)
    sim.page.fill('[data-wr="tasks"][data-i="2"][data-f="pred"]', "B, X")
    sim.page.fill('[data-wr="tasks"][data-i="3"][data-f="res"]', "ZZ:1")
    sim.page.click("#wNext")
    err = sim.js("document.querySelector('.werr').innerText")
    assert "X" in err and "ZZ" in err and sim.page.is_disabled("#wCreate")
    sim.page.click('[data-wgo="4"]')
    sim.page.fill('[data-wr="tasks"][data-i="2"][data-f="pred"]', "B")
    sim.page.fill('[data-wr="tasks"][data-i="3"][data-f="res"]', "PM:0.5")
    sim.page.fill('[data-wr="tasks"][data-i="0"][data-f="pred"]', "E")
    sim.page.click('[data-wgo="5"]')
    assert "silmukka" in sim.js("document.querySelector('.werr').innerText") and sim.page.is_disabled("#wCreate")


def test_U10_oma_projekti_vienti_ja_tuonti(sim):
    """Viety oma projekti tuodaan toiseen selaimeen ja lisätään projektivalikkoon."""
    _wizard_project(sim)
    sim.page.click("#wNext")
    sim.page.click("#wCreate")
    s = sim.call("serialize")
    sim.js("localStorage.clear()")
    sim.page.reload()
    sim.page.wait_for_function("window.PmSim !== undefined")
    assert sim.call("customs") == []
    sim.page.click("#jsonBtn")
    sim.page.fill("#jsonTa", s)
    sim.page.click("#jsonImp")
    assert [c["n"] for c in sim.call("customs")] == ["Testiprojekti"] and sim.call("schedule")["fin"] == 23
