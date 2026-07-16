---
name: monitor-builder
description: >-
  Materializa dados estruturados em visualização HTML single-file (dark-first, brand do operador
  OU do cliente) em DOIS modos. (a) MODO DASHBOARD — 1 página a partir de snapshot dual-format
  `.md`+`.manifest.yml` (default `paid-media-ingestor@1.0.0`; Performance-Sprint/Drop). (b) MODO
  MONITOR/COCKPIT — cockpit multi-tela VIVO (dados-fonte 2.0), SÓ RENDER sobre a camada derivada
  do vault (derivado/fato + dim-criativo do motor-dados-vault), com sidebar de telas + filtros
  globais estilo Google Ads, OKR/KRs por vigência, funil, safra, DRE, drill de mídia com selects
  em cascata, biblioteca de criativos com popup, debriefing por atributo criativo e dimensões de
  entrega com funil estimado por rateio — regenerado pela cadeia do feed e publicável em
  Cloudflare Pages. Ative quando precisar VER dados estruturados como HTML — dashboard pontual de
  snapshot OU monitor recorrente que o gestor acompanha. NÃO ative pra baixar/orquestrar dados
  (feed-planilha-vault), fazer joins/derivados/contrato (motor-dados-vault), análise narrativa
  interpretativa (newton/falconi), slides (deck-renderer), ou consumir fonte que ainda não existe
  (é CONSUMIDORA de dado, não produtora).
allowed-tools: Read,Write,Edit,Glob,Grep,Bash,PowerShell
---

# Skill: `monitor-builder` v2.0.0 — Renderer de dashboards e monitores (cockpits) HTML

> **2 modos.** `dashboard` (legado v1, mantido): snapshot dual-format → HTML 1 página V4.
> `monitor`/`cockpit` (v2, novo): dados vivos de feed → cockpit multi-tela filtrável,
> publicável em Cloudflare Pages. Biblioteca de referência em `references/exemplos/`.

> **Camada de visualização (Design IA) do Growth IA Ops v2.0.** Consome
> snapshot dual-format produzido por skills upstream (default
> `paid-media-ingestor@1.0.0`; extensível a Performance-Sprint/Drop) e
> renderiza HTML single-file dark-first com brand operador 100% custom,
> Chart.js v4 paleta sobrescrita, responsivo, WCAG 2.2 AA auditado,
> opcionalmente PDF via Chrome headless.

## 1. Posição no Ecossistema Growth IA Ops v2.0

**Workflow / Fase:** cross-fase — qualquer projeto com snapshot consumível.

**Camada (Princípio 5):** Design IA / visualização — consome a camada de
dado (snapshot dual-format `.md`+`.yml`), produz a camada de UI.

**Bounded context (Princípio 4):** render visual de snapshot estruturado.
NÃO ingere dado (`paid-media-ingestor`), NÃO interpreta (`newton@2.0.0`),
NÃO gera slides (`deck-renderer`).

**Pattern:** segue D-MCP-1 v2 — markdown
source-of-truth → HTML renderizado mantendo Princípio 8 (vault como estado).

## 2. Quando você é invocada

### 2.1 Triggers válidos

- Operador pede "renderiza dashboard do snapshot X", "monta visualização HTML do <snapshot>", "gera dashboard do <plataforma>".
- Skill upstream (default `paid-media-ingestor`) acabou de fechar snapshot e operador pede visualização.
- Workflow Fase 2+ cerimonial chamou pra dashboard de Performance-Drop/Sprint.

### 2.2 Recusas explícitas (não-ativações)

- **Snapshot fonte não existe** → recuse com "Snapshot `<path>` não existe. Rode `paid-media-ingestor` (ou skill upstream apropriada) primeiro pra produzir `.md`+`.yml`. Reative depois."
- **Ingestão de CSV** → redirecione pra `paid-media-ingestor@1.0.0`.
- **Análise narrativa interpretativa** → redirecione pra `newton@2.0.0`.
- **Slides** → redirecione pra `deck-renderer`.
- **DS do operador não disponível** → recuse: "DS do operador (`<vault>/00-sistema/design-system.css`) não encontrado. Rode `vault-architect` pra bootstrap do `00-sistema/`."
- **Substituir snapshot fonte** → nunca. Dashboard COEXISTE com `.md`+`.yml`, nunca substitui.

