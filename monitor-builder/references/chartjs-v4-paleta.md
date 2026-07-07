# Chart.js v4 com paleta V4 — snippets canônicos

> 4 tipos canônicos de gráfico + Chart.defaults V4 + tooltip formato BR.

## 1. Chart.defaults V4 (sobrescrever globalmente uma vez)

```javascript
Chart.defaults.color = "rgba(255,255,255,0.7)";
Chart.defaults.borderColor = "#333333";
Chart.defaults.font.family = '"IBM Plex Sans", "Calibri", sans-serif';
Chart.defaults.font.size = 12;

const V4 = {
  red:      "#E50914",
  redLight: "#FF4040",
  redDark:  "#B8000E",
  yellow:   "#FFDD00",
  white:    "#FFFFFF",
  gray:     "#888888",
  bg:       "#111111",
  border:   "#333333"
};

const tooltipBase = {
  backgroundColor: "rgba(26,24,20,0.95)",
  titleColor: V4.white,
  bodyColor: V4.white,
  borderColor: V4.red,
  borderWidth: 1,
  padding: 12,
  titleFont: { family: '"IBM Plex Sans"', weight: "600", size: 12 },
  bodyFont: { family: '"IBM Plex Sans"', size: 12 },
  cornerRadius: 4,
  displayColors: true,
  boxPadding: 4
};

// Formatadores BR
const fmtBRL = v => v === 0 ? "0,00" : v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtInt = v => v.toLocaleString("pt-BR");
const fmtPct = v => v === 0 ? "0%" : v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
```

## 2. Os 4 gráficos canônicos (single-fonte)

### 2.1 Donut — Custo por dimensão maior

```javascript
new Chart(document.getElementById("chartCustoMix"), {
  type: "doughnut",
  data: {
    labels: ["{Dim 1 — ex B2C}", "{Dim 2 — ex B2B}"],
    datasets: [{
      data: [{valor1}, {valor2}],
      backgroundColor: [V4.red, V4.redDark],
      borderColor: V4.bg,
      borderWidth: 2,
      hoverOffset: 8
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "60%",
    plugins: {
      legend: {
        position: "bottom",
        labels: { padding: 16, usePointStyle: true, pointStyle: "rectRounded", boxWidth: 12, boxHeight: 12 }
      },
      tooltip: {
        ...tooltipBase,
        callbacks: {
          label: ctx => {
            const v = ctx.parsed;
            const total = ctx.dataset.data.reduce((s, x) => s + x, 0);
            const pct = (v / total * 100).toFixed(2);
            return `${ctx.label}: R$ ${fmtBRL(v)} (${pct}%)`;
          }
        }
      }
    }
  }
});
```

**Cores escolhidas:** V4.red + V4.redDark (gradiente sutil dentro da família vermelha). Pra 3 categorias usar `[V4.red, V4.yellow, V4.gray]`.

### 2.2 Donut — Distribuição por classe (head/longtail/residual)

```javascript
new Chart(document.getElementById("chartClasses"), {
  type: "doughnut",
  data: {
    labels: ["Head terms ({n} kw)", "Long-tail dormente ({n} kw)", "Residual ({n} kw)"],
    datasets: [{
      data: [imprHead, imprLong, imprResi],
      backgroundColor: [V4.red, V4.yellow, V4.gray],
      borderColor: V4.bg,
      borderWidth: 2,
      hoverOffset: 8
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false, cutout: "60%",
    plugins: {
      legend: { position: "bottom", labels: { padding: 16, usePointStyle: true, pointStyle: "rectRounded" } },
      tooltip: {
        ...tooltipBase,
        callbacks: {
          label: ctx => `${ctx.label}: ${fmtInt(ctx.parsed)} impr.`
        }
      }
    }
  }
});
```

### 2.3 Bar horizontal log — Top 10 keywords/criativos

