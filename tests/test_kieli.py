"""Kieliversioiden testit K01–K05 (suomi, englanti, saksa)."""
API_NAME = "PmSim"
import re
from conftest import INDEX

SALLITUT = ("Seinäjoki", "JSON-muodossa")


def _fi_rivit(text):
    return [l for l in text.split("\n") if re.search("[äöÄÖ]", l) and not any(s in l for s in SALLITUT)]


def test_K01_englanninkieliset_tekstit_kattavat(sim):
    """Englanninkielisessä näkymässä ei ole suomenkielisiä rivejä millään välilehdellä, esimerkillä, ohjeessa eikä kyselyssä."""
    sim.call("setLang", "en")
    for ex in [e["id"] for e in sim.call("examples")]:
        sim.call("loadExample", ex)
        for tab in ["gantt", "net", "res", "evm", "mc", "ex"]:
            sim.call("setTab", tab)
            sim.page.wait_for_timeout(40)
            left = _fi_rivit(sim.js("document.body.innerText"))
            assert not left, f"K01 ({ex}/{tab}): suomenkielistä tekstiä: {left[:5]}"
    sim.js("document.querySelector('#helpBtn').click()")
    left = _fi_rivit(sim.js("document.querySelector('#mbox').innerText"))
    assert not left, f"K01: suomea ohjeikkunassa: {left[:5]}"
    sim.js("document.querySelector('#modal').classList.remove('open')")
    sim.call("openWizard", "empty")
    for step in range(6):
        sim.js(f"document.querySelector('[data-wgo=\"{step}\"]').click()")
        left = _fi_rivit(sim.js("document.querySelector('#mbox').innerText"))
        assert not left, f"K01: suomea kyselyn vaiheessa {step + 1}: {left[:5]}"


def test_K02_kielen_vaihto_ei_vaikuta_tuloksiin(sim):
    def ajo(l):
        sim.call("setLang", l)
        sim.call("loadExample", "sw")
        s = sim.call("schedule")
        return s["fin"], round(s["total"], 6), s["chain"]
    assert ajo("fi") == ajo("en") == ajo("de"), "K02: kieli vaikutti tulokseen"


def test_K03_url_parametri(browser):
    page = browser.new_page()
    page.goto(INDEX.as_uri() + "?lang=en")
    page.wait_for_function("window.PmSim !== undefined")
    assert page.evaluate("PmSim.lang()") == "en"
    assert page.inner_text("#helpBtn") == "Help"
    page.goto(INDEX.as_uri() + "?lang=fi")
    page.wait_for_function("window.PmSim !== undefined")
    assert page.evaluate("PmSim.lang()") == "fi"
    assert page.inner_text("#helpBtn") == "Ohje"
    page.evaluate("localStorage.clear()")
    page.close()


# ---------- Saksa (DE) ----------
DE_SALLITUT = {'Status', 'TCPI (BAC)', 'SPI = EV / PV', 'Feedback', 'CPI = EV / AC', 'Name'}
DE_NAKYMAT = [
 "",
 "PmSim.setTab('net')",
 "PmSim.setTab('res')",
 "PmSim.setTab('evm')",
 "PmSim.setTab('mc')",
 "PmSim.setTab('ex')",
 "PmSim.setTab('ex');document.querySelectorAll('.ex').forEach(e=>{const i=e.querySelector('input');if(i){i.value='1';i.dispatchEvent(new Event('input',{bubbles:true}));}e.querySelector('[data-chk]').click();});document.querySelectorAll('.ex details').forEach(d=>d.open=true)",
 "PmSim.loadExample('robo');PmSim.setTab('gantt')",
 "PmSim.loadExample('halli');PmSim.setTab('evm')",
 "PmSim.loadExample('tki');PmSim.setTab('net')",
 "PmSim.loadExample('sw');PmSim.setTab('gantt')",
 "PmSim.loadExample('sw');PmSim.setTab('ex');document.querySelectorAll('.ex').forEach(e=>{const i=e.querySelector('input');if(i){i.value='1';i.dispatchEvent(new Event('input',{bubbles:true}));}e.querySelector('[data-chk]').click();});document.querySelectorAll('.ex details').forEach(d=>d.open=true)",
 "PmSim.loadExample('ce');PmSim.loadScenario();PmSim.setTab('evm')",
 "PmSim.loadExample('ce');PmSim.level();PmSim.setTab('res')",
 "document.querySelector('#helpBtn').click()",
 "document.querySelector('#modal').classList.remove('open');document.querySelector('#jsonBtn').click()",
 "document.querySelector('#modal').classList.remove('open');PmSim.openWizard('empty')",
 "PmSim.openWizard('empty');document.querySelector('[data-wgo=\"1\"]').click()",
 "PmSim.openWizard('empty');document.querySelector('[data-wgo=\"2\"]').click()",
 "PmSim.openWizard('empty');document.querySelector('[data-wgo=\"3\"]').click()",
 "PmSim.openWizard('empty');document.querySelector('[data-wgo=\"4\"]').click()",
 "PmSim.openWizard('empty');document.querySelector('[data-wgo=\"5\"]').click()",
 "PmSim.openWizard('copy');document.querySelector('[data-wgo=\"5\"]').click()",
 "document.querySelector('#modal').classList.remove('open');document.querySelector('#palauteBtn').click()",
 "document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'));PmSim.setTab('gantt')"
]


def _rivit(page):
    return page.evaluate("""(()=>{const out=[];const add=t=>t.split('\\n').map(x=>x.trim()).filter(x=>x&&/[A-Za-zÄÖÜäöüß]{3,}/.test(x)).forEach(x=>out.push(x));
      add(document.body.innerText);return out;})()""")


def test_K04_saksankieliset_tekstit_kattavat(sim):
    """Saksankielisessä näkymässä ei ole suomen- tai englanninkielisiä rivejä: jokainen rivi, joka eroaa suomen ja englannin välillä, on käännetty."""
    jaljella = {}
    for js in DE_NAKYMAT:
        T = {}
        for l in ("fi", "en", "de"):
            sim.call("setLang", l)
            sim.page.wait_for_timeout(100)  # piirtosilmukka päivittää lukemat seuraavalla kehyksellä
            if js:
                sim.js(js)
                sim.page.wait_for_timeout(150)
            T[l] = _rivit(sim.page)
        fi, en = set(T["fi"]), set(T["en"])
        for x in T["de"]:
            if x in DE_SALLITUT or x.split('\t')[0] in DE_SALLITUT:
                continue
            if (x in en and x not in fi) or (x in fi and x not in en):
                jaljella.setdefault(x, js or "alku")
    assert not jaljella, f"K04: kääntämättömiä rivejä saksankielisessä näkymässä: {list(jaljella.items())[:8]}"


def test_K05_saksa_ei_vaikuta_tuloksiin_ja_url(browser):
    """?lang=de avaa saksankielisen näkymän; kielivalitsimessa on DE."""
    page = browser.new_page()
    page.goto(INDEX.as_uri() + "?lang=de")
    page.wait_for_function(f"window.{API_NAME} !== undefined")
    assert page.evaluate(f"{API_NAME}.lang()") == "de"
    assert page.evaluate("document.documentElement.lang") == "de"
    assert page.locator('.langsw [data-lang="de"]').count() == 1
    page.evaluate("localStorage.clear()")
    page.close()