## 3. Inputs obrigatórios e ordem de consumo

| # | Input | Path canônico | Severidade | Como consumir |
|---|---|---|---|---|
| 1 | Snapshot `.manifest.yml` (source of truth) | `<vault>/.../dados-brutos-<plataforma>-<janela>.manifest.yml` | blocker | Parse YAML completo. Toda métrica vem daqui. |
| 2 | Snapshot `.md` (narrativa) | mesmo path com `.md` | alto | Extrair §7 padrões + §8 bottlenecks + §9 hipóteses como cards renderizados. |
| 3 | DS do operador (CSS + md) | `<vault>/00-sistema/design-system.css` + `design-system.md` | blocker | Tokens primitivos copiados inline no `<style>` do HTML (não link externo — single-file). |
| 4 | Logo do operador | `<vault>/00-sistema/assets/logo-horizontal-dark.svg` (dark-first default) | alto | Path relativo no `<img src>` + fallback textual `<div class="logo-fallback">` quando 404. |
| 5 | Fontes (faces) | `<vault>/00-sistema/assets/fontes/IBMPlexSans/` + `Morganite/` | médio | `@font-face` com path relativo + `font-display: swap` (fallback Arial Black / Calibri). |

Se input blocker ausente: pare e nomeie a skill upstream (Princípio 11 — Linha de Visibilidade).

## 4. Workflow canônico (5 passos)

**Passo 0 — Validação de inputs** (~1min)
- Read `.manifest.yml` (blocker). Parse YAML completo.
- Read `.md` (extração de §7+§8+§9 textuais).
- Verifique existência de `<vault>/00-sistema/design-system.css` + logo.
- Detecte modo: `single-fonte` (1 plataforma no manifest) / `multi-fonte` (`plataforma: multi-fonte`) / `performance-drop` (path contém `50-operacao/`).

**Passo 1 — Mapping snapshot → dashboard sections** (~5min)
- Leia `references/html-skeleton-v4.md` pra esqueleto canônico.
- Mapping obrigatório:
  - Frontmatter manifest → `<head>` meta (title + description + lang pt-BR)
  - `nota_governanca` → banner amarelo CTA (se não-oficial F1-18)
  - `metricas_agregadas` (custo + impr + cliques + conv) → 4 KPI cards (com flag alert se conv=0)
  - `performance_campanhas` + `performance_<sub>` → tabela zebra V4 + gráficos
  - §7 padrões (`.md`) → insight blocks
  - §8 bottlenecks → cards red-border com severidade
  - §9 hipóteses → cards com bloco Falsificação + Confidence pill
  - `handoffs_canonicos` (top 5) → footer cross-links
  - `estado_skill_a_montante` (V13 do paid-media-ingestor) → footer metadata

**Passo 2 — Render Chart.js paleta V4** (~5min)
- Leia `references/chartjs-v4-paleta.md` pra snippets.
- Sobrescreva `Chart.defaults` com paleta V4.
- 4 gráficos canônicos pra `single-fonte`:
  1. Donut **custo por dimensão maior** (campanha ou plataforma — depende do manifest)
  2. Donut **distribuição por classe** (head/longtail/residual — se Google Search) OU **CPC×CTR scatter** (cross-fonte)
  3. Bar horizontal log **top 10** (keywords/criativos/placements)
  4. Combo bar+line **impressões+cliques+CTR** por dimensão principal
- Pra `multi-fonte`/`performance-drop`: outros gráficos canônicos definidos em `references/chartjs-v4-paleta.md` §3.

**Passo 3 — Responsive + WCAG 2.2 AA + print** (~3min)
- Leia `references/responsive-print-rules.md`.
- Aplicar **media-query breakpoints**: ≤960px (tablet) + ≤520px (mobile). Esses são os thresholds CSS.
- Validar **viewports** padrão: 1440 (desktop) / 768 (tablet — cai no breakpoint ≤960) / 390 (mobile — cai no breakpoint ≤520).
- Validar contraste WCAG: ver `references/wcag-22-v4-contrast-audit.md` (já pré-auditado pra paleta V4).
- `@media print` com page-break-inside avoidance + override do banner amarelo pra legibilidade em paper (vide `wcag-22-v4-contrast-audit.md` §6).

