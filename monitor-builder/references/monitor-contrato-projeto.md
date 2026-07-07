# Contrato do projeto — `contrato-cockpit.yml`

O contrato é o **único lugar** onde mora o que varia por cliente. Preencha-o no Passo 0 (com o operador) e use-o pra adaptar o gerador/renderer. Tudo aqui é exemplo preenchido com **Sigo ERP** — troque pelos valores do projeto-alvo.

> **Dois regimes.** A maioria dos blocos (`fontes`, `campanhas_cols`, `funil`, `tcv`, `design_system`) **guia a adaptação manual** do gerador/renderer no Passo 1 — viram código explícito. O bloco **`metas`** é **lido em runtime** por `load_meta()`: trocar a meta a cada quarter = editar só esse bloco, sem tocar no `.py` (o feed regenera com a meta nova). Requer `pyyaml` no ambiente do feed; sem ele, o gerador cai num `META_DEFAULT` embutido e avisa no stderr.

```yaml
projeto: sigo-erp

# --- Fontes do feed (nomes dos CSVs em dados-fonte/) ---
fontes:
  campanhas: campanhas-completo.csv     # diário por anúncio (sem PII)
  crm:       crm-completo.csv           # grão lead/deal (PII → git-ignored)
  termos:    termos-google-completo.csv # OPCIONAL (snapshot Google Search; some se ausente)
min_ano: 2024                            # descarta outliers de data pré-início

# --- Colunas do CSV de campanhas (coluna real → conceito) ---
campanhas_cols:
  data: Data
  canal: Canal
  campanha: Campanha
  conjunto: Conjunto
  anuncio: Anúncio
  investimento: Investimento
  conversao: MQL              # ATENÇÃO: no Sigo a coluna "MQL" JÁ é o SAL (evento de conversão)
  demo_agendada: Demo Agendada
  demo_realizada: Demo Realizada
  clientes: Novos Clientes
  faturamento: Faturamento
  impressoes: Impressões      # opcional/tolerante (acende quando a fonte preenche)
  cliques: Cliques            # opcional/tolerante

# --- Mapeamento CRM: etapa lógica → {flag booleano, campo de data} ---
# É O CORAÇÃO DA PARAMETRIZAÇÃO. Cada projeto nomeia suas etapas/campos diferente.
funil:
  lead:            {flag: null,               date: create_at}
  mql_operacional: {flag: sal,                date: sal_at}              # Sigo: MQL = SAL (SDR valida)
  sql:             {flag: sql,                date: sql_at}
  demo_agendada:   {flag: scheduled_meeting,  date: scheduled_meeting_at}
  demo_realizada:  {flag: show_meeting,       date: show_meeting_at}     # ★ ESTRELA (meta mensal)
  negociacao:      {flag: in_negotiation,     date: null}
  cliente:         {flag: win,                date: win_at}
  perdido:         {flag: lost,               date: null, reason: lost_reason}
  mql_form:        {flag: mql}                # qualificação automática do form (≠ conversão; mede qualidade da fonte)
join_ad_id: ad_id          # liga lead↔anúncio (campanhas é a verdade do CRM fatiada por anúncio)
canal_crm: canal           # canal do lead (paid/orgânico)
segmento: icm_product_map  # dimensão de segmento (Sigo: tier_tamanho vem vazio → usa este)

# --- Campos de valor (receita) ---
campos_valor:
  total_value:   total_value          # 1 mensalidade + implementação
  mensalidade:   value_mensalidade
  implementacao: value_implementação

# --- Métrica-estrela & metas OKR (por quarter) ---
estrela: demo_realizada
metas:                          # ↓ LIDO EM RUNTIME — trocar a cada quarter sem tocar no .py
  quarter_vigencia: "2026-Q2"   # quarter destas metas (AAAA-Qn); WARN se ≠ quarter corrente
  demos_real_mes: 100
  demos_agend_mes: 120
  sql_semana: 25
  clientes_q: 40
  valor_total_q: 100000
  budget_q: 50000
  taxas: {sal_sql: 0.50, show: 0.70, close: 0.20}
  baseline_q_anterior: {show: 0.60, close: 0.15, sal_sql: 0.40}

# --- TCV (fórmula de receita — varia por modelo de negócio) ---
tcv:
  modelo: recorrente                 # recorrente | one-shot
  formula: "tcv_meses * mensalidade + implementacao"  # Sigo: 6 meses (produto recorrente, sem LTV real)
  config_csv: config-financeiro.csv  # FEE/margem/tcv_meses por mês

# --- Identidade visual (DS do operador) ---
design_system: ../../00-sistema/design-system.css
fonte_titulo: Archivo                 # Sigo rejeitou Morganite/Montserrat
```

