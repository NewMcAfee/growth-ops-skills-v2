# -*- coding: utf-8 -*-
"""
consolidate.py — orquestrador config-driven do kimball.

Le um config (YAML ou JSON) que mapeia as colunas de cada fonte -> schema canonico,
e produz: campanhas_consolidada.csv (fato midia ad×dia), leads_master.csv (funil/
accumulating snapshot 1 linha/lead), deals_higienizados.csv + deals_ganhos.csv (opc),
relatorio_qualidade.md (QA DAMA). Usa lib_kimball.

Uso:  py consolidate.py config.yml
Nada de cliente hardcoded aqui: tudo vem do config. Ver config.example.yml e
references/regras-aplicadas.md.
"""
import sys, json, re
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_kimball as K

def load_config(p):
    txt = Path(p).read_text(encoding="utf-8")
    if str(p).endswith((".yml", ".yaml")):
        try:
            import yaml; return yaml.safe_load(txt)
        except ImportError:
            sys.exit("PyYAML ausente. Rode:  py -m pip install pyyaml   (ou use config .json)")
    return json.loads(txt)

def rd(raw_dir, fname):
    """CSV como string pura (preserva IDs de 18 digitos)."""
    return pd.read_csv(Path(raw_dir) / fname, dtype=str, keep_default_na=False, na_values=[])

