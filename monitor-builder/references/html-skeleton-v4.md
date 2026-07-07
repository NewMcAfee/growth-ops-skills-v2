# Esqueleto HTML canônico V4 — single-file dashboard dark-first

> Template pronto pra clonar. Tokens DS V4 inline (sem link externo). Logo
> via path relativo + fallback textual. Chart.js v4 via CDN. Vanilla JS.

## Estrutura completa

```html
<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cliente} — Dashboard {plataforma} ({janela}) · V4</title>
  <meta name="description" content="Dashboard {modo} · {plataforma} · {janela_label} · operador V4">
  <meta name="source-snapshot" content="{nome-do-md}">
  <meta name="source-manifest" content="{nome-do-yml}">
  <link rel="preconnect" href="https://cdn.jsdelivr.net">
  <style>
    /* ===== DS V4 inline (snapshot de 00-sistema/design-system.css) ===== */
    :root {
      /* Primitivos */
      --v4-red:           #E50914;
      --v4-red-light:     #FF4040;
      --v4-red-dark:      #B8000E;
      --v4-red-insight:   #FF8888;
      --v4-red-bg:        #2A0005;
      --v4-yellow:        #FFDD00;
      --v4-yellow-light:  #FFEF99;
      --v4-white:         #FFFFFF;
      --v4-gray:          #464646;
      --v4-deep-black:    #1A1814;
      --v4-row-odd:       #111111;
      --v4-row-even:      #1A1A1A;
      --v4-border:        #333333;

      /* Semânticos */
      --bg-surface:    var(--v4-deep-black);
      --bg-elevated:   #222020;
      --bg-muted:      var(--v4-row-odd);
      --fg-default:    var(--v4-white);
      --fg-muted:      rgba(255,255,255,0.7);
      --fg-subtle:     #888;
      --accent-default: var(--v4-red);
      --accent-cta:     var(--v4-yellow);
      --border-default: var(--v4-border);
      --insight:        var(--v4-red-insight);

      /* Componentes — tabela */
      --table-header-bg:  var(--v4-red);
      --table-header-fg:  var(--v4-white);
      --table-row-odd:    var(--v4-row-odd);
      --table-row-even:   var(--v4-row-even);
      --table-border:     var(--v4-border);

      /* Tipografia */
      --font-display: "Morganite", "Arial Black", sans-serif;
      --font-body:    "IBM Plex Sans", "Calibri", sans-serif;
      --font-mono:    "JetBrains Mono", "Courier New", monospace;

      /* Espaçamento (base 4) */
      --space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem;
      --space-4: 1rem;   --space-5: 1.25rem; --space-6: 1.5rem;
      --space-8: 2rem;   --space-10: 2.5rem; --space-12: 3rem;
      --space-16: 4rem;

      /* Raio + sombra + transição */
      --radius-sm: 0.125rem; --radius-base: 0.25rem; --radius-md: 0.5rem; --radius-lg: 0.75rem;
      --shadow-sm: 0 1px 2px 0 rgba(229,9,20,0.1);
      --shadow-base: 0 4px 6px -1px rgba(0,0,0,0.5);
      --shadow-md: 0 10px 15px -3px rgba(0,0,0,0.5);
      --transition-fast: 150ms ease;
      --transition-base: 200ms ease;
      --v4-top-bar-height: 4pt;
    }

    /* Faces (path relativo + fallback) */
    @font-face {
      font-family: 'IBM Plex Sans';
      src: url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-Regular.ttf') format('truetype');
      font-weight: 400; font-display: swap;
    }
    @font-face {
      font-family: 'IBM Plex Sans';
      src: url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-Bold.ttf') format('truetype');
      font-weight: 700; font-display: swap;
    }
    @font-face {
      font-family: 'Morganite';
      src: url('../../00-sistema/assets/fontes/Morganite/Morganite-Black.ttf') format('truetype');
      font-weight: 900; font-display: swap;
    }
    /* + Medium/SemiBold/Italic conforme necessidade */

    /* Reset */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      font-size: 14px;
      line-height: 1.5;
      color: var(--fg-default);
      background-color: var(--bg-surface);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }

    /* Top bar canônica */
    .v4-top-bar {
      height: var(--v4-top-bar-height);
      background-color: var(--v4-red);
      width: 100%;
      position: sticky; top: 0; z-index: 10;
    }

    /* Container */
    .container { max-width: 1400px; margin: 0 auto; padding: var(--space-8) var(--space-6); }

    /* Header */
    header.page-header {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: end;
      gap: var(--space-6);
      padding-bottom: var(--space-6);
      border-bottom: 1px solid var(--border-default);
      margin-bottom: var(--space-8);
    }
    .section-tag {
      font-weight: 600;
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      color: var(--accent-default);
      text-transform: uppercase;
    }
    h1.display {
      font-family: var(--font-display);
      font-weight: 900;
      font-size: clamp(2.5rem, 6vw, 4rem);
      line-height: 0.9;
      text-transform: uppercase;
    }
    h1.display .accent { color: var(--accent-default); }
    .logo-wrap img { height: 48px; width: auto; }
    .logo-wrap .logo-fallback {
      display: none;
      font-family: var(--font-display);
      font-weight: 900;
      font-size: 2rem;
      color: var(--accent-default);
    }

    /* Governance banner (yellow CTA) */
    .governance-banner {
      display: flex;
      gap: var(--space-4);
      padding: var(--space-4) var(--space-5);
      background-color: rgba(255,221,0,0.06);
      border: 1px solid rgba(255,221,0,0.3);
      border-left: 4px solid var(--accent-cta);
      border-radius: var(--radius-md);
      margin-bottom: var(--space-8);
    }
    .governance-banner .icon {
      font-family: var(--font-display);
      font-weight: 900;
      font-size: 1.75rem;
      color: var(--accent-cta);
    }
    .governance-banner h3 {
      font-family: var(--font-display);
      font-weight: 700;
      text-transform: uppercase;
      color: var(--accent-cta);
      margin-bottom: var(--space-1);
    }

    /* KPI grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--space-4);
    }
    .kpi-card {
      background-color: var(--v4-red-bg);
      border: 1.5pt solid var(--v4-red);
      border-radius: var(--radius-md);
      padding: var(--space-5);
      transition: transform var(--transition-base);
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    .kpi-card .label {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--fg-muted);
    }
    .kpi-card .value {
      font-family: var(--font-display);
      font-weight: 900;
      font-size: 3rem;
      line-height: 0.95;
      color: var(--v4-white);
    }
    .kpi-card.alert .delta strong { color: var(--v4-red-light); }

    /* Charts grid */
    .charts-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--space-5);
    }
    .chart-card {
      background-color: var(--v4-row-odd);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: var(--space-5);
    }
    .chart-card.span-2 { grid-column: span 2; }
    .chart-canvas-wrap { min-height: 280px; }

    /* Tabela canônica */
    .table-wrap { overflow-x: auto; border: 1px solid var(--border-default); border-radius: var(--radius-md); }
    table.v4-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }
    table.v4-table thead th {
      background-color: var(--table-header-bg);
      color: var(--table-header-fg);
      padding: var(--space-3) var(--space-4);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.72rem;
      letter-spacing: 0.08em;
      position: sticky; top: 0;
    }
    table.v4-table tbody tr:nth-child(odd) { background-color: var(--table-row-odd); }
    table.v4-table tbody tr:nth-child(even) { background-color: var(--table-row-even); }
    table.v4-table tbody tr:hover { background-color: var(--v4-red-bg); }
    table.v4-table tbody td {
      padding: var(--space-3) var(--space-4);
      border-top: 1px solid var(--table-border);
    }

    /* Pills */
    .pill {
      display: inline-block;
      padding: 0.15rem 0.6rem;
      border-radius: var(--radius-base);
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
    }
    .pill.head     { background: rgba(229,9,20,0.18); color: var(--v4-red-light); border: 1px solid var(--v4-red); }
    .pill.longtail { background: rgba(255,221,0,0.1); color: var(--v4-yellow); }
    .pill.residual { background: rgba(255,255,255,0.05); color: var(--fg-subtle); }

    /* Bottleneck cards */
    .bottleneck-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: var(--space-4);
    }
    .bottleneck-card {
      background-color: var(--v4-row-odd);
      border: 1px solid var(--border-default);
      border-left: 4px solid var(--v4-red);
      border-radius: var(--radius-md);
      padding: var(--space-5);
    }
    .bottleneck-card.blocker { border-left-color: var(--v4-red); background: linear-gradient(135deg, rgba(229,9,20,0.08) 0%, transparent 60%), var(--v4-row-odd); }
    .bottleneck-card.high { border-left-color: var(--v4-red-light); }
    .bottleneck-card.medium { border-left-color: var(--v4-yellow); }
    .bottleneck-card .id {
      font-family: var(--font-display);
      font-weight: 900;
      font-size: 1.5rem;
      color: var(--accent-default);
    }
    .bottleneck-card .severity {
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      padding: 0.2rem 0.5rem;
      border-radius: var(--radius-sm);
    }
    .bottleneck-card.blocker .severity { background: var(--v4-red); color: var(--v4-white); }
    .bottleneck-card.high .severity { background: rgba(255,64,64,0.15); color: var(--v4-red-light); border: 1px solid var(--v4-red-light); }
    .bottleneck-card.medium .severity { background: rgba(255,221,0,0.12); color: var(--v4-yellow); border: 1px solid rgba(255,221,0,0.4); }

    /* Insight block */
    .insight-block {
      background-color: var(--v4-row-odd);
      border-left: 3px solid var(--v4-red);
      padding: var(--space-4) var(--space-5);
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
    }
    .insight-block .quote {
      font-style: italic;
      color: var(--insight);
    }

    /* Footer */
    footer.page-footer {
      margin-top: var(--space-16);
      padding-top: var(--space-6);
      border-top: 1px solid var(--border-default);
      display: grid;
      grid-template-columns: 1fr auto;
      gap: var(--space-6);
    }
    footer.page-footer .sig-block {
      text-align: right;
      font-family: var(--font-display);
      font-weight: 700;
      text-transform: uppercase;
      color: var(--fg-muted);
    }
    footer.page-footer .sig-block .red { color: var(--accent-default); font-weight: 900; }

    /* Responsive */
    @media (max-width: 960px) {
      .kpi-grid { grid-template-columns: repeat(2, 1fr); }
      .charts-grid { grid-template-columns: 1fr; }
      .chart-card.span-2 { grid-column: span 1; }
      header.page-header { grid-template-columns: 1fr; }
      footer.page-footer { grid-template-columns: 1fr; }
    }
    @media (max-width: 520px) {
      .kpi-grid { grid-template-columns: 1fr; }
    }

    /* Print */
    @media print {
      body { background: white; color: black; }
      .v4-top-bar { background: var(--v4-red) !important; -webkit-print-color-adjust: exact; }
      section, .chart-card, .bottleneck-card, .kpi-card { page-break-inside: avoid; }
    }
  </style>
</head>
<body>

  <div class="v4-top-bar"></div>

  <div class="container">

    <header class="page-header">
      <div>
        <div class="section-tag">{seção: ex "Snapshot · Pré-Fundação · 20-snapshots/2026-05"}</div>
        <h1 class="display">{título line 1} <span class="accent">{accent}</span><br>{título line 2}</h1>
        <p class="subtitle">{subtitle com cliente + janela + métricas-âncora resumidas}</p>
      </div>
      <div class="logo-wrap">
        <img src="../../00-sistema/assets/logo-horizontal-dark.svg"
             alt="{Operador — ex V4 Company}"
             onerror="this.style.display='none';this.nextElementSibling.style.display='block'">
        <div class="logo-fallback">V4</div>
        <div class="logo-caption">{Operador} · Growth IA Ops v2.0</div>
      </div>
    </header>

    <!-- Banner governança (cond. — se nota_governanca declara não-oficial F1-18) -->
    <div class="governance-banner" role="alert">
      <div class="icon">⚠</div>
      <div class="text">
        <h3>{título extraído}</h3>
        <p>{texto do nota_governanca}</p>
      </div>
    </div>

    <section id="kpis">
      <h2 class="section-title">§3 Meta-métricas · período inteiro</h2>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="label">Custo total</div>
          <div class="value">R$ {custo}</div>
          <div class="delta">{custo_diario_medio}/dia · {custo_mensal_extrapolado}/mês extrapolado</div>
        </div>
        <!-- + 3 KPI cards (impr, cliques, conv) -->
      </div>
    </section>

    <section id="charts">
      <h2 class="section-title">§4 Performance · visualizações</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <h3>{título chart 1}</h3>
            <div class="chart-lead">{lead chart 1}</div>
          </div>
          <div class="chart-canvas-wrap"><canvas id="chart1"></canvas></div>
        </div>
        <!-- + 3 chart-cards -->
      </div>
    </section>

    <!-- Insight block (citação de §7 padrão crítico extraído) -->
    <div class="insight-block">
      <p class="quote">"{padrão crítico extraído do §7 do markdown}"</p>
    </div>

    <section id="tabela">
      <h2 class="section-title">§6 Tabela completa</h2>
      <div class="table-wrap">
        <table class="v4-table" id="tableMain">
          <thead><tr><!-- colunas dinâmicas conforme manifest --></tr></thead>
          <tbody><!-- linhas via JS --></tbody>
        </table>
      </div>
    </section>

    <section id="bottlenecks">
      <h2 class="section-title">§8 Bottlenecks</h2>
      <div class="bottleneck-grid">
        <div class="bottleneck-card {severidade}">
          <div class="header-row"><div class="id">{B1}</div><div class="severity">{severidade}</div></div>
          <h4>{nome}</h4>
          <p>{descricao}</p>
          <div class="meta">Handoff: <strong>{handoff}</strong></div>
        </div>
        <!-- + cards B2..Bn -->
      </div>
    </section>

    <section id="hipoteses">
      <h2 class="section-title">§9 Hipóteses preliminares</h2>
      <div class="bottleneck-grid">
        <div class="bottleneck-card high">
          <div class="header-row"><div class="id">{H1}</div><div class="severity">Conf. {confidence}</div></div>
          <h4>{nome curto}</h4>
          <p>{declaracao}</p>
          <div class="meta"><strong>Falsificação:</strong> {falsificacao}</div>
        </div>
        <!-- + cards H2..Hn -->
      </div>
    </section>

    <footer class="page-footer">
      <div class="meta-left">
        <strong>Operador:</strong> {operador}<br>
        <strong>Cliente:</strong> {cliente} · ticker <code>{ticker}</code><br>
        <strong>Skill renderer:</strong> <code>monitor-builder@1.0.0</code><br>
        <strong>Skill upstream:</strong> <code>{skill_upstream}</code><br>
        <strong>Snapshot fonte:</strong> <code>{nome-do-md}</code> + <code>{nome-do-yml}</code><br>
        <strong>Data:</strong> {data} · <strong>Janela:</strong> {janela_inicio} → {janela_fim}
      </div>
      <div class="sig-block">
        <div class="red">{Operador — ex V4 Company}</div>
        {tagline operador — ex "Inimiga da inércia"}
      </div>
    </footer>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <script>
    // Dados inline extraídos do manifest YAML
    const DATA = { /* manifest.metricas_agregadas + performance_* + etc */ };

    // Render table via JS (conteúdo dinâmico)
    function renderTable() { /* ... */ }
    renderTable();

    // Chart.defaults V4 (vide references/chartjs-v4-paleta.md)
    Chart.defaults.color = "rgba(255,255,255,0.7)";
    Chart.defaults.borderColor = "#333";
    Chart.defaults.font.family = '"IBM Plex Sans", "Calibri", sans-serif';
    const V4 = { red: "#E50914", redLight: "#FF4040", redDark: "#B8000E", yellow: "#FFDD00", gray: "#888", bg: "#111" };
    const tooltipBase = {
      backgroundColor: "rgba(26,24,20,0.95)",
      titleColor: "#FFFFFF",
      bodyColor: "#FFFFFF",
      borderColor: V4.red,
      borderWidth: 1,
      padding: 12,
      cornerRadius: 4
    };

    // 4 Chart.js charts (vide references/chartjs-v4-paleta.md §2)
    new Chart(document.getElementById("chart1"), { /* ... */ });
    // ... + 3 charts
  </script>
</body>
</html>
```

## Notas de implementação

1. **Path relativo do logo** depende da profundidade do output no vault:
   - `20-snapshots/YYYY-MM/file.html` → `../../00-sistema/assets/...`
   - `50-operacao/operacional/aquisicao/paga/sprint-YYYY-Q?/drop-YYYY-MM/file.html` → `../../../../../00-sistema/assets/...`

2. **Fonte do logo:** prefira `logo-horizontal-dark.svg` em dark-first.

3. **Charts ID convenção:** `chartCustoMix` / `chartClasses` / `chartTopKw` / `chartImprClique` (single-fonte) — variável conforme modo.

4. **Banner governança é OPCIONAL** — só renderizar quando `manifest.nota_governanca` ou `manifest.estado_skill_a_montante.gate_canonico_passado == false`.
