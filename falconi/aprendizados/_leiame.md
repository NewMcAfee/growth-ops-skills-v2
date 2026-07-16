# Aprendizados da `falconi` — área viva

Repositório de **padrões causais validados** que a skill acumula e **relê no Passo 0** para diagnosticar melhor a cada ciclo. Materializa as fases **Padronização/Conclusão** do MASP: o que se confirmou vira conhecimento permanente que evita rediagnosticar do zero.

## Por que existe (≠ memória)

Aplicação do princípio de alavancagem: **aprendizado que muda a *execução* mora na skill (ativo), não na memória (recall passivo).** A `falconi` lê estes arquivos quando roda; a memória do projeto só é carregada no boot. Logo:

- Lição de **método/padrão causal** (reutilizável entre ciclos/clientes do mesmo tipo de funil) → **aqui**.
- Fato/estado de **um cliente** (incidente, número, decisão) → memória project-specific + `references/exemplos/<cliente>/`.
- Mudança estrutural no **como diagnosticar** → não é aprendizado solto: é iteração do `SKILL.md`/`catalogo-causas.md` (via `iterador-skills`).

## O que entra

Um padrão só entra quando **se confirmou** (não hipótese): observado em ≥1 diagnóstico real, com evidência, e **generalizável** além daquele caso pontual. Na dúvida, não suba — ruído aqui degrada todo diagnóstico futuro.

## Formato

Um arquivo por padrão (`<slug>.md`) ou entrada nesta pasta, com:

```
## Padrão: <nome curto>
- Sintoma (como aparece no funil): <ex.: queda de MQL→Demo com topo saudável>
- Causa-raiz validada: <ex.: no-show por lembrete tardio>
- Evidência que confirmou: <métrica + registro qualitativo>
- Como aplicar no próximo diagnóstico: <atalho — onde olhar primeiro>
- Origem: <projeto · data> · Confiança: <alta|média>
```

## Como a skill usa

No **Passo 0**, lê esta pasta e dá prioridade de investigação aos padrões já validados para a etapa do agressor. No **Loop (fase 5)**, ao confirmar um padrão reutilizável, **propõe** (não materializa sozinha) o append aqui — o operador aprova. Padrão refutado por ciclos seguintes é rebaixado ou removido.