def main(cfg_path):
    cfg = load_config(cfg_path)
    base = Path(cfg_path).resolve().parent
    raw = (base / cfg["paths"]["raw_dir"]).resolve()
    out = (base / cfg["paths"]["out_dir"]).resolve(); out.mkdir(parents=True, exist_ok=True)
    rel = []
    def log(m): rel.append(m); print(m)

    # ══════════════ A) FATO DE MIDIA (grao ad×dia) ══════════════
    log("## A) Campanhas consolidada (grao ad×dia)\n")
    frames = []
    for src in cfg.get("media", []):
        df = rd(raw, src["file"]); m = src["map"]; loc = src.get("number_locale", "pt-BR")
        fmt = src.get("date_format")
        cur = pd.DataFrame({
            "date": df[m["date"]].map(lambda s: K.to_iso(s, fmt)),
            "ad_id": df[m["ad_id"]].map(K.strip_id),
            "canal": src["name"],
            "campaign": df[m.get("campaign", m["date"])].map(K.n_txt) if m.get("campaign") else "",
            "grupo": df[m["grupo"]].map(K.n_txt) if m.get("grupo") else "",
            "ad_name": df[m["ad_name"]].map(K.n_txt) if m.get("ad_name") else "",
            "spend": df[m["spend"]].map(lambda s: K.to_num(s, loc)),
            "impressions": df[m["impressions"]].map(lambda s: K.to_num(s, loc)),
            "clicks": df[m["clicks"]].map(lambda s: K.to_num(s, loc)),
        })
        for canon, col in src.get("extra_sum", {}).items():
            cur[canon] = df[col].map(lambda s: K.to_num(s, loc))
        if src.get("aggregate"):                       # grao sub (search-term) -> agrega
            sums = ["spend", "impressions", "clicks"] + list(src.get("extra_sum", {}))
            n0 = len(cur)
            cur = K.aggregate_no_fanout(cur, ["date", "ad_id", "canal", "campaign", "grupo", "ad_name"], sums)
            log(f"- {src['name']}: {n0} linhas (sub-grao) -> {len(cur)} (ad×dia) [invariante nao-fan-out OK]")
        frames.append(cur)
    if frames:
        campanhas = pd.concat(frames, ignore_index=True)
        campanhas = campanhas[campanhas["date"].notna()].sort_values(["date", "canal", "ad_id"])
        campanhas.to_csv(out / "campanhas_consolidada.csv", index=False, encoding="utf-8-sig")
        log(f"- consolidada: {len(campanhas)} linhas | " +
            " ".join(f"{k}={v}" for k, v in campanhas['canal'].value_counts().items()))
        log(f"- spend total: {campanhas['spend'].sum():,.2f} | ad_ids: {campanhas['ad_id'].nunique()}\n")
    else:
        campanhas = pd.DataFrame(columns=["ad_id"]); log("- (sem fontes de midia)\n")

    # ══════════════ B) LEADS: higienizar + resolver identidade ══════════════
    log("## B) Leads master (dedup por identidade)\n")
    lc = cfg["leads"]; m = lc["map"]; reg = cfg.get("identity", {}).get("region_default", "BR")
    tl = rd(raw, lc["file"])
    em = tl[m["email"]].map(K.n_email)
    base_df = pd.DataFrame({
        "nome": tl[m["nome"]].map(K.n_txt) if m.get("nome") else "",
        "email": tl[m["email"]].map(lambda s: K.n_email(s)[0]),
        "email_role": em.map(lambda t: t[1]),
        "phone": tl[m["phone"]].map(lambda s: K.n_phone(s, reg)),
        "dt": tl[m["date"]].map(lambda s: K.to_iso(s, lc.get("date_format"))),
    })
    for canon, col in lc.get("extra_map", {}).items():
        base_df[canon] = tl[col].map(K.unslug if canon in lc.get("unslug_fields", []) else K.n_txt)
    log(f"- todos_leads bruto: {len(base_df)} linhas")

    recs = [{"email_canon": base_df.at[i, "email"], "email_role": base_df.at[i, "email_role"],
             "phone": base_df.at[i, "phone"]} for i in base_df.index]
    labels, idrep = K.resolve_identity(recs, cfg.get("identity", {}).get("shared_phone_min", 3))
    base_df["_cluster"] = labels
    log(f"- resolucao de identidade: {idrep['records']} -> {idrep['clusters']} leads unicos "
        f"({idrep['collapsed']} colapsados) | tel. compartilhados ignorados: {idrep['shared_phones']} "
        f"| unioes bloqueadas por hard-conflict: {idrep['hard_conflicts_blocked']}")

    FIELDS = [c for c in base_df.columns if c not in ("email_role", "dt", "_cluster")]
    rows = []
    for cid, g in base_df.groupby("_cluster"):
        rep, order = K.survivorship(g, FIELDS, recency_col="dt")
        dts = [d for d in g["dt"] if d]
        rep["primeiro_contato"] = min(dts).isoformat() if dts else ""
        rep["ultima_interacao"] = max(dts).isoformat() if dts else ""
        rep["n_interacoes"] = len(g)
        rows.append(rep)
    leads = pd.DataFrame(rows)

    # ══════════════ C) CROSSWALK: platform_leads -> contatos -> deals ══════════════
    # C1) platform_leads (ex: form nativo) -> ad_id + canal
    if cfg.get("platform_leads"):
        pl = cfg["platform_leads"]; pm = pl["map"]; d = rd(raw, pl["file"])
        idx = {}
        for i in range(len(d)):
            e = K.n_email(d[pm["email"]].iat[i])[0] if pm.get("email") else ""
            ph = K.n_phone(d[pm["phone"]].iat[i], reg) if pm.get("phone") else ""
            cand = (K.to_iso(d[pm["created"]].iat[i]) if pm.get("created") else None,
                    K.strip_id(d[pm["ad_id"]].iat[i]),
                    K.n_txt(d[pm["campaign"]].iat[i]) if pm.get("campaign") else "")
            for k in (e, ph):
                if k and (k not in idx or (cand[0] and idx[k][0] and cand[0] > idx[k][0])):
                    idx[k] = cand
        def mp(r):
            for k in (r["email"], r["phone"]):
                if k and k in idx: return idx[k]
            return None
        mm = leads.apply(mp, axis=1)
        leads["is_platform"] = mm.map(lambda x: x is not None)
        leads["ad_id"] = mm.map(lambda x: x[1] if x else "")
        leads["platform_campaign"] = mm.map(lambda x: x[2] if x else "")
        leads["channel_platform"] = leads["is_platform"].map(lambda b: pl.get("channel", "paid_platform") if b else "")
        log(f"- match platform_leads ({pl.get('channel','paid_platform')}): {leads['is_platform'].sum()} / {len(leads)}")
    else:
        leads["is_platform"] = False; leads["ad_id"] = ""; leads["channel_platform"] = ""

    # C2) contatos -> contact_id
    contact_by = {}
    if cfg.get("crm_contacts"):
        cc = cfg["crm_contacts"]; cm = cc["map"]; c = rd(raw, cc["file"])
        for i in range(len(c)):
            e = K.n_email(c[cm["email"]].iat[i])[0] if cm.get("email") else ""
            ph = K.n_phone(c[cm["phone"]].iat[i], reg) if cm.get("phone") else ""
            cid = K.n_txt(c[cm["contact_id"]].iat[i])
            for k in (e, ph):
                if k and k not in contact_by: contact_by[k] = cid
        def mc(r):
            for k in (r["email"], r["phone"]):
                if k and k in contact_by: return contact_by[k]
            return ""
        leads["contact_id"] = leads.apply(mc, axis=1)
        log(f"- match contatos (contact_id): {(leads['contact_id']!='').sum()} / {len(leads)}")
    else:
        leads["contact_id"] = ""

    # C3) deals via contact_id  (+ deteccao de coluna de stage morta)
    if cfg.get("crm_deals"):
        dc = cfg["crm_deals"]; dm = dc["map"]; loc = dc.get("number_locale", "pt-BR")
        dd = rd(raw, dc["file"])
        stage = dd[dm["stage"]].map(K.n_txt)
        if K.is_dead_column(stage, dc.get("stage_fill_min", 0.5)):
            log(f"  ⚠️ ALERTA: coluna de stage '{dm['stage']}' parece MORTA "
                f"(fill/variacao baixa) — ganho/perda podem estar em outra coluna. Confirmar.")
        dd["_cid"] = dd[dm["contact_id"]].map(lambda s: K.strip_id(s).split(";")[0] if s else "")
        dd["_val"] = dd[dm["valor"]].map(lambda s: K.to_num(s, loc)) if dm.get("valor") else 0.0
        dd["_stage"] = stage
        won, lost = set(dc.get("won_values", [])), set(dc.get("lost_values", []))
        dd["_won"] = dd["_stage"].map(lambda s: s in won)
        dd["_lost"] = dd["_stage"].map(lambda s: s in lost)
        dd["_dt"] = dd[dm["created"]].map(lambda s: K.to_iso(s, dc.get("date_format"))) if dm.get("created") else None
        dd["_did"] = dd[dm["deal_id"]].map(K.n_txt)
        au = cfg.get("attribution", {}).get("crm_utm", {})       # UTMs do CRM p/ atribuicao
        dd["_uc"] = dd[au["campaign"]].map(K.n_txt) if au.get("campaign") in dd.columns else ""
        dd["_us"] = dd[au["source"]].map(K.n_txt) if au.get("source") in dd.columns else ""
        dd["_um"] = dd[au["medium"]].map(K.n_txt) if au.get("medium") in dd.columns else ""
        deals_by = {}
        for i in range(len(dd)):
            c = dd["_cid"].iat[i]
            if c: deals_by.setdefault(c, []).append(i)
        def agg(cid):
            if not cid or cid not in deals_by:
                return dict(n_deals=0, valor_total=0.0, status_deal="", tem_ganho=False,
                            tem_perda=False, valor_ganho=0.0, deal_ids="",
                            d_utm_camp="", d_utm_src="", d_utm_med="")
            ix = sorted(deals_by[cid], key=lambda i: dd["_dt"].iat[i].isoformat() if dd["_dt"].iat[i] else "",
                        reverse=True)
            recent = ix[0]
            won_ = any(dd["_won"].iat[i] for i in ix); lost_ = any(dd["_lost"].iat[i] for i in ix)
            return dict(n_deals=len(ix), valor_total=round(sum(dd["_val"].iat[i] for i in ix), 2),
                        status_deal="ganho" if won_ else "perdido" if lost_ else "aberto",
                        tem_ganho=won_, tem_perda=lost_,
                        valor_ganho=round(sum(dd["_val"].iat[i] for i in ix if dd["_won"].iat[i]), 2),
                        deal_ids=";".join(dd["_did"].iat[i] for i in ix),
                        d_utm_camp=dd["_uc"].iat[recent], d_utm_src=dd["_us"].iat[recent],
                        d_utm_med=dd["_um"].iat[recent])
        leads = pd.concat([leads, leads["contact_id"].map(agg).apply(pd.Series)], axis=1)
        log(f"- match deals: {(leads['n_deals']>0).sum()} c/ negocio | ganho={(leads['tem_ganho']).sum()} "
            f"perdido={(leads['tem_perda']).sum()} | valor ganho {leads['valor_ganho'].sum():,.2f}")
        if dc.get("emit_hygienized"):
            dh = pd.DataFrame({"deal_id": dd["_did"], "contact_id": dd["_cid"], "valor": dd["_val"],
                               "stage": dd["_stage"],
                               "status": dd.apply(lambda r: "ganho" if r["_won"] else "perdido" if r["_lost"] else "aberto", axis=1),
                               "data_criacao": dd["_dt"].map(lambda d: d.isoformat() if d else "") if dm.get("created") else ""})
            dh.to_csv(out / "deals_higienizados.csv", index=False, encoding="utf-8-sig")
            dh[dh["status"] == "ganho"].to_csv(out / "deals_ganhos.csv", index=False, encoding="utf-8-sig")
            log(f"- deals_higienizados: {len(dh)} | deals_ganhos: {(dh['status']=='ganho').sum()}")

    # ══════════════ D) ATRIBUICAO (utm_source enriquecido, config-driven) ══════════════
    # Precedencia: (1) match em plataforma -> (2) UTM do CRM -> (3) nome de campanha no
    # lead -> (4) default. Regras de canal vem do config (regex por nome), NAO hardcoded.
    att = cfg.get("attribution", {})
    rules = att.get("channel_rules", [])
    paid_meds = {m.lower() for m in att.get("paid_mediums", ["cpc", "paid", "ppc"])}
    name_fields = [f for f in att.get("lead_name_fields", []) if f in leads.columns]
    default_src = att.get("default", "indefinido")
    # auto-heal footgun YAML: "\b" em aspas-duplas vira BACKSPACE (\x08) -> restaura word-boundary
    comp = [(re.compile(r["pattern"].replace("\x08", r"\b"), re.I), r["channel"]) for r in rules]

    def infer(*names):
        blob = " ".join(str(n).upper() for n in names if n)
        for rx, ch in comp:
            if rx.search(blob): return ch
        return ""
    def first_name(r):
        for f in name_fields:
            if str(r.get(f, "")).strip(): return r[f]
        return ""
    def attribute(r):
        if r.get("channel_platform"):                        # 1) match em plataforma (form)
            return pd.Series([r["channel_platform"],
                              r.get("platform_campaign", "") or first_name(r), "platform_match"])
        duc, dus = r.get("d_utm_camp", ""), r.get("d_utm_src", "")
        dum = str(r.get("d_utm_med", "")).lower()
        if duc or dus or dum:                                # 2) UTM do CRM (deal)
            ch = infer(duc, *[r.get(f, "") for f in name_fields])
            if not ch and dum in paid_meds: ch = "paid_" + (dus.lower() or "outro")
            if ch: return pd.Series([ch, duc or first_name(r), "deals_utm"])
        ch = infer(*[r.get(f, "") for f in name_fields])     # 3) nome de campanha no lead
        if ch: return pd.Series([ch, first_name(r), "lead_name"])
        return pd.Series([default_src, "", "none"])          # 4) indefinido

    leads[["utm_source", "campaign_atribuida", "attribution_source"]] = leads.apply(attribute, axis=1)
    leads.to_csv(out / "leads_master.csv", index=False, encoding="utf-8-sig")
    log("\n### Canal (utm_source):")
    for k, v in leads["utm_source"].value_counts().items(): log(f"- {k}: {v}")
    log("### Fonte da atribuicao:")
    for k, v in leads["attribution_source"].value_counts().items(): log(f"- {k}: {v}")

    # ══════════════ E) QA REPORT (6 dimensoes DAMA, threshold binario) ══════════════
    log("\n## QA — dimensoes DAMA\n")
    checks = []
    nb = leads.loc[leads["email"] != "", "email"]
    checks.append(K.qa_check("uniqueness: email unico por lead (pos-dedup)",
                             round(nb.nunique() / max(len(nb), 1), 4), 1.0))
    # completeness das chaves criticas
    for col, thr in [("email", 0.95), ("phone", 0.95)]:
        if col in leads: checks.append(K.qa_check(f"completeness: {col}", K.fill_rate(leads[col]), thr))
    if "ad_id" in leads and len(campanhas):
        la = set(leads.loc[leads["ad_id"] != "", "ad_id"]); ca = set(campanhas["ad_id"])
        integ = round(len(la & ca) / max(len(la), 1), 4)
        checks.append(K.qa_check("accuracy: ad_id de lead casa em campanhas (join integrity)", integ, 0.99))
    for c in checks:
        log(f"- [{c['verdict']}] {c['check']}: {c['value']:.2%} (min {c['threshold']:.0%})")

    (out / "relatorio_qualidade.md").write_text(
        "# Relatorio de qualidade — kimball\n\n" + "\n".join(rel), encoding="utf-8")
    print("\nOK -> leads_master.csv, campanhas_consolidada.csv, relatorio_qualidade.md")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit("uso: py consolidate.py <config.yml>")
    main(sys.argv[1])