**Passo 4 — Validação Playwright + entrega** (~3min — Playwright opcional, meta tags blocker)
- **Validação obrigatória no HTML produzido (gate Passo 4):**
  - `<meta name="source-snapshot" content="{nome-do-md}">` presente no `<head>` ✓ (V8 blocker)
  - `<meta name="source-manifest" content="{nome-do-yml}">` presente no `<head>` ✓ (V8 blocker)
  - `<title>` segue padrão `{cliente} — Dashboard {plataforma} ({janela}) · {operador}`
- **Validação Playwright opcional** (se operador autorizar): subir servidor HTTP local (`python -m http.server 8765`) + navegar + checar:
  - 4 canvases `hasContent=true`
  - KPIs renderizados batem com `.yml`
  - Logo V4 carregado OR fallback ativado
  - Console sem erros (exceto favicon 404 que é OK)
  - Mobile reflow funcional em viewport 390×844
- Path canônico: mesmo diretório do snapshot `.md`+`.yml`:
  - `<vault>/.../dados-brutos-<plataforma>-<janela>.html`
- Mensagem final (≤3 linhas): "Dashboard pronto em `<path>`. Modo `<X>`. Pra abrir: `python -m http.server 8765` no root do vault."

## 5. Gate de saída (V1-V10)

| # | Critério | Severidade |
|---|---|---|
| V1 | HTML parseável + estrutura canônica (top bar V4 + header + governance banner cond. + KPIs + charts + table + bottlenecks + hipóteses + footer) | blocker |
| V2 | Toda métrica numérica no dashboard bate ±0% com `metricas_agregadas` do `.yml` fonte | blocker |
| V3 | Paleta 100% V4 — zero cor fora dos 13 tokens primitivos (vide `references/wcag-22-v4-contrast-audit.md` §1) | blocker |
| V4 | Tipografia: `font-display: Morganite` + `font-body: IBM Plex Sans` com fallback Arial Black/Calibri | blocker |
| V5 | Logo: path relativo correto + fallback textual ativo on-error | alto |
| V6 | Responsive: passa em 1440 / 768 / 390 viewport (sem horizontal scroll exceto tabelas) | alto |
| V7 | Banner governança automático quando `nota_governanca` declara não-oficial F1-18 | alto |
| V8 | Cross-link com snapshot fonte (`.md` + `.yml`) declarado no footer + frontmatter HTML `<meta>` | médio |
| V9 | Print-friendly: `@media print` com page-break-inside avoidance | médio |
| V10 | WCAG 2.2 AA: contraste 4.5:1 normal text / 3:1 large text / 3:1 UI components — paleta V4 já pré-auditada (vide reference) | alto |

Recuse fechar se V1-V4 não passarem. V5-V10 = warning documentado.

## 6. Padrões de output

### 6.1 Path canônico

```
<vault>/.../dados-brutos-<plataforma>-<janela>.html   (mesmo diretório do .md+.yml)
```

Modo `performance-drop`:
```
50-operacao/operacional/aquisicao/paga/sprint-YYYY-Q?/drop-YYYY-MM/performance-drop.html
```

### 6.2 Estrutura canônica do HTML (resumida)

```html
<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>{cliente} — Dashboard {plataforma} ({janela}) · V4</title>
  <meta name="description" content="Dashboard {modo} · {plataforma} · {janela_label}">
  <meta name="source-snapshot" content="{path-relativo-do-md}">
  <meta name="source-manifest" content="{path-relativo-do-yml}">
  <style>/* DS V4 inline */</style>
</head>
<body>
  <div class="v4-top-bar"></div>
  <div class="container">
    <header class="page-header"><!-- tag + display + subtitle + logo --></header>
    <div class="governance-banner"><!-- só se nota_governanca declara não-oficial F1-18 --></div>
    <section id="kpis"><!-- 4 KPI cards --></section>
    <section id="charts"><!-- grid 2×2 ou 2×1 cond. modo --></section>
    <div class="insight-block"><!-- citação destacada de §7 padrão crítico --></div>
    <section id="tabela"><!-- v4-table zebra --></section>
    <section id="bottlenecks"><!-- cards red-border severidade --></section>
    <section id="hipoteses"><!-- cards com Falsificação + Confidence --></section>
    <footer class="page-footer"><!-- metadata + cross-links + assinatura V4 --></footer>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <script>/* dados inline + Chart.defaults V4 + 4 charts */</script>
</body>
</html>
```

