"""Kieliversioiden testit K01–K03."""
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
    assert ajo("fi") == ajo("en"), "K02: kieli vaikutti tulokseen"


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
