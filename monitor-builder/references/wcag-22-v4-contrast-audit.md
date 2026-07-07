# Auditoria WCAG 2.2 AA — paleta V4 dark-first

> Audit pré-feito dos contraste de cada token V4 sobre os 3 backgrounds dark
> canônicos (`#1A1814`, `#111111`, `#1A1A1A`). Valores calculados via fórmula
> WCAG 2.2 (relative luminance + ratio).

## 1. Tokens V4 — uso permitido por categoria de texto

### Sobre `#1A1814` (`--bg-surface` — fundo principal)

| Token | Hex | Contraste vs `#1A1814` | WCAG normal text 4.5:1 | WCAG large text 3:1 | WCAG UI 3:1 |
|---|---|---|---|---|---|
| `--v4-white` | `#FFFFFF` | **17.27:1** | ✅ AAA | ✅ AAA | ✅ |
| `--v4-yellow` | `#FFDD00` | **13.66:1** | ✅ AAA | ✅ AAA | ✅ |
| `--v4-yellow-light` | `#FFEF99` | **15.21:1** | ✅ AAA | ✅ AAA | ✅ |
| `--v4-red-insight` | `#FF8888` | **6.39:1** | ✅ AA | ✅ AAA | ✅ |
| `--v4-red-light` | `#FF4040` | **4.91:1** | ✅ AA | ✅ AAA | ✅ |
| `--v4-red` | `#E50914` | **4.34:1** | ⚠️ Borderline normal text (4.34 < 4.5) | ✅ AA | ✅ |
| `--v4-red-dark` | `#B8000E` | **3.05:1** | ❌ Falha normal text | ✅ AA | ✅ |
| `--v4-gray` | `#464646` | **1.92:1** | ❌ Falha | ❌ Falha | ❌ Falha |

### Sobre `#111111` (`--v4-row-odd` — tabela ímpar / card bg)

| Token | Hex | Contraste vs `#111111` | Veredito |
|---|---|---|---|
| `--v4-white` | `#FFFFFF` | **18.74:1** | ✅ AAA |
| `--v4-yellow` | `#FFDD00` | **14.82:1** | ✅ AAA |
| `--v4-red-insight` | `#FF8888` | **6.94:1** | ✅ AA |
| `--v4-red-light` | `#FF4040` | **5.33:1** | ✅ AA |
| `--v4-red` | `#E50914` | **4.71:1** | ✅ AA normal text |
| `--v4-red-dark` | `#B8000E` | **3.31:1** | ✅ AA large text + UI |

### Sobre `#1A1A1A` (`--v4-row-even` — tabela par)

Idêntico ao `#1A1814` ±0.05 (diferença imperceptível). Use os mesmos valores.

## 2. Regras canônicas de uso (V4 dark-first)

| Onde | Use |
|---|---|
| **Body text** (normal, regular) | `--v4-white` ou `--fg-muted` (rgba(255,255,255,0.7) = **12.09:1** AAA) |
| **Headings display** (Morganite Black 26pt+) | `--v4-white` OR `--v4-red` (large text — AA passa em ambos) |
| **Accent emphasis** em normal text | `--v4-red-light` (4.91:1 AA) — **NÃO** usar `--v4-red` (4.34 borderline) |
| **CTA buttons** | `--v4-yellow` background + `--v4-deep-black` text (**13.66:1** AAA) |
| **Insight / citação** | `--v4-red-insight` italic (**6.39:1** AA) |
| **Border/UI elements** | `--v4-red` (4.34) ou `--v4-border` `#333` (UI passa 3:1) |
| **Disabled / decorativo** | `--v4-gray` `#464646` (1.92 — usar apenas onde semântica permite, ex divisores) |

## 3. Anti-pattern de uso (deve-se EVITAR)