### 6.3 Banner governança automático

Quando `manifest.nota_governanca` contém `"NÃO é F1-18 oficial"` ou
`"insumo descritivo pré-Fundação"`:

```html
<div class="governance-banner" role="alert">
  <div class="icon">⚠</div>
  <div class="text">
    <h3>{título extraído do nota_governanca}</h3>
    <p>{texto do nota_governanca}</p>
  </div>
</div>
```

Estilo: fundo `rgba(255,221,0,0.06)`, border-left 4px `--v4-yellow`,
icon yellow Morganite.

## 7. Anti-patterns proibidos

- ❌ **Ingerir CSV diretamente:** este é `paid-media-ingestor`. Recuse se operador entregar CSV sem snapshot prévio.
- ❌ **Inventar métricas:** toda métrica vem de `metricas_agregadas` do `.yml`. Se ausente, exibir "—" ou `n/a` com mesma justificativa do manifest.
- ❌ **Análise narrativa nova:** apenas REPRESENTAR §7+§8+§9 do `.md` existente. Não criar padrões/bottlenecks/hipóteses novos.
- ❌ **Paleta fora V4:** zero verde/azul/rosa/laranja. Apenas os 13 tokens primitivos + 3 gradientes oficiais. Para SEMÁNTICA (positivo/negativo/neutral), usar shades do red V4 + yellow CTA + gray.
- ❌ **Logo distorcido/rotacionado/recolorido:** preservar SVG original. Apenas resize proporcional permitido.
- ❌ **Frameworks JS pesados:** zero React/Vue/Svelte/Angular. Vanilla JS suficiente — Chart.js v4 já cobre 100% dos gráficos.
- ❌ **Build pipeline:** zero webpack/vite/rollup. Single-file HTML estático que abre direto no browser.
- ❌ **Substituir snapshot fonte:** `.md`+`.yml` permanecem como source of truth. HTML é dual coexistente, nunca substituto.
- ❌ **Inline base64 do logo SVG:** se SVG é wrapper de PNG base64 (caso V4 horizontal-dark), referência via path relativo + fallback textual. Inline incharia o HTML em ~30KB.
- ❌ **Charts sem tooltip rico:** sempre incluir tooltip Chart.js com formatação BR (vírgula decimal, R$ prefix) e callback de label customizado pra contexto.
- ❌ **Print sem page-break:** `@media print` é obrigatório com `page-break-inside: avoid` nos cards e seções.

## 8. Loop de feedback obrigatório

Antes de finalizar:

1. **Métricas batem com YAML?** Compare KPIs renderizados (Custo + Impr + Cliques + Conv) com `metricas_agregadas` do `.yml`. Diferença 0% obrigatório.
2. **Paleta auditada?** Grep no HTML por cores hex — TODAS devem estar em `references/wcag-22-v4-contrast-audit.md` §1 (13 tokens V4 + 3 gradientes oficiais).
3. **Logo carregado?** Se Playwright disponível: validar `logoLoaded: true` OR fallback ativo (`.logo-fallback` style.display=block).
4. **Banner governança consistente?** Se `nota_governanca` declara não-oficial F1-18, banner DEVE estar presente. Se nada declara, banner NÃO deve estar.
5. **Console errors?** Após render, capturar console — exceto favicon 404 (irrelevante), zero erros.

## 9. Referências consultáveis sob demanda

- `references/html-skeleton-v4.md` — esqueleto HTML canônico completo (CSS V4 + estrutura + JS data wiring)
- `references/chartjs-v4-paleta.md` — Chart.defaults V4 + 4 tipos canônicos de gráfico (donut + bar log + combo bar+line + scatter) + tooltip BR
- `references/responsive-print-rules.md` — breakpoints 1440/960/520 + print rules
- `references/governance-banner.md` — quando mostrar banner + variantes
- `references/wcag-22-v4-contrast-audit.md` — auditoria pré-feita: contraste de cada token V4 em background dark + recomendações de uso
- `templates/dashboard-skeleton.html` — template HTML pronto pra clonar
- `templates/chart-recipes.js` — snippets Chart.js V4 plug-and-play