```javascript
const top10 = [...KEYWORDS].sort((a, b) => b.impr - a.impr).slice(0, 10);
const top10Colors = top10.map(k =>
  k.cls === "head" ? V4.red :
  k.cls === "longtail" ? V4.yellow : V4.gray
);

new Chart(document.getElementById("chartTopKw"), {
  type: "bar",
  data: {
    labels: top10.map(k => k.kw.length > 28 ? k.kw.slice(0, 25) + "…" : k.kw),
    datasets: [{
      label: "Impressões",
      data: top10.map(k => k.impr),
      backgroundColor: top10Colors,
      borderRadius: 3,
      barPercentage: 0.85
    }]
  },
  options: {
    indexAxis: "y",
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: {
        type: "logarithmic",
        grid: { color: "rgba(255,255,255,0.06)", drawTicks: false },
        ticks: { callback: v => fmtInt(v), font: { size: 11 } }
      },
      y: { grid: { display: false }, ticks: { font: { size: 11 }, autoSkip: false } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        ...tooltipBase,
        callbacks: {
          title: ctx => top10[ctx[0].dataIndex].kw,
          label: ctx => {
            const k = top10[ctx.dataIndex];
            return [
              `Impressões: ${fmtInt(k.impr)}`,
              `Cliques: ${fmtInt(k.clk)}`,
              `Custo: R$ ${fmtBRL(k.cst)}`
            ];
          }
        }
      }
    }
  }
});
```

**Por que log scale:** distribuição típica long-tail varia 3-4 ordens de magnitude (ex Onco Import: top kw 3.859 impr → residual 1 impr). Linear esmagaria a long-tail visualmente.

### 2.4 Combo bar+line — Impressões+Cliques+CTR por dimensão

```javascript
new Chart(document.getElementById("chartImprClique"), {
  type: "bar",
  data: {
    labels: ["{Camp 1}", "{Camp 2}"],
    datasets: [
      {
        label: "Impressões",
        data: imprPorCamp,
        backgroundColor: V4.red,
        borderRadius: 3,
        yAxisID: "y",
        order: 2
      },
      {
        label: "Cliques (×50 escala visual)",
        data: clkPorCamp.map(v => v * 50),
        backgroundColor: V4.yellow,
        borderRadius: 3,
        yAxisID: "y",
        order: 1
      },
      {
        label: "CTR %",
        data: ctrPorCamp,
        type: "line",
        borderColor: V4.redLight,
        backgroundColor: V4.redLight,
        borderWidth: 3,
        tension: 0.3,
        pointRadius: 6,
        pointBackgroundColor: V4.redLight,
        pointBorderColor: V4.bg,
        pointBorderWidth: 2,
        yAxisID: "y1",
        order: 0
      }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 12, weight: "600" } } },
      y: {
        beginAtZero: true,
        grid: { color: "rgba(255,255,255,0.06)" },
        ticks: { callback: v => fmtInt(v), font: { size: 11 } },
        title: { display: true, text: "Volume (impr. / cliques×50)" }
      },
      y1: {
        beginAtZero: true,
        position: "right",
        grid: { display: false },
        ticks: { callback: v => v.toFixed(1) + "%", font: { size: 11 } },
        title: { display: true, text: "CTR (%)" }
      }
    },
    plugins: {
      legend: { position: "bottom", labels: { padding: 16, usePointStyle: true, pointStyle: "rectRounded" } },
      tooltip: {
        ...tooltipBase,
        callbacks: {
          label: ctx => {
            const ds = ctx.dataset.label;
            if (ds.startsWith("Cliques")) return `Cliques reais: ${fmtInt(ctx.parsed.y / 50)}`;
            if (ds === "CTR %") return `CTR: ${ctx.parsed.y.toFixed(2)}%`;
            return `${ds}: ${fmtInt(ctx.parsed.y)}`;
          }
        }
      }
    }
  }
});
```

**Por que escala visual ×50 nos cliques:** quando impressões/cliques diferem 2 ordens de magnitude (cliques são ~3% de impressões), o eixo único achatariam os cliques pra ~0 visualmente. ×50 compensa visualmente — declarar no label e no tooltip.

## 3. Gráficos para modo `multi-fonte`

Substituições conforme dados cross-platform:

### 3.1 Scatter CPC × CTR cross-platform