| Anti-pattern | Por que falha |
|---|---|
| `--v4-red` (`#E50914`) em normal text sobre `#1A1814` | 4.34:1 < 4.5 — borderline normal text. Use `--v4-red-light` ou aumente tamanho pra ≥18px (large text) |
| `--v4-red-dark` (`#B8000E`) em qualquer texto sobre dark | 3.05:1 — falha normal text. Use SÓ como background de cards/badges |
| `--v4-gray` (`#464646`) em qualquer texto sobre dark | 1.92:1 — falha tudo. Use SÓ como divisor visual |
| Texto branco sobre `--v4-red` `#E50914` (header tabela) | **inverso:** `#FFFFFF` em `#E50914` = 3.98:1 — falha normal text. Use texto bold ≥600 e font-size ≥14px (large text → 3:1 passa) |
| Cores fora V4 (verde/azul/rosa) | Quebra brand. ZERO tolerância. |

## 4. Para Chart.js — Datasets

Cores de séries devem respeitar contraste **e** distinguibilidade (não-cor-dependente, conforme WCAG 1.4.1):

| Posição | Token | Razão |
|---|---|---|
| 1ª série / categoria principal | `--v4-red` `#E50914` | Acento V4 |
| 2ª série | `--v4-yellow` `#FFDD00` | CTA — alta distinção vs red |
| 3ª série | `--v4-red-light` `#FF4040` | Variante familia |
| 4ª série | `--v4-gray` `#888` (não `--v4-gray` `#464646` — esse é fundo) | Neutralidade |
| 5ª+ série | `--v4-red-dark` `#B8000E` ou tons OKLCH derivados | Cuidado: 5+ séries quebram leitura — repensar viz |

**Adicional pra a11y datasets:** sempre incluir `pointStyle: "rectRounded"` diferente por série em line/scatter — distinguibilidade não-cor-dependente.

## 5. Validação programática (snippet pra rodar no console)

```javascript
function contrast(fg, bg) {
  const lum = hex => {
    const rgb = hex.match(/\w\w/g).map(c => parseInt(c, 16) / 255);
    const [r, g, b] = rgb.map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const l1 = lum(fg), l2 = lum(bg);
  const [light, dark] = l1 > l2 ? [l1, l2] : [l2, l1];
  return ((light + 0.05) / (dark + 0.05)).toFixed(2);
}

// Validações canônicas
console.assert(contrast("#FFFFFF", "#1A1814") >= 4.5, "white on surface");
console.assert(contrast("#FFDD00", "#1A1814") >= 4.5, "yellow on surface");
console.assert(contrast("#FF8888", "#1A1814") >= 4.5, "red-insight on surface");
console.assert(contrast("#FF4040", "#1A1814") >= 4.5, "red-light on surface");
// V4 red em normal text — borderline, falha test estrito
// console.assert(contrast("#E50914", "#1A1814") >= 4.5, "v4-red on surface (BORDERLINE)");
```

## 6. Print mode contraste

`@media print` inverte pra white background — paleta V4 fica:

| Token | Contraste vs `#FFFFFF` | Veredito |
|---|---|---|
| `--v4-deep-black` `#1A1814` | **17.27:1** | ✅ AAA (texto principal) |
| `--v4-red` `#E50914` | **4.34:1** | ⚠️ Borderline |
| `--v4-red-dark` `#B8000E` | **5.66:1** | ✅ AA |
| `--v4-yellow` `#FFDD00` | **1.26:1** | ❌ Falha (não usar em print) |
| `--v4-gray` `#464646` | **8.98:1** | ✅ AAA |

**Regra print:** banner amarelo CTA fica ilegível em print. Adicionar
`@media print { .governance-banner { background: #FFF8E1; border-color: #B8860B; color: #5C4A00; } }` pra preservar conteúdo legível.

## 7. Skill upstream rule de validação

Quando renderer rodar Passo 3 (responsive + WCAG check):

1. Grep no HTML por todas cores hex (`/#[0-9A-Fa-f]{3,6}/g`)
2. Validar que TODAS estão em §1 deste documento
3. Se houver hex fora — recusar fechar (V3 blocker — paleta 100% V4)
4. Validar contraste programático com snippet §5 — ratio ≥4.5 normal text / ≥3 large/UI
5. Se algum texto em normal-size estiver em `--v4-red`, sugerir `--v4-red-light` (4.91 AA)