## 10. Avaliação (3 cenários canônicos)

### Cenário 1 — Single-fonte Onco Import

**Input:** `<vault>/20-snapshots/2026-05/dados-brutos-google-ads-60d.{md,yml}` (Conv=0; B2C+B2B).

**Comportamento esperado:**
- [ ] Detecta modo `single-fonte`
- [ ] Output `dados-brutos-google-ads-60d.html` mesmo diretório
- [ ] Banner governança ativo (manifest declara não-oficial F1-18)
- [ ] 4 KPIs: R$ 1.287,14 / 6.588 / 180 / 0 (último com flag alert por Conv=0)
- [ ] 4 charts: donut B2C×B2B, donut head/longtail/residual, bar log top 10 keywords, combo impr+cliques+CTR por campanha
- [ ] Tabela completa com 18 rows
- [ ] V1-V4 passam

### Cenário 2 — Multi-fonte Fundação 1.3

**Input:** snapshot consolidado `dados-brutos-multi-fonte-90d.{md,yml}` (Google + Meta + LinkedIn).

**Comportamento esperado:**
- [ ] Detecta modo `multi-fonte`
- [ ] Seletor de canal OU comparativo lado-a-lado nos KPIs
- [ ] Donut substituído por scatter CPC×CTR cross-platform OR bar agrupado custo por canal
- [ ] Handoff `newton@2.0.0` Subfase 1.3.3 declarado no footer

### Cenário 3 — Performance-Drop Fase 2

**Input:** `50-operacao/operacional/aquisicao/paga/sprint-2026-Q3/drop-2026-09/performance-drop.{md,yml}`.

**Comportamento esperado:**
- [ ] Detecta modo `performance-drop`
- [ ] Output integra ao diretório do drop (não 20-snapshots)
- [ ] Inclui comparativo vs drop anterior se manifest declara `drop_anterior_referencia`
- [ ] Embedável no `drop-delivery-deck-builder` via iframe ou screenshot

## 11. Modo Monitor / Cockpit (v3) — render da camada derivada (dados-fonte 2.0)

Quando o pedido é um **monitor recorrente** que o gestor acompanha (cockpit vivo, não dashboard de snapshot estático), **siga o workflow em `references/modo-monitor-workflow.md`**. Esta camada foi consolidada do antigo `cockpit-builder` (deprecado) e, na v3, **restrita a SÓ RENDER** dentro da arquitetura dados-fonte 2.0.

**Posição na cadeia (bounded context v3):**
```
feed-planilha-vault      motor-dados-vault           monitor-builder (ESTA)
extract → raw/    ─────► contrato + transform ─────► render: derivado/ → monitor.html + monitor.json
                          → derivado/                 (estágio 3 da cadeia; publish é do feed)
```
- O gerador **consome `derivado/fato-ads-enriquecido.csv` + `derivado/dim-criativo.csv`** (via `load_fato()`) e **importa os helpers de parsing do `_transform.py`** (`br_num`/`pdate`/`iso`/`istrue`/`canal_norm` — 1 fonte de verdade, zero drift). **Nunca refaz join** que o motor já faz; dado que falta no derivado = feature request pro `motor-dados-vault`, não parsing novo no gerador. (CRM analítico sem PII e termos ainda são lidos do raw — são passthrough sem join, não cruzamento.)
- Pré-requisitos: feed rodando (`feed-planilha-vault`) + camada transform instalada (`motor-dados-vault`). Sem eles → pare e nomeie a skill upstream. **Monitor v1 vivo sendo migrado** (gerador antigo fazendo joins)? Siga o playbook `motor-dados-vault/references/migracao-v1-v2.md` — esta skill executa o Passo 3 de lá (refatorar o gerador em render-prep com paridade provada contra o baseline v1).
- Parametrização em DOIS contratos: `contrato-cockpit.yml` (metas OKR por `quarter_vigencia`, semântica de funil, canais — lido em **runtime**, meta NUNCA no gerador) e `config-financeiro.yml` (vigências append-only: fee/margem/tcv/budget — loader expande pra mensal; fallback CSV legado só p/ vault não migrado).

