# Responsive + print rules canônicas V4

## 1. Breakpoints

| Breakpoint | Viewport | Tipo |
|---|---|---|
| Desktop default | ≥961px | 4 KPIs em linha · grid 2×2 charts · header 2-col |
| Tablet | 521-960px | 2×2 KPIs · charts empilhados · header 1-col |
| Mobile | ≤520px | 1×4 KPIs empilhados · tabela horizontal scroll · charts full-width |

## 2. CSS canônico

```css
/* Default desktop */
.kpi-grid { grid-template-columns: repeat(4, 1fr); }
.charts-grid { grid-template-columns: 1fr 1fr; }
header.page-header { grid-template-columns: 1fr auto; }
footer.page-footer { grid-template-columns: 1fr auto; }

@media (max-width: 960px) {
  .container { padding: var(--space-6) var(--space-4); }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
  .chart-card.span-2 { grid-column: span 1; }
  header.page-header { grid-template-columns: 1fr; }
  .logo-wrap { align-items: flex-start; }
  footer.page-footer { grid-template-columns: 1fr; }
  footer.page-footer .sig-block { text-align: left; }
  h1.display { font-size: 2.5rem; }
  h2.section-title { font-size: 1.75rem; }
}

@media (max-width: 520px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .kpi-card .value { font-size: 2.5rem; }
}
```

## 3. Anti-patterns responsive

- ❌ Fixar largura em px (use `max-width` no container + `1fr` em grid)
- ❌ Esconder conteúdo crítico (KPIs, bottlenecks) em mobile — sempre mostrar
- ❌ Fontes < 14px em mobile (a11y)
- ❌ Tabelas sem overflow-x — sempre `<div class="table-wrap" style="overflow-x: auto">`
- ❌ Chart.js sem `maintainAspectRatio: false` — quebra em grid responsive

## 4. Print rules

```css
@media print {
  body { background: white; color: black; }

  .v4-top-bar {
    background: var(--v4-red) !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* Preserve banner amarelo legível em print */
  .governance-banner {
    background: #FFF8E1;
    border-color: #B8860B;
    color: #5C4A00;
  }
  .governance-banner h3 { color: #B8860B; }

  /* Avoid breaks */
  section, .chart-card, .bottleneck-card, .kpi-card { page-break-inside: avoid; }
  h2.section-title { page-break-after: avoid; }

  /* Force background colors */
  table.v4-table thead th {
    background: var(--v4-red) !important;
    color: var(--v4-white) !important;
  }

  /* Hide interactive-only elements */
  .table-wrap { overflow-x: visible !important; }
}
```

## 5. Validação visual

Recomendado abrir o HTML em 3 viewports:

1. **Desktop 1440×900** — layout cheio, todos elementos visíveis
2. **Tablet 768×1024** — KPIs 2×2, charts empilhados
3. **Mobile 390×844** — KPIs 1×4, tabela scrollable, charts full-width

**Validação Playwright opcional** (vide SKILL.md §4 Passo 4):

```javascript
await page.setViewportSize({ width: 1440, height: 900 });
await page.screenshot({ fullPage: true, path: "desktop.png" });

await page.setViewportSize({ width: 390, height: 844 });
await page.screenshot({ fullPage: true, path: "mobile.png" });
```
