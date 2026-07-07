# Framework: Modo Piloto vs Escala

## Quando operar em Modo Piloto (1 campanha) vs Escala (N campanhas)

O erro clássico na abertura de uma conta nova é abrir todos os silos propostos simultaneamente. Isso dilui budget abaixo do threshold de aprendizado do algoritmo, gera ruído em vez de sinal, e nos primeiros 30 dias entrega dados inconclusivos — justamente quando o cliente está mais cético e avaliando se continua ou não.

O **Modo Piloto** concentra budget em 1 campanha-âncora com a hipótese de maior probabilidade de vitória. Valida em 30 dias ou 30 conversões. Só então expande.

### Ative Modo Piloto quando:

- Conta é **nova** (zero histórico de conversão) OU
- Conta tem **histórico contaminado** (ex: 85%+ leads fora do ICP) — o sinal anterior não serve OU
- Projeto está **sob pressão de prova** (contrato com cláusula de saída nos primeiros 3 meses, cliente cético, churn prévio com outras agências) OU
- **Budget apertado** (≤ R$ 3k/mês por canal) — diluir em 3 campanhas gera < R$ 33/dia por campanha, abaixo do mínimo do Smart Bidding aprender OU
- **Faltam criativos prontos** para 1 ou mais etapas do funil

### Abra múltiplas campanhas desde o início quando:

- Conta **madura** (30+ conversões/mês registradas no canal) E
- **Budget robusto** (R$ 10k+ por canal) que permite cada campanha ter ≥ R$ 30/dia E
- **Criativos entregues** para todas as etapas do funil E
- **Múltiplos produtos/ICPs** com keywords suficientemente distintas (sem canibalização)

## Estrutura do Modo Piloto

**1. Escolha da campanha-piloto — critérios de priorização:**

- Produto com maior share de faturamento do cliente
- Cluster de intenção mais próximo do ponto de compra (fundo de funil, transacional pura)
- Menor dependência de outras entregas (copy pronta, LP pronta, conversão rastreada)
- Maior probabilidade de gerar cotação/venda rápida — pro cliente ver número antes da cláusula de saída

**2. Alocação de budget:** 100% do budget do canal vai para a campanha-piloto. Outros silos ficam no roadmap, em pausa.

**3. Critérios de decisão GO/NO-GO após 30 dias OU 30 conversões:**

| Decisão | Critérios (quantos têm que atender) | Ação |
|---|---|---|
| ✅ **GO** (escalar) | 3 de 4: CTR ≥ benchmark, CPL ≤ alvo, % qualificação ≥ esperado, N cotações/vendas atribuídas | Abrir próximo silo do roadmap |
| ⚠️ **Zona Cinza** | Métricas mistas, na faixa de benchmark mas sem passar todos | Estender piloto +15 dias com 1-2 calibrações (negativas, RSA novo) |
| 🔴 **NO-GO** | CPL > 2x alvo OU qualificação < 40% OU zero cotações | Revisão profunda antes de escalar — problema pode ser fora de mídia (LP, atendimento) |

**4. Definição dos benchmarks antes do piloto:**

Antes de subir, documente os alvos numéricos. Se o Arquimedes já definiu CAC alvo, derive:
- CPL alvo = CAC alvo × taxa Lead→Win média do negócio
- CTR alvo = depende do nicho (5%+ em B2B com keywords de alta intenção; 2-4% em Display/Social ToF)
- % qualificação = % de leads que passam pelo pedágio/SDR como MQL

Se não há dados, usar range da categoria conforme briefing do Oráculo.

## Expansão progressiva (pós-GO)

Mesmo após GO, abrir silos **um de cada vez**, não todos simultaneamente. Cada silo novo começa com budget menor que o piloto (≤ 40% do piloto) e tem sua própria métrica de validação. Se o silo 2 falhar, não compromete o silo 1 que já está validado.

## Anti-patterns

- **Abrir 3 campanhas no dia 1 com R$ 5k/mês total** — R$ 55/dia por campanha não sustenta Smart Bidding
- **Escalar antes de 30 conversões** — Smart Bidding precisa desse volume mínimo pra migrar de Maximize Clicks pra Maximize Conversions
- **Não definir critério GO/NO-GO antes do piloto** — sem gatilho objetivo, qualquer resultado vira "vamos esperar mais um pouco" por inércia
- **Subir piloto sem pre-flight tracking** — se conversão não dispara, piloto não mede nada e o operador só descobre no fim do mês

## Exemplo real: Piloto Manchester (2026-04-16)

- **Contexto:** conta Google Ads nova, 0 conversões históricas. Contrato com cláusula de saída a partir do mês 3. Orçamento Google R$ 2.000/mês. ICP = construtora PME RJ. Produto principal = Vergalhão CA50/CA60.
- **Decisão Piloto:** 1 campanha ("Distribuição B2B Vergalhão | RJ"), 100% do budget, 3 grupos (SOLUTION/GENERIC/BRANDED). Belgo Pronto e Cercamentos no roadmap pro mês 2.
- **Critérios GO (3 de 4):** CTR ≥ 4%, CPL MQL ≤ R$ 60, % CNPJ no pedágio ≥ 60%, ≥ 3 cotações atribuídas no mês.
- **NO-GO:** CPL > R$ 100 OU % CNPJ < 40% OU zero cotações.
- **Resultado esperado:** se GO, ativa Belgo Pronto no mês 2 + reabre Meta com criativos B2B prontos.
