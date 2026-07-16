# Ranking cruza o CRM nas dimensões de decisão — CTR nunca é norte

**Padrão (retrospectiva/sprint):** quando o operador pede "rankear tudo" (o que deu certo/errado), a tentação é rankear as dimensões de plataforma (idade, gênero, geo, device) pelo que a plataforma expõe — e o breakdown do Meta só traz custo/impressão/clique, sem conversão. Cair pra **CTR como critério de "melhor/pior" é erro**: CTR não mede resultado e não está na régua (que vai até Lead). O caminho certo é **cruzar o CRM deal-level**, onde moram as dimensões que decidem um B2B: `segmento`, `qualificador_tamanho` (porte/nº-obras), `qualificador_cargo`, `create_at` (hora), `user_agent` (device), `state` (geo) + `lost_reason` — e computar o **funil real por bucket** (lead→SAL→SQL→demo→win→receita) + taxas.

**Incidente (piloto Sigo Q2, 2026-07-10).** Na 1ª versão do §4 do dossiê, dois erros que o operador pegou:
1. **CTR usado como norte** em geo/idade/gênero ("candidato a exclusão pelo pior CTR") — quando a instrução era cruzar com o CRM.
2. **Células "—" contraditórias:** CPA R$ 113 com a coluna de conversões em branco (lido como zero — mas CPA existe logo conv>0); "cliente" numa linha sem "demo".

**Correção.** Reconstruir o §4 em 3 famílias: (A) mídia com custo → CP-SQL/CP-SAL/ROAS; (B) **perfil de quem converte cruzado com o CRM**; (C) `lost_reason`. Idade/gênero saíram do ranking (não existem no CRM/lead) com o motivo declarado — não viraram tabela de CTR. O cruzamento revelou o achado central que a estratificação só-por-canal não pegava: **63% dos leads em porte errado** (1-2 obras/nenhuma obra convertem lead→demo a ≤10,6% vs 21-23% do porte-alvo) e **50,4% das perdas "fora do perfil"** — promovendo 2 causas de [hipótese] a [confirmada].

**Regras que viraram invariante da skill (Fase 2b):**
- CTR/métrica de entrega **nunca** é norte de ranking; dimensão sem cruzamento CRM fica **fora** do ranking, com motivo — não vira CTR.
- Régua degrada por disponibilidade de **custo** (mídia→CP-X/ROAS; CRM→Faturamento/Novos Clientes/taxa), não por teimosia.
- Toda tabela = **funil completo e consistente**; denominador de CPA/CPL visível e reconciliável; nada de "—" que contradiz; ranking sempre em tabela.
- Quando a fonte óbvia falha (`leads` vazia), **pense o caminho** no CRM completo (deal-level) — não caia pra métrica de entrega.

**Fonte:** `20-snapshots/2026-Q2/dossie-quarter-q2-2026.md` §4A/§4B/§4C (projeto Sigo ERP).