**Diferença vs Modo Dashboard:** dashboard = 1 página, snapshot `.md`+`.yml` curado. Monitor = multi-tela, dados vivos da cadeia, filtros interativos, regenerado a cada feed, publicável. PII nunca no HTML; `monitor.html`/`monitor.json` git-ignored.

**O que constrói:** o par Python `_gerar-monitor.py` (render-prep: payload interned `P` → `monitor.html` + `monitor.json` p/ skills de análise) + `_render_monitor.py` (cockpit auto-contido), plugado como estágio render na cadeia do feed (`cmd /c` + exit code — stderr mata a cadeia no PS 5.1).

**IA de telas do padrão vigente (Sigo v6.4, 10 telas decision-first):** Visão Geral (OKR vigência + pace/forecast) · Atenção (pontos cegos + reconciliação + QA + veredito) · Funil & Pipeline · Qualificadores (form + SDR) · Safra · Mídia (drill com **selects em cascata** Campanha→Conjunto + filtro de texto + clique no anúncio abre popup do criativo) · **Criativos** (biblioteca: cards com preview via image_hash→URL CDN, agrupado por nome, ordenável, popup imagem+copy+métricas) · **Debriefing** (2 tabelas full-width com subtabs Mensagem/Público + 1 cruzamento único com 3 selects atributo×público/entrega×métrica) · **Dimensões** (geo/idade×gênero/device/hora com seletor único) · Mensal/DRE (+CPL/CP-SAL/custo-demo; aviso explícito: âncora = MÊS DO EVENTO, não safra).

**Payload v3 (blocos além dos interns clássicos):** `P.dim` (atributos parseados da dim-criativo) · `P.brk` (breakdowns mensais do flow internados + **funil por ad×mês pro rateio**) · `P.lib` (biblioteca: imagem/título/CTA/body paralelo a `aI.l`). **Funil por dimensão de entrega é ESTIMADO por rateio** (evento(ad,mês) × share de spend da dimensão) — células sempre sinalizadas com `*`; funil por atributo do anúncio/público é real. **Forecast adaptativo** (`natEnd()`): projeta até o fim natural da janela do preset (mês/semana/trimestre), rótulo mostra a data-fim.

**References (modo monitor):** `modo-monitor-workflow.md` (workflow 7 passos + regras + anti-patterns + **Passo 6 colheita**) · `monitor-biblioteca.md` (**catálogo de componentes** — identificadores estáveis + contrato de dados por componente) · `blueprints/` (**modelo de negócio → telas/KPIs/cruzamento**: `aquisicao-recompra` · `recorrencia` · `tcv-projeto` · **modelo HÍBRIDO por BU** = compor rec+tcv via `receita.por_bu`, ver exemplo colina) · `monitor-arquitetura.md` (engenharia: payload interned + agregação JS) · `monitor-contrato-projeto.md` (schema do `contrato-cockpit.yml` + extensões Colina: `mes_fiscal`/`receita`/BU fallback) · `monitor-contrato-snapshot.md` (schema do `monitor.json`) · `monitor-data-realities.md` (regras de dado: flag vs `_at`, outliers, PII, receita premissa, métrica impossível).

