# -*- coding: utf-8 -*-
"""
lib_kimball — primitivas testadas de consolidacao/cruzamento de dados marketing+CRM.

Biblioteca importada por consolidate.py (ou por scripts ad-hoc que a skill escreva).
Cada funcao materializa uma pratica validada (ver references/regras-aplicadas.md).
NAO contem logica de nenhum cliente especifico: so primitivas parametrizaveis.

Dependencias: pandas. (libphonenumber e opcional; ha fallback BR embutido.)
"""
import re, unicodedata
from datetime import datetime, date

# ─────────────────────────── NORMALIZACAO (boundary hardening) ──────────────────
# Regra: converter no boundary de ingestao; IDs viram string; nunca number-format em ID.

ROLE_LOCAL = {"info", "contato", "contact", "sac", "atendimento", "financeiro",
              "vendas", "comercial", "adm", "administrativo", "noreply", "no-reply",
              "faleconosco", "suporte", "marketing", "rh"}
_GMAIL = {"gmail.com", "googlemail.com"}

def n_email(s):
    """Email canonico (lowercase+trim SEMPRE; dots/+tag removidos SO no Gmail).
       Retorna (canonico, is_role_based). Aplicar regra global = bug de over-merge."""
    if s is None: return "", False
    s = str(s).strip().lower()
    if "@" not in s or "." not in s.rsplit("@", 1)[-1]:
        return "", False
    local, dom = s.rsplit("@", 1)
    role = local.split("+")[0] in ROLE_LOCAL
    if dom in _GMAIL:                         # provider-especifico
        local = local.split("+")[0].replace(".", "")
    else:
        local = local.split("+")[0]
    return f"{local}@{dom}", role

def n_phone(s, region="BR"):
    """Normaliza para E.164 (so digitos, com DDI). Fallback BR embutido.
       Tenta phonenumbers (libphonenumber) se instalado; senao heuristica BR."""
    if s is None: return ""
    raw = str(s).strip()
    if not raw: return ""
    try:
        import phonenumbers                    # opcional; melhor caminho
        try:
            p = phonenumbers.parse(raw, region)
            if phonenumbers.is_valid_number(p):
                return re.sub(r"\D", "", phonenumbers.format_number(
                    p, phonenumbers.PhoneNumberFormat.E164))
        except Exception:
            pass
    except ImportError:
        pass
    d = re.sub(r"\D", "", raw)                  # fallback determinístico BR
    if not d: return ""
    if region == "BR":
        if d.startswith("55") and len(d) in (12, 13): return d
        if len(d) in (10, 11): return "55" + d
    return d

def n_txt(s):
    return "" if s is None else str(s).strip()

def fold_key(s):
    """Chave de blocking: NFKD + fold de acentos + lowercase + colapso de espaco.
       Preserve SEMPRE o valor raw para exibicao — esta chave e so p/ match."""
    s = n_txt(s)
    if not s: return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()

def unslug(s):
    """'curso_de_gastronomia' -> 'curso de gastronomia' (valores de form despadronizados)."""
    s = n_txt(s)
    return re.sub(r"\s+", " ", s.replace("_", " ")).strip() if s else ""

def strip_id(s):
    """Remove prefixos de export de plataforma (ag:/c:/as:/l:/p:) e '+'. ID sempre string."""
    s = n_txt(s)
    return re.sub(r"^[a-z]+:", "", s).lstrip("+")

def to_num(s, locale="pt-BR"):
    """Parser numerico por LOCALE DECLARADO (nao inferido linha-a-linha).
       pt-BR: '1.234,56'->1234.56 ; en-US: '1,234.56'->1234.56 ; '' -> 0.0"""
    s = n_txt(s)
    if not s: return 0.0
    s = re.sub(r"[^\d,.\-]", "", s)
    if locale == "pt-BR":
        if "," in s: s = s.replace(".", "").replace(",", ".")
    else:  # en-US
        if "." in s: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def to_iso(s, fmt=None):
    """Data -> ISO 'YYYY-MM-DD'. Se fmt declarado, usa ele (recomendado); senao tenta comuns.
       Retorna date|None. Datas ambiguas (01/02/2026) EXIGEM fmt declarado por fonte."""
    s = n_txt(s)
    if not s: return None
    s = s.replace("T", " ").split(" ")[0]
    fmts = [fmt] if fmt else ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]
    for f in fmts:
        try: return datetime.strptime(s, f).date()
        except (ValueError, TypeError): continue
    try: return datetime.fromisoformat(s).date()
    except ValueError: return None

# ─────────────────────────── RESOLUCAO DE IDENTIDADE ────────────────────────────
# Fellegi-Sunter destilado: chave forte = exato pos-normalizacao. Union-find SO em
# aresta forte (email/phone exato). Guards anti-over-merge: telefone compartilhado,
# email role-based, hard-conflict (2 emails distintos ligados so por telefone).

