# Banner de governança — regras de exibição

## 1. Quando mostrar

Banner amarelo CTA é OBRIGATÓRIO quando UMA das condições:

1. `manifest.nota_governanca` contém palavras: "NÃO é F1-18 oficial", "insumo descritivo", "pré-Fundação", "modo gambiarra", "não-canônico"
2. `manifest.estado_skill_a_montante.gate_canonico_passado == false`
3. `manifest.modo` ∈ {`bootstrap-pre-fundacao`, `dados-brutos-organizados`}

## 2. Quando NÃO mostrar

1. `manifest.modo == fundacao` E `gate_canonico_passado == true`
2. `manifest.modo == recurring` em Fase 2+ (operação normal)
3. Performance-Drop cerimonial já validado por skill Fase 3

## 3. Conteúdo do banner

Extrair de `manifest.nota_governanca`:

- **Título** (h3): primeira frase, em CAPS Morganite Bold
- **Corpo** (p): o resto do texto, IBM Plex Sans Regular

Exemplos canônicos:

### Modo `bootstrap-pre-fundacao`

```html
<div class="governance-banner" role="alert">
  <div class="icon">⚠</div>
  <div class="text">
    <h3>NÃO É F1-18 OFICIAL</h3>
    <p>
      Este dashboard é insumo descritivo <strong>pré-Fundação</strong> produzido
      pela skill <code>paid-media-ingestor@1.0.0</code> em modo
      <code>bootstrap-pre-fundacao</code>. O output canônico F1-18
      (<code>analise-dados-historicos.md</code> da Subfase 1.3.3) será produzido
      pela skill <code>newton@2.0.0</code> quando os inputs blocker existirem.
    </p>
  </div>
</div>
```

### Modo `fundacao` com gate parcial

```html
<div class="governance-banner" role="alert">
  <div class="icon">ⓘ</div>
  <div class="text">
    <h3>INSUMO INTERMEDIÁRIO · FUNDAÇÃO 1.3</h3>
    <p>
      Este dashboard reflete o snapshot consolidado pré-newton@2.0.0 oficial.
      A análise interpretativa F1-18 oficial (com hipóteses falsificáveis
      rigorosas e Cenário Baseline) é produzida pela <code>newton@2.0.0</code>
      em sequência canônica.
    </p>
  </div>
</div>
```

### Modo `recurring` sem banner

Skip — banner não renderizado.

## 4. CSS canônico

```css
.governance-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background-color: rgba(255, 221, 0, 0.06);
  border: 1px solid rgba(255, 221, 0, 0.3);
  border-left: 4px solid var(--accent-cta);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-8);
}

.governance-banner .icon {
  flex-shrink: 0;
  font-family: var(--font-display);
  font-weight: 900;
  font-size: 1.75rem;
  color: var(--accent-cta);
  line-height: 1;
}

.governance-banner h3 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--accent-cta);
  margin-bottom: var(--space-1);
}

.governance-banner p {
  font-size: 0.85rem;
  color: var(--fg-muted);
  line-height: 1.6;
}

.governance-banner code {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--insight);
  background: rgba(255,255,255,0.05);
  padding: 0.05rem 0.35rem;
  border-radius: var(--radius-sm);
}
```

## 5. Ícone — convenção

- `⚠` (warning) — modo bootstrap-pre-fundacao ou gambiarra
- `ⓘ` (info) — modo fundacao intermediário
- (nenhum) — modo recurring (não renderiza banner)

## 6. Anti-patterns

- ❌ Banner em vermelho — usa amarelo CTA (governança, não erro)
- ❌ Banner em recurring/fase 2+ — só pra modos não-oficiais
- ❌ Texto genérico ("data may be incomplete") — sempre extrair do `nota_governanca` real
- ❌ Banner permanente sem skip rule — operador precisa saber quando NÃO renderizar
- ❌ Esconder banner em mobile — manter visível em todos viewports (a11y)