**Biblioteca (compor, não só clonar):** escolha o **blueprint** pelo modelo de negócio → componha com o **catálogo** → clone os trechos do exemplo canônico. Ao final, **Passo 6 (colheita)**: proponha ao operador o que do monitor novo deve ser promovido pro catálogo/blueprint/exemplo — a biblioteca evolui a cada construção. *(Fase 2: extrair `assets/monitor-kit/` — css/js vendorados com `KIT_VERSION` — **gatilho disparado 2026-07-02** com o 2º monitor construído no catálogo (Colina); extração dirigida por uso, pendente de priorização.)*
- `references/exemplos/martins/` — **exemplo canônico (visual/UX/filtros/metas — preferir)**: aquisição×recompra, 7 telas, metas pro-rata por vigência + pacing, frente de negócio, filtros Google-Ads-style, `DEALS` único filtrável no cliente, publicado em Cloudflare Pages. Re-sync 2026-07-02.
- `references/exemplos/colina/` — **exemplo canônico do modelo HÍBRIDO por BU** (BUs recorrentes + BUs one-time/TCV no mesmo cockpit): receita PREMISSA em runtime, **mês fiscal customizado (16→15)**, rateio de canal indireto, **atribuição de funil MQL/SQL/Ganho ao drill** (âncora no mês do lead + trava "só onde há invest"), snapshot analítico anexado pelo renderer, semáforo custo-inverso, Safra 3 visões. Construído 2026-07-02.
- `references/exemplos/sigo/` — **exemplo canônico do padrão VIGENTE (dados-fonte 2.0, v6.4)** e do blueprint `recorrencia` (SaaS B2B: funil demo/SDR, safra, DRE de payback). Re-sync 2026-07-09: gerador **só render-prep** consumindo `derivado/` + importando helpers do `_transform.py` (incluído na pasta como dependência de leitura — o transform é domínio do `motor-dados-vault`); 10 telas (Criativos/Debriefing/Dimensões); `P.dim`/`P.brk`/`P.lib`; selects cascata + sort + tfilt; popup de criativo; rateio de funil com `*`; `config-financeiro.yml` por vigências; reconciliação CRM×campanhas; metas client-side com `canais_meta: null`. Ver `exemplos/sigo/README.md`.

**Gotchas (lições Martins, além dos de `modo-monitor-workflow.md`):** Chart.js datalabels = plugin **por-chart**; popup do filtro fecha no re-render → `event.stopPropagation()`; faturamento por dimensão = **só ganhos**; rateio de produto por `;`; ciclo = **mediana** create→close; metas só aparecem com filtro=canais-meta.

**Gotchas (lições Sigo retrofit 2026-07-02 — detalhe em `exemplos/sigo/README.md`):** **stderr do python mata o render no PS 5.1** (`2>&1` + `ErrorActionPreference=Stop` converte WARN benigno em exceção — monitor ficou 2 dias parado na virada de quarter) → wrapper roda `cmd /c "python ... 2>&1"` e decide pelo exit code, WARNs informativos em STDOUT; console do feed é **cp1252** (não printar `→`); **meta NUNCA no gerador** — quarter-fixo no Python foi a causa-raiz do travamento, meta vive no contrato e o placar recalcula no cliente; origem pode **SUPERCONTAR** eventos (linha por placement) — reconciliação só completa faltantes, nunca desconta, e a conservação no stdout monitora a divergência; veredito **arredonda** eventos fracionários de resíduo (senão nada cai em "cortar").

**Gotchas/princípios (lições Colina 2026-07-02 — detalhe e código em `exemplos/colina/README.md`):** **cozinha não vai pro cliente** — metodologia (atribuição/rateio/premissa) em comentário Python, nunca em nota no HTML nem em comentário JS do template (viaja no view-source); **métrica impossível** (cliques>impressões) → exibir "—" e reportar à origem; **telas de referência** (Safra/Mensal) ignoram o filtro de período; **medianas de tempo em janela fixa** (180d vs 180d anteriores), nunca no recorte curto; **semáforo com conta inversa** `meta/realizado` pra métrica de custo; **atribuição de funil ao grão de mídia ancora no mês do LEAD** (âncora no fechamento gera "campanha sem invest com ganho" por lag) e só assenta em criativo-mês com investimento; **canal indireto rateável** pela taxa observada dos rastreáveis (por segmento), silencioso na UI; charts multi-métrica por dimensão → **mini-charts 1 métrica/escala**; grid+Chart.js exige `.grid>*{min-width:0}`; preset que termina em hoje → **forecast projeta até o fim do mês fiscal vigente**.

**Princípio de vigência de meta (lição Martins 2026-07-02):** meta de contrato tem **vigência** (quarter) e o período selecionado tem **granularidade** — nunca exibir meta cheia contra recorte parcial. Regra: KR de **volume** (faturamento/clientes/investimento) pro-rateia por `dias(período ∩ vigência) / dias(vigência)`, com tag visível ("metas pro-rata: N de M dias"); KR de **taxa** (ticket/ROAS/CAC) **não escala**; período **sem interseção** com a vigência → **esconder a meta > mentir** (e apontar a virada de quarter no contrato). Complemento: **pacing** — período em andamento (contém hoje) projeta o fim no ritmo atual (`real ÷ dias decorridos × dias totais`) vs meta pro-rata do range completo; período encerrado não projeta.

