# Regras de dado — as lições que evitam retrabalho

Cada regra abaixo nasceu de um problema real (Sigo jun/2026 · Martins jun/2026 · Colina jul/2026) ou de best-practice validada. São os pontos onde um builder ingênuo erra.

## A. Volume via flag, timing via `_at`
Em CRM real, os campos de **data de etapa** (`sal_at`, `sql_at`, `scheduled_meeting_at`…) vêm **esparsos** (só preenchidos pra parte dos registros), enquanto os **flags booleanos** (`sal`, `sql`, `win`…) estão completos.
- **Contagem de etapa (volume)** → use o **flag**.
- **Tempo-de-ciclo / pace temporal** → use o `_at`, e **exiba o `n`** (tamanho da amostra) pra não enganar.
- No filtro por período de uma etapa: `inR(l.<etapa>_at || l.create_at, a, b)` — cai pro `create_at` quando a data da etapa falta.
- NUNCA conte volume por `_at` (subconta).
- **Caso extremo — `_at` 100% vazios** (ex: Aquatro jul/2026: `win_at`/`sql_at`/`mql_at` vêm vazios, só o flag booleano preenchido): a âncora `create_at` precisa ir também no **gerador Python**, não só no JS — em `compute_okr`, `compute_resid` e nas vendas atribuídas (`vend_rows`), conte por flag com `pdate(_at) or pdate(create_at)`. Sintoma de esquecer: OKR/reconciliação mostram "0 clientes / 0 demos" com o CRM tendo ganhos. Emita a data já ancorada no payload (`iso(pdate(_at) or (_cda if istrue(flag) else None))`) pra o JS herdar a âncora sem recalcular.

## B. Outliers de data → `MIN_ANO`
Bases completas trazem lixo (ex: linhas com data de 1999). Descarte no parsing: `if d.year < MIN_ANO: continue` (campanhas) e pula leads com `create_at` pré-`MIN_ANO`. `MIN_ANO` = ano de início real do projeto (do contrato).

## C. Colunas opcionais tolerantes
Impressões/Cliques/CPM/CTR e o CSV de termos **chegam depois** (a fonte passa a preencher). Leia com fallback (`r.get("Impressões") or 0`); a feature **acende sozinha** quando o dado existe (ex: `hasImpr = any(impr>0)`), e a seção **some** se o arquivo não existe (`if not TERMS.exists(): return None` → JS condiciona a render). Nunca quebre por coluna ausente.

## D. Receita faltante ≠ prejuízo
Se o campo de receita (ex: `value_mensalidade`) está vazio num período (não havia tracking), o DRE daquele mês mostra **"s/ receita" mudo**, NÃO "Faltou R$X" (que parece prejuízo). Sinalize o backfill. Regra: `norev = (tcv==0 && deals>0)`.

## E. Normalização de canal
A fonte mistura rótulos (`paid_google`, `gads`, `GADS`; `paid_meta`, `facebook`, `ig`). Normalize: `gads|google→google`, `fb|ig|instagram|facebook|meta→meta`. A lista de canais do filtro é **derivada do dado** (distinct com volume ≥ N) → genérico pra N canais.

## F. Drill só mídia paga
No drill campanha→conjunto→anúncio, **filtre `inv>0`** — bases completas trazem fontes orgânicas (direct/blog/seo) como "campanhas" com R$0, que poluem.

## G. Termos = snapshot
O relatório de termos de busca é **agregado sem data** → a seção **independe dos filtros de tempo** (rotule isso). Veredito por termo: `0 conv + custo ≥ limiar → negativar`; `conv>0 & CP-conv ≤ média → escalar`. Não duplique `darwin` (análise profunda fica lá).

## H. PII nunca no HTML
Payload de leads carrega só campos analíticos (datas/flags/valores/segmento/canal). Zero identificadores diretos. O HTML ainda fica **git-ignored** por embutir comportamento do CRM.

## I. Cohort-payback (best-practice SaaS 2025)
- Triângulo de maturação: linhas=safra (mês de entrada), colunas M0…Mn (meses desde entrada), célula=métrica acumulada (conversão/CAC/receita/tempo). `·` = mês não decorrido.
- **CAC cai conforme a safra matura** (mais clientes sobre o mesmo investimento) — esperado, não bug.
- **M0–M2 conversão < 75%** (ou o equivalente do projeto) → a camada Decisão prioriza **consertar o funil antes de escalar CAC** (adicionar lead em funil furado estende payback).
- Payback = resultado acumulado ≥ 0 desde o início; benchmark de referência ~16 meses (mediana SaaS 2025) — não trate vermelho como falha sem olhar a janela.

## J. Vereditos acionáveis (Cortar/Escalar/Investigar)
Alvos derivados do contrato: `alvo_custo_demo = budget_q / meta_demos_q`; `alvo_cac = budget_q / meta_clientes_q`. Regras: gasto relevante + 0 resultado → Cortar; CAC ≤ alvo + volume → Escalar; CP subindo 28d-vs-28d → Investigar. Ignore `inv < 200` (ruído).

## K. Receita 100% vazia → PREMISSA declarada (Colina)
Diferente de D (receita faltante em parte do período): quando o campo de receita está vazio em **todos** os ganhos, não deixe o monitor sem economia — use **valores-premissa da fundação do cliente** (ticket/mensalidade/LTV documentados), declarados no contrato (`receita.fonte: premissa`) e com **selo `PREMISSA` visível** em toda métrica derivada. Rota de troca: quando o backfill chegar, `fonte: premissa → crm` sem tocar código.

## L. Métrica impossível na origem (Colina)
Fontes reais entregam inconsistência dura (ex.: 9 anúncios com **cliques > impressões** no bd_ads — mistura de all-clicks vs link-clicks). Regra: **exiba "—"** na métrica derivada impossível (CTR>100%) e **reporte ao dono do pipeline de dado**; nunca imprima o número (mina a confiança no monitor inteiro) nem conserte silenciosamente na ponta.

## M. Canal indireto rateável (Colina)
Canal "de recepção" (ex. `manual_zendesk`) que na verdade é demanda gerada pelos pagos **não é canal de aquisição** — rateie entre os canais pagos pela **taxa observada dos leads rastreáveis** (por segmento/BU; fallback global; fallback 50/50). Determinístico no grão registro (streaming proporcional), fracionário nos agregados. Sem isso, o CAC dos pagos infla e o canal fantasma esconde um terço da máquina.

## N. Dimensão em multi-campo (Colina)
Quando a mesma dimensão existe em 2 colunas do CRM (ex. BU em `origem` E `funnel`), trave com o operador **qual é primária e qual é fallback** e centralize numa função única de normalização usada por TODOS os consumidores (funil, rateio, atribuição) — divergência entre campos chegou a 7,8% dos leads no caso real.

## Mapa: trecho do exemplo → chave do contrato
Ao adaptar `references/exemplo-sigo/_gerar-monitor.py`, troque:
- `CAMP/CRM/TERMS` paths, `MIN_ANO`, `META{}` → contrato `fontes`/`min_ano`/`metas`.
- `load_campanhas()` `r.get("MQL")`, `r.get("Demo Agendada")`… → `campanhas_cols`.
- bloco de `lead_rows.append([...])` (flags + `_at`) → `funil`.
- `canal_norm()` → `metas`/canais do contrato.
No `_render_monitor.py`: `tcvOf()` → `tcv.formula`; `--fdisplay`/`@font-face` → `design_system`/`fonte_titulo`; metas nos cards OKR → `metas`.
