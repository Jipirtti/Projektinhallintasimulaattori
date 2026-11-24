"""Riippumaton viitelaskenta Pythonilla (ei käytä simulaattorin koodia).

Kriittisen polun menetelmä (CPM) lasketaan relaksaatiolla: aikaisimmat ajat kasvavat ja myöhäisimmät
pienenevät, kunnes yksikään riippuvuusehto ei muutu. Menetelmä ei tarvitse topologista järjestystä,
joten se on toteutustavaltaan eri kuin simulaattorin Kahnin algoritmiin perustuva laskenta.
Riippuvuusehdot (ES = aikaisin alku, EF = ES + kesto, lag = viive):
  LA/FS: ES_j >= EF_i + lag      AA/SS: ES_j >= ES_i + lag
  LL/FF: EF_j >= EF_i + lag      AL/SF: EF_j >= ES_i + lag
"""
import math
import re

TYPES = {"FS": "FS", "SS": "SS", "FF": "FF", "SF": "SF", "LA": "FS", "AA": "SS", "LL": "FF", "AL": "SF"}


def parse_pred(s):
    out = []
    for tok in re.split(r"[,;]", s or ""):
        tok = tok.strip()
        if not tok:
            continue
        m = re.match(r"^([A-Za-z0-9_]+)(?:\s+([A-Za-z]{2}))?\s*([+-]\s*\d+)?$", tok)
        assert m, f"tunnistamaton riippuvuus {tok}"
        out.append((m.group(1).upper(), TYPES[(m.group(2) or "FS").upper()], int(m.group(3).replace(" ", "")) if m.group(3) else 0))
    return out


def parse_res(s):
    o = {}
    for part in (s or "").split(","):
        if not part.strip():
            continue
        r, _, u = part.partition(":")
        o[r.strip()] = float(u) if u else 1.0
    return o


def network(defn, dev=None):
    """Palauttaa (ids, kesto, edeltäjät, aloitusviive) esimerkin määrittelystä ja poikkeamista."""
    dev = dev or {}
    ids = [t[0] for t in defn["t"]]
    D = {t[0]: max(0, t[3] + dev.get(t[0], {}).get("extra", 0)) for t in defn["t"]}
    P = {t[0]: parse_pred(t[6]) for t in defn["t"]}
    slip = {i: dev.get(i, {}).get("slip", 0) for i in ids}
    return ids, D, P, slip


def cpm(defn, dev=None):
    ids, D, P, slip = network(defn, dev)
    ES = {i: 0.0 for i in ids}
    for _ in range(len(ids) + 2):
        changed = False
        for j in ids:
            v = 0.0
            for i, typ, lag in P[j]:
                v = max(v, {"FS": ES[i] + D[i] + lag, "SS": ES[i] + lag,
                            "FF": ES[i] + D[i] + lag - D[j], "SF": ES[i] + lag - D[j]}[typ])
            v += slip[j]
            if v != ES[j]:
                ES[j], changed = v, True
        if not changed:
            break
    EF = {i: ES[i] + D[i] for i in ids}
    fin = max(EF.values())
    S = {i: [] for i in ids}
    for j in ids:
        for i, typ, lag in P[j]:
            S[i].append((j, typ, lag))
    LF = {i: fin for i in ids}
    for _ in range(len(ids) + 2):
        changed = False
        for i in ids:
            v = fin
            for j, typ, lag in S[i]:
                LSj = LF[j] - D[j]
                v = min(v, {"FS": LSj - lag, "SS": LSj - lag + D[i], "FF": LF[j] - lag, "SF": LF[j] - lag + D[i]}[typ])
            if v != LF[i]:
                LF[i], changed = v, True
        if not changed:
            break
    LS = {i: LF[i] - D[i] for i in ids}
    TF = {i: LS[i] - ES[i] for i in ids}
    FF = {}
    for i in ids:
        if not S[i]:
            ff = fin - EF[i]
        else:
            ff = min({"FS": ES[j] - (EF[i] + lag), "SS": ES[j] - (ES[i] + lag),
                      "FF": EF[j] - (EF[i] + lag), "SF": EF[j] - (ES[i] + lag)}[typ] for j, typ, lag in S[i])
        FF[i] = max(0.0, min(ff, TF[i]))
    return {"ids": ids, "D": D, "ES": ES, "EF": EF, "LS": LS, "LF": LF, "TF": TF, "FF": FF, "fin": fin}


def costs(defn, dev=None):
    """Tehtävän kustannus = Σ yksiköt · kesto · h/pv · €/h + kiinteä kustannus."""
    ids, D, _, _ = network(defn, dev)
    rate = {r[0]: r[4] for r in defn["res"]}
    out = {}
    for t in defn["t"]:
        lab = sum(u * D[t[0]] * defn["hpd"] * rate[r] for r, u in parse_res(t[7]).items())
        out[t[0]] = lab + t[8]
    return out


def frac(es, d, t):
    if d <= 0:
        return 1.0 if t >= es else 0.0
    return min(1.0, max(0.0, (t - es) / d))


def evm(defn, dev, status):
    """Ansaittu arvo: perustaso = poikkeamaton suunnitelma, valmiusaste nykyisen aikataulun mukaan."""
    b, bc = cpm(defn), costs(defn)
    c, cc = cpm(defn, dev), costs(defn, dev)
    acf = {i: dev.get(i, {}).get("acf", 1.0) for i in b["ids"]}
    PVb = lambda t: sum(bc[i] * frac(b["ES"][i], b["D"][i], t) for i in b["ids"])
    PV = PVb(status)
    EV = sum(bc[i] * frac(c["ES"][i], c["D"][i], status) for i in b["ids"])
    AC = sum(cc[i] * frac(c["ES"][i], c["D"][i], status) * acf[i] for i in b["ids"])
    BAC = sum(bc.values())
    lo, hi = 0.0, b["fin"]
    if EV >= PVb(hi) - 1e-9:
        es = hi
    else:
        for _ in range(60):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if PVb(m) < EV else (lo, m)
        es = lo
    return {"BAC": BAC, "PV": PV, "EV": EV, "AC": AC, "SPI": EV / PV, "CPI": EV / AC, "ESt": es,
            "SPIt": es / status, "EAC": BAC / (EV / AC), "fin": c["fin"], "bfin": b["fin"]}


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))