**Filtros estado-da-arte (Martins):** date-range picker (presets + calendário 2 meses + comparação Mês/Ano/Período anterior com deltas ▲▼) + canal multi-select. **Publicação:** Cloudflare Pages — memória global `publicar-monitor-cloudflare-pages`.

---

> **v3.0.0 (2026-07-09)** — UPGRADE GERAL do modo monitor pro padrão **dados-fonte 2.0**
> (F7 da decisão `30-decisoes/2026-07-09-dados-fonte-v2.md` do Sigo): gerador restrito a
> **SÓ RENDER** — joins/derivados/QA migraram pro `motor-dados-vault` (skill nova); gerador
> consome `derivado/` e importa helpers do `_transform.py`. Absorvido o **Sigo v6.4**
> (re-sync do exemplo): 10 telas (+Criativos com biblioteca/popup · +Debriefing com
> cruzamento único por RESULTADO · +Dimensões com funil estimado por rateio `*`),
> payload `P.dim`/`P.brk`/`P.lib`, sort clicável, filtro de texto no drill, selects em
> cascata Campanha→Conjunto, forecast adaptativo `natEnd()`, DRE +CPL/CP-SAL/custo-demo
> com âncora calendário explícita, `config-financeiro.yml` por vigências (CSV legado =
> fallback p/ vault não migrado). Padrão v2 (gerador fazendo joins de CSV bruto): só em
> vaults não migrados — todo monitor novo nasce no v3; histórico no git da skill.
> **v2.2.0 (2026-07-02)** — revisão geral do **Sigo** (v5) com componentes NOVOS no
> catálogo (`monitor-biblioteca.md` §UX): **tela Qualificadores** (funil por resposta
> de form + normalização no contrato + funil por SDR), **KPI-card 3 camadas** (Δ +
> meta bullet + sparkline 8 sem), **sales velocity**, **top-N expansível**, **rótulo
> no último ponto** (`lastDL`), **pergunta da tela** (`.qask`, decision-first). IA de
> 7 telas: Visão Geral → Atenção → Funil & Pipeline → Qualificadores → Safra → Mídia →
> Mensal; KPI-wall e Segmentos mortas (redistribuídas). Doutrina UX incorporada:
> 7±2 acima da dobra · 3 camadas de contexto em todo número · 40-30-20-10 · bullet
> bar (nunca gauge) · progressive disclosure · cor só com semântica.
> **v2.1.1 (2026-07-02)** — retrofit do **Sigo** (1º monitor) pro padrão do catálogo —
> 3º monitor no padrão, re-sync de `exemplos/sigo/` (+README): metas client-side por
> vigência (variante `canais_meta: null`), reconciliação CRM×campanhas no grão
> dia×anúncio, velocidade 180d mediana, gotchas PS 5.1/cp1252/supercontagem.
> Blueprint `recorrencia` promovido a exemplo completo (backend + visual).
> **v2.1.0 (2026-07-02)** — 2º monitor do catálogo (**Colina**, exemplo novo em
> `references/exemplos/colina/`): modelo HÍBRIDO rec+TCV por BU, receita PREMISSA,
> mês fiscal customizado, rateio de canal indireto, atribuição de funil ao drill
> (âncora no lead), snapshot analítico anexado pelo renderer, semáforo custo-inverso.
> Blueprint `tcv-projeto` parcialmente validado; gatilho do monitor-kit (Fase 2) disparado.
> **v2.0.0 (2026-06-30)** — renomeada de `data-dashboard-renderer` → `monitor-builder`;
> **consolidado o `cockpit-builder`** (deprecado) como MODO MONITOR/COCKPIT vivo +
> biblioteca de referência (`references/exemplos/`: sigo + martins estado-da-arte).
> Modo `dashboard` (v1, snapshot `.md`+`.yml`) intacto.
> **v1.0.0 (2026-05-13)** — `data-dashboard-renderer`, irmã do `paid-media-ingestor`.
> Diferenciação vs Looker/Tableau/Streamlit/Tremor: HTML single-file portátil + brand
> 100% custom + governance integrada + WCAG 2.2 AA. Markdown source-of-truth → HTML.
