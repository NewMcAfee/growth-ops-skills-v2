# Catálogo de causa-raiz por etapa do funil

Ponto de partida para a fase **Causa-raiz** — não gabarito. Cada etapa tem causas típicas e o **campo-evidência** onde confirmá-las. Genérico e parametrizável: os nomes de campo entre parênteses são exemplos do padrão de CRM B2B SaaS; mapeie aos campos reais do projeto no Passo 0.

## Como usar

1. Identifique a **etapa do indicador agressor** (fase Estratificação).
2. Vá às causas prováveis dessa etapa (abaixo).
3. Confirme cada uma na **ordem de evidência**: snapshot → CRM → calls → mensagens. Rotule [confirmada] (evidência citada) ou [hipótese-a-verificar].
4. **Normalize** valores sujos (capitalização/sinônimos) antes de agregar.
5. Trate **campo 100% vazio** como *não-instrumentado*: não é evidência — e a cegueira nesse qualificador pode ser ela mesma a causa-raiz.

> **Atalho de ouro:** muitos CRMs já **tagueiam o motivo de perda por etapa** (campo tipo `lost_reason`, ex.: "(SAL) Não conseguimos contato"). Comece por ele — é causa-raiz semi-pronta; a prefixação revela em que etapa o lead morreu.

---

## Topo — Lead → MQL/SAL (qualidade de fonte / fit)

| Causa provável | Evidência onde confirmar |
|---|---|
| Tráfego fora do ICP (mídia atraindo não-perfil) | `lost_reason` "fora do perfil/não é lead"; `segmento` fora do ICP; qualificadores de fit (tamanho/cargo) cruzados por **canal × criativo** (`utm_content`/`ad_id`) |
| Dado de contato inválido | `lost_reason` "telefone/e-mail inválido"; taxa de invalidez por fonte |
| Promessa do criativo desalinhada com o produto | `utm_content` (criativo) × taxa de fit/avanço por criativo; calls de quem avançou |

Pergunta-guia: *o gargalo é volume (poucos leads) ou qualidade (muitos leads, baixo fit)?* Volume → mídia/orçamento; qualidade → segmentação/criativo/form.

---

## Meio — SAL → Demo agendada → Demo realizada (conexão / agendamento / no-show)

| Causa provável | Evidência onde confirmar |
|---|---|
| Baixa contactabilidade / follow-up lento | `lost_reason` "não conseguimos contato"/"não responde mais"; latência `first_contact_at − create_at`; flag `connection` |
| No-show / reagendamento esgotado | `lost_reason` "reagendamento esgotado"; gap `scheduled_meeting` → `show_meeting`; calls de remarcação |
| Timing / maturidade ("não é o momento") | `lost_reason` "não é o momento"; `qualificador_maturidade`; voz do lead em calls |
| Capacidade comercial (SDR/closer insuficiente) | volume de agendados vs realizados por `sdr`/`closer`; fila de demos |

Pergunta-guia: *o lead chega à demo? Se agenda mas não comparece → no-show (lembrete/qualificação); se nem agenda → contactabilidade/interesse.*

---

## Fundo — Demo → Proposta → Negociação → Ganho (fechamento)

| Causa provável | Evidência onde confirmar |
|---|---|
| Perda competitiva | `lost_reason` "fechou com outro/concorrente"; objeção em calls |
| Gap de produto / funcionalidade | `lost_reason` "faltam funcionalidades"; `qualificador_dor` (texto); calls |
| Orçamento / poder de decisão | `qualificador_orçamento`/`decision_committee` **se instrumentados**; senão, calls/mensagens (a evidência migra pro qualitativo) |
| Proposta fraca / discovery raso | padrão de perda pós-`proposal_sent`; `value` vs ticket-alvo; calls de negociação |

Pergunta-guia: *perde por fit (produto/perfil) ou por execução (proposta/discovery/preço)?* Fit → qualificação/produto; execução → playbook comercial.

---

## Benchmarks de referência (B2B SaaS — parametrizável por projeto)

Use como **régua**, ajustando ao baseline do cliente (o baseline do próprio projeto > a média de indústria):

- **Lead → MQL** ~40% · **MQL → SQL** 15–21% (red flag <15% → lead scoring + follow-up speed)
- **SQL → Oportunidade** ~40% · **Oportunidade → Fechamento** ~37%
- **Win rate** 20–30% (red flag <25% → qualificação/proposta/competitivo)
- **Ciclo de venda** 46–75 dias ótimo (>120d red flag)

Fonte: regras aplicadas em `regras-aplicadas.md`. Diferenças por **segmento/fonte** são grandes — segmente antes de comparar.

---

## Higiene de dado (antes de qualquer agregação)

- **Normalize** capitalização e sinônimos (ex.: "+5 obras" = "+5 Obras"; "gestor_(sócio/diretor)" = "Gestor (Sócio/Diretor)").
- **Filtre registros de teste** (e-mails internos / domínio próprio / `ad_id`=manual com nomes "teste").
- **Outliers de data** (ex.: `create_at` pré-início do projeto) — descarte ou isole.
- **Campo 100% vazio** ≠ "tudo zero": é não-instrumentado. Reporte como lacuna, não como sinal negativo.
