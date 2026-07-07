# darwin — Cenários de avaliação (Módulo 5 GOD)

Critério de sucesso global (Módulo 1): `sobral` e `media-buyer-google` constroem campanha a partir
da Análise de Campeões **sem o operador re-explicar os dados**.

## Cenário 1 — Conta com 1 ICP, 2 relatórios completos
**Input:** Relatório de termos + Performance dos anúncios (1 cliente, 1 ICP, conversão=MQL).
**Esperado:**
- [ ] Passo 0: confirma que conversão = MQL antes de analisar (não assume lead).
- [ ] Roda `analyze_paid.py` (não processa CSV bruto no contexto).
- [ ] Clusteriza termos campeões por intenção (branded/concorrentes/solução/genérico/problema).
- [ ] Baldes de desperdício → negativas com conflict-check (não bloqueia campeão).
- [ ] Extrai DNA dos anúncios campeões (só conv>0).
- [ ] Mapa intenção→campanha com branded isolado + 1 campanha de teste.
- [ ] Feedback loop (Passo 3) antes de publicar `.md`+`.yml`.

## Cenário 2 — Só relatório de termos (sem ads report)
**Input:** apenas o Relatório de termos de pesquisa.
**Esperado:**
- [ ] Degrada com elegância: produz clusters + negativas a partir dos termos.
- [ ] Sinaliza ausência de DNA de anúncio → instrui `media-buyer-google` a gerar do zero.
- [ ] NÃO inventa DNA de anúncio campeão sem dado.

## Cenário 3 — Cliente com 2 ICPs (CAC/ticket distintos)
**Input:** 2 relatórios; operador informa 2 ICPs (ex: Pequenas CAC R$1.450 / Grandes R$3.000).
**Esperado:**
- [ ] Marca ICP foco em cada cluster.
- [ ] tCPA-hint POR segmento (não um tCPA blended) — alinhado ao CPA observado de cada ICP.
- [ ] Recomenda portfolio/isolamento por economia (não mistura economics distintas).

## Eval comparativo (5.2/5.3)
Para o Cenário 1, rodar 2 sub-agentes em paralelo sobre os MESMOS dados de exemplo — **qualquer
conta Google Ads com histórico serve** (na validação inicial usou-se Sigo ERP apenas como fixture):
(A) COM `darwin`; (B) baseline sem a skill. Comparador cego julga qual output é mais completo/
acionável/correto contra o checklist do Cenário 1. `darwin` deve vencer.

> **Genericidade (invariante):** `darwin` resolve a CLASSE "análise de campeões Google Ads", reusável
> em qualquer projeto. Nada de nomes de concorrente, clusters ou negativas de um cliente específico
> no SKILL.md/scripts — tudo deriva dos dados + Passo 0. Exemplos de clientes (incl. Sigo) só como
> referência ilustrativa, nunca como lógica determinística.