## Como cada chave vira código

| Chave do contrato | Onde no gerador/renderer |
|---|---|
| `fontes.*`, `min_ano` | paths e filtro de outlier no topo de `_gerar-monitor.py` |
| `campanhas_cols.*` | `load_campanhas()` (`r.get("<coluna>")`) |
| `funil.*` | parsing do CRM (flags + `_at`) no `build_payload` **e** as funções JS `funil`/`velocidade`/`pipelineAberto`/`cohort` |
| `metas.*`, `estrela` | **lido em runtime** por `load_meta()` → dict `META` + `compute_okr` + cards OKR. Troca de quarter = editar só este bloco (sem tocar `.py`). Requer `pyyaml`; fallback gracioso pro `META_DEFAULT` se ausente. `quarter_vigencia` → WARN no stderr se ≠ quarter corrente |
| `tcv.*` | função `tcvOf` (JS) + `config-financeiro.csv` + DRE |
| `join_ad_id`, `canal_crm`, `segmento` | join e dimensões no payload/JS |
| `design_system`, `fonte_titulo` | `<style>` e `@font-face`/Google Fonts no renderer |

## Perguntas obrigatórias do Passo 0 (se o operador não trouxe)

1. **Qual é o evento de conversão "MQL"?** (lead bruto? validado por SDR? qualificação do form?) — ler errado quebra tudo.
2. **Qual a métrica-estrela e a meta** (mensal/quarter)?
3. **Modelo de receita:** recorrente (qual N de meses pro TCV?) ou one-shot (= total_value)?
4. **Tem FEE de assessoria** pra DRE/breakeven/payback? Desde quando?
5. **Quais canais** existem e como normalizar (ex: gads→google)?
6. **Datas de meio-de-funil** estão preenchidas ou esparsas? (define o que é volume-via-flag vs timing-via-`_at`).

## Extensões validadas no Colina (2026-07-02) — blocos opcionais do contrato

Ver `exemplos/colina/contrato-cockpit.yml` (código real). Todos lidos em runtime:

```yaml
mes_fiscal:                 # calendário do cliente ≠ mês civil
  dia_inicio: 16            # mês 16→15
  nomeia_por: fim           # "julho" = 16/jun–15/jul (alternativa: inicio)

bu:                         # dimensão em multi-campo (regra N do data-realities)
  col: origem               # primário no CRM
  col_fallback: funnel      # quando o primário vier vazio

receita:                    # economia HÍBRIDA por BU (rec + tcv no mesmo cockpit)
  fonte: premissa           # premissa (valores da fundação) | crm (dado real)
  por_bu:
    "Plano SP": {modelo: recorrente, mensalidade: 110, ltv_meses: 18}
    "Jazigo":   {modelo: tcv, valor: 8000}   # contrato cheio mesmo parcelado

payback: {modo: midia}      # midia (sem FEE) | total (mídia + FEE)
retencao: {ativa: false, motivo: "sem dado de churn no feed"}

metas:                      # VIGÊNCIA CUSTOMIZADA (trimestre do cliente ≠ quarter civil — ex: Aquatro jul/2026)
  quarter_vigencia: "Q2/3 2026"   # rótulo livre quando não encaixa em AAAA-Qn
  vigencia_inicio: "2026-05-01"   # se ambos presentes, tomam prioridade sobre parse_quarter_key
  vigencia_fim: "2026-07-31"      # gerador: VSTART/VEND vêm daqui; renderer pro-rateia igual (metaPeriodo)
```

**Vigência customizada (gerador):** quando `metas.vigencia_inicio`/`vigencia_fim` existem, o
bloco de vigência usa essas datas em vez de `parse_quarter_key(quarter_vigencia)` — trimestre do
cliente que atravessa o quarter civil (ex: mai–jul, deadline 30/jul). O renderer não muda (já
pro-rateia pela interseção período×vigência). **Gotcha de default de período:** quando os dados
estão num quarter passado (fase inicial / histórico), o default `Este trimestre` abre o cockpit
VAZIO — troque o `FILT` default do renderer pra `Todo o período` (`ini:MINDATA,fim:P.hoje`).

**Perguntas extras do Passo 0 quando esses blocos entram:** o mês do cliente é civil ou
customizado (e nomeia pelo início ou fim)? · alguma BU é one-time (TCV) convivendo com
recorrentes? · o campo de receita do CRM está populado (senão: premissa de onde)? ·
existe canal indireto de recepção a ratear (regra M)? · semáforo de meta do operador
(thresholds + quais métricas são de custo → conta inversa)?