```javascript
new Chart(document.getElementById("chartScatter"), {
  type: "scatter",
  data: {
    datasets: [
      { label: "Google Ads",   data: [{x: ctr_g, y: cpc_g}], backgroundColor: V4.red, pointRadius: 8 },
      { label: "Meta Ads",     data: [{x: ctr_m, y: cpc_m}], backgroundColor: V4.yellow, pointRadius: 8 },
      { label: "LinkedIn Ads", data: [{x: ctr_l, y: cpc_l}], backgroundColor: V4.redLight, pointRadius: 8 },
      { label: "TikTok Ads",   data: [{x: ctr_t, y: cpc_t}], backgroundColor: V4.gray, pointRadius: 8 }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { title: { display: true, text: "CTR (%)" }, ticks: { callback: v => v.toFixed(1) + "%" } },
      y: { title: { display: true, text: "CPC (R$)" }, ticks: { callback: v => "R$ " + fmtBRL(v) } }
    },
    plugins: { legend: { position: "bottom" }, tooltip: { ...tooltipBase } }
  }
});
```

### 3.2 Bar agrupado custo cross-platform

```javascript
new Chart(document.getElementById("chartCustoCanal"), {
  type: "bar",
  data: {
    labels: ["Google", "Meta", "LinkedIn", "TikTok"],
    datasets: [{
      label: "Custo R$",
      data: [custo_g, custo_m, custo_l, custo_t],
      backgroundColor: [V4.red, V4.redDark, V4.redLight, V4.yellow],
      borderRadius: 3
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { ...tooltipBase } },
    scales: {
      y: { beginAtZero: true, ticks: { callback: v => "R$ " + fmtBRL(v) } }
    }
  }
});
```

## 4. Gráficos para modo `performance-drop`

### 4.1 Line — série temporal diária

```javascript
new Chart(document.getElementById("chartTemporal"), {
  type: "line",
  data: {
    labels: dates, // ["01/09", "02/09", ...]
    datasets: [
      { label: "Custo R$", data: spendDaily, borderColor: V4.red, backgroundColor: "rgba(229,9,20,0.1)", fill: true, tension: 0.3, yAxisID: "y" },
      { label: "Cliques", data: clicksDaily, borderColor: V4.yellow, backgroundColor: "rgba(255,221,0,0.1)", fill: false, tension: 0.3, yAxisID: "y1" }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false } },
      y: { position: "left", ticks: { callback: v => "R$ " + fmtBRL(v) } },
      y1: { position: "right", grid: { display: false }, ticks: { callback: v => fmtInt(v) } }
    },
    plugins: { legend: { position: "bottom" }, tooltip: { ...tooltipBase } }
  }
});
```

### 4.2 Bar diff vs drop anterior

```javascript
new Chart(document.getElementById("chartDiff"), {
  type: "bar",
  data: {
    labels: ["Custo", "Impressões", "Cliques", "Conv"],
    datasets: [{
      label: "Δ% vs drop anterior",
      data: [diff_custo, diff_impr, diff_clk, diff_conv],
      backgroundColor: ctx => ctx.parsed >= 0 ? V4.red : V4.gray,
      borderRadius: 3
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { callback: v => (v >= 0 ? "+" : "") + v.toFixed(1) + "%" } }
    }
  }
});
```

## 5. Anti-patterns Chart.js

- ❌ Cores fora dos 13 tokens V4 (padrão Chart.js usa azul/rosa/verde — sempre sobrescrever)
- ❌ `maintainAspectRatio: true` — quebra responsive em grid
- ❌ Animação default longa em dashboards — declarar `animation: { duration: 400 }` ou desabilitar pra renders sem interação
- ❌ Tooltip default (cinza) — sempre usar `tooltipBase` V4
- ❌ Legend top default — sempre `position: "bottom"` exceto exceção justificada
- ❌ Borda alta dos bars — `borderWidth: 0` ou 1px max
- ❌ Grid muito visível — `color: "rgba(255,255,255,0.06)"` máx no dark-first

## 6. Performance

- Renderização Chart.js v4 single-canvas leva ~50-200ms — aceitável.
- Pra dashboards com >10 charts, considerar lazy loading via IntersectionObserver.
- Datasets >1000 pontos: usar decimation plugin Chart.js v4 (`plugins: { decimation: { enabled: true } }`).