class UnionFind:
    def __init__(self, n): self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[max(ra, rb)] = min(ra, rb)

def resolve_identity(records, shared_phone_min=3):
    """
    records: lista de dicts com 'email_canon' (str), 'email_role' (bool), 'phone' (str).
    Retorna: (labels, report) onde labels[i] = id do cluster de records[i].

    Regras (validadas):
      - Une por EMAIL canonico exato (aresta forte, sempre).
      - Une por TELEFONE exato SO se nao criar hard-conflict (2 emails distintos) e o
        telefone nao for compartilhado (usado por >= shared_phone_min emails distintos).
      - Email role-based (contato@/sac@) NUNCA e chave de uniao.
    """
    n = len(records)
    uf = UnionFind(n)
    # 1) mapear telefone -> conjunto de emails distintos (detecta compartilhado)
    phone_emails = {}
    for r in records:
        ph = r.get("phone", "")
        if ph:
            phone_emails.setdefault(ph, set())
            if r.get("email_canon"): phone_emails[ph].add(r["email_canon"])
    shared_phones = {p for p, es in phone_emails.items() if len(es) >= shared_phone_min}

    # 2) unir por email (forte)
    seen_email = {}
    for i, r in enumerate(records):
        e = r.get("email_canon", "")
        if e and not r.get("email_role"):
            if e in seen_email: uf.union(i, seen_email[e])
            else: seen_email[e] = i

    # 3) unir por telefone (com guards)
    seen_phone = {}
    blocked = 0
    for i, r in enumerate(records):
        ph = r.get("phone", "")
        if not ph or ph in shared_phones:
            continue
        if ph in seen_phone:
            j = seen_phone[ph]
            ei, ej = r.get("email_canon", ""), records[j].get("email_canon", "")
            if ei and ej and ei != ej:        # hard-conflict: emails distintos
                blocked += 1; continue
            uf.union(i, j)
        else:
            seen_phone[ph] = i

    labels = [uf.find(i) for i in range(n)]
    report = dict(records=n, clusters=len(set(labels)),
                  collapsed=n - len(set(labels)),
                  shared_phones=len(shared_phones), hard_conflicts_blocked=blocked)
    return labels, report

def survivorship(group_df, fields, recency_col=None):
    """Golden record por ATRIBUTO (nao por registro): para cada campo, valor do registro
       mais completo; coalesce com o 1o nao-vazio dos demais (ordem: completude, recencia).
       O 'registro vencedor raramente tem o melhor valor em todos os campos'."""
    def completeness(idx): return sum(1 for f in fields if str(group_df.at[idx, f]).strip())
    order = sorted(group_df.index,
                   key=lambda i: (completeness(i),
                                  group_df.at[i, recency_col] if recency_col else 0),
                   reverse=True)
    rep = {}
    for f in fields:
        val = ""
        for i in order:
            v = str(group_df.at[i, f]).strip()
            if v: val = v; break
        rep[f] = val
    return rep, order

# ─────────────────────────── FATO DE MIDIA (grao ad×dia) ────────────────────────

def aggregate_no_fanout(df, group_cols, sum_cols):
    """Colapsa sub-grao (ex: search-term) para o grao alvo somando metricas.
       Checa INVARIANTE nao-fan-out: SUM pos == SUM pre (tolerancia float)."""
    pre = {c: df[c].sum() for c in sum_cols}
    out = df.groupby(group_cols, as_index=False)[sum_cols].sum()
    for c in sum_cols:
        assert abs(out[c].sum() - pre[c]) < 1e-6, f"fan-out em {c}: {out[c].sum()} != {pre[c]}"
    return out

# ─────────────────────────── QA (6 dimensoes DAMA) ──────────────────────────────

def fill_rate(series):
    s = series.astype(str).str.strip()
    return round((s != "").sum() / max(len(s), 1), 4)

def qa_check(name, value, threshold, higher_is_better=True):
    """Retorna dict de check binario com veredito PASS/WARN/FAIL."""
    ok = value >= threshold if higher_is_better else value <= threshold
    warn = (threshold * 0.9 <= value < threshold) if higher_is_better else False
    return dict(check=name, value=value, threshold=threshold,
                verdict="PASS" if ok else ("WARN" if warn else "FAIL"))

def is_dead_column(series, min_fill=0.5):
    """Coluna 'morta': fill-rate < min_fill OU um unico valor distinto (ex: tudo FALSE).
       NAO usar como join/marco de funil sem confirmacao humana."""
    s = series.astype(str).str.strip()
    nonblank = s[s != ""]
    if len(nonblank) == 0: return True
    return fill_rate(series) < min_fill or nonblank.nunique() <= 1
