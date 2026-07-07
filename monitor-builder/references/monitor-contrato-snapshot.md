# Contrato do snapshot — `monitor.json`

O gerador (`_gerar-monitor.py`) emite, junto do `monitor.html`, um **`monitor.json`** com o **mesmo payload `P`** que alimenta o HTML — a versão **consumível por máquina** do cockpit. É o ponto de integração entre a `cockpit-builder` (que **produz** o dado, deterministicamente, no feed diário, sem LLM) e skills de **análise** que o **consomem** (ex.: growth-review / diagnóstico causal de funil).

**Princípio de fronteira:** a `cockpit-builder` não analisa — ela entrega dado estruturado fresco. A skill consumidora lê `monitor.json` como **path canônico**; se não existe, é erro upstream (o feed/gerador não rodou). Nenhuma skill de análise recomputa o cockpit — ela parte do snapshot.

## Propriedades

- **Path:** `<dados-fonte>/monitor.json`, ao lado do `monitor.html`.
- **Git-ignored:** embute comportamento do CRM (campos analíticos, sem PII direta — mesma política do HTML). Nunca commitar.
- **Frescor:** regenerado a cada execução do feed (diário). `freshness` carimba a geração e a última linha de cada fonte.
- **Encoding:** UTF-8, `ensure_ascii=false` (acentos preservados em nomes de campanha/segmento).

## Schema (chaves de topo de `P`)

| Chave | Tipo | Conteúdo |
|---|---|---|
| `freshness` | obj | `{gerado, crm_ate, camp_ate}` — timestamp da geração + última data de cada fonte |
| `quarter` | obj | `{label, ini, fim, elapsed, days, start, end, ano}` — janela do quarter corrente |
| `hoje` | str | data da geração (ISO) |
| `meta` | obj | metas OKR vigentes + `quarter_vigencia` (origem: `contrato-cockpit.yml`) |
| `alvos` | obj | `{custo_demo, cac}` derivados de `budget_q ÷ meta` |
| `okr` | obj | placar **calendário** pré-computado (abaixo) |
| `camp` | obj | mídia **granular** por dia×anúncio, interned |
| `leads` | obj | CRM **granular** por lead, interned, só campos analíticos |
| `fin` | obj | config DRE por mês (`config-financeiro.csv`) |
| `termos` | obj/null | termos de busca Google (agregado) — `null` se a fonte não existe |

### `okr` — placar calendário, pré-computado
Leitura **mês-calendário**: conta eventos cujo `_at` cai no quarter. Cada métrica de volume vem como `pace`: `{real, meta, pct, proj, proj_pct}` (`proj` = projeção proporcional ao dia decorrido). Taxas (`q_show`, `q_close`, `q_salsql`) vêm `{real, meta, q1}`.

### `camp` / `leads` — granular interned
Formato `{<listas-interned>, cols:[...], rows:[[...]]}`. O consumidor reconstrói objetos casando `cols` com cada `row`; índices (`camp`, `conj`, `anun`, `icm`, `reason`) resolvem nas listas. `leads.cols`: `canal, icm, create_at, sal, sal_at, sql, sql_at, mqlform, sched_at, show_at, win, win_at, lost, reason, value, neg, mens, impl`.

## Duas leituras do funil (calendário × safra)

O `okr` é **calendário** (a leitura que a meta cobra). Para **causa-raiz de mídia**, o consumidor deriva a **safra (coorte)** do granular `leads.rows`:

- **Calendário** (já em `okr`): "quantas demos aconteceram no mês" — conta por `show_at` na janela. É o que a meta exige.
- **Safra/coorte** (derivar): agrupa leads por `create_at` (mês de entrada) e segue cada coorte pelas etapas — liga o investimento da safra ao resultado que ele gerou. É o que atribui mídia corretamente (a demo de hoje veio de um lead de semanas atrás; misturar coortes contamina o diagnóstico).

**Regra de derivação** (de `data-realities.md` §A): **volume via flag, timing via `_at`**. Conte a etapa pelo flag (`sal`, `sql`, `win`… — completos); use `_at` só para tempo-de-ciclo/janela e **exiba o `n`** (os `_at` são esparsos). Nunca conte volume por `_at` (subconta).

> **Por que a safra não é pré-computada no JSON:** o granular é a fonte única, e a tela **Safra** do HTML já agrega no JS (`cohort()`). Pré-computar no Python duplicaria a lógica e engessaria as dimensões da coorte. O consumidor deriva o recorte de que precisar.

## Política PII
`leads` carrega só campos analíticos (datas/flags/valores/segmento/canal). **Zero** nome/email/telefone/CNPJ. Ainda assim o `monitor.json` é **git-ignored** (embute comportamento do CRM). A skill consumidora trata o arquivo como sensível e nunca o reexporta com PII.

## Variante Colina (2026-07-02): snapshot agregado + bloco anexado pelo renderer

O schema acima descreve o padrão Sigo (payload `P` completo interned). O **Colina**
usa um `monitor.json` **agregado** (`okr_total`/`okr_por_bu` com receita premissa +
`por_canal`) emitido pelo gerador, e o **renderer anexa** depois o bloco
`funil_atribuido_campanha_mes` (linhas campanha×mês fiscal×BU×canal: investimento,
impressões, cliques, mql, sql, clientes, cac — com a MESMA atribuição do drill do HTML).

**Princípio:** quem computa a visão anexa o dado analítico ao snapshot — zero
duplicação de motor entre `_gerar-monitor.py` e `_render_monitor.py`. O wrapper roda
gerar→render em sequência, então o bloco sobrevive a toda rodada do feed. O schema do
`monitor.json` é **por projeto** (documente no mapa.md da dados-fonte do cliente);
o invariante é: skills de análise consomem o JSON, nunca parseiam o HTML.
