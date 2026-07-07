---
name: darwin
description: |
  Analista de campeões de Google Ads do eixo Mídia Paga (Growth IA Ops v2.0) —
  ingere relatórios de performance JÁ FILTRADOS aos campeões (Relatório de termos
  de pesquisa + Performance dos anúncios, exports dos últimos 10-12 meses dos
  termos/anúncios que geraram conversão) e produz a "Análise de Campeões"
  (`champion-analysis.md` + `.yml`) — a ponte, hoje inexistente no mercado, entre
  TERMOS campeões (clusterizados por intenção × ICP) e DNA dos ANÚNCIOS campeões,
  mais baldes de desperdício → negativas e mapa intenção→campanha. Output canônico
  consumido por `sobral` (plano de mídia) e `media-buyer-google` (estrutura de
  campanhas). Seleção natural: os termos/anúncios que "sobreviveram" gerando
  conversão são o material genético das novas campanhas vencedoras (campeão +
  2 variações de ângulo novo + 1 campanha de teste).

  Premissa-âncora: a coluna "Conversões" dos relatórios é o evento de conversão
  acordado com o operador — frequentemente MQL, NÃO lead bruto (confirmar no
  Passo 0; ler errado quebra todo o downstream). Suporta 1+ ICPs com CAC/ticket
  distintos (segmenta clusters por ICP).

  Ative quando o operador entregar exports de termos+anúncios do Google Ads para
  análise de campeões, auditoria de termos, ou re-estruturação de campanhas a
  partir do que já performa.

  NÃO ative para: ingestão/normalização de CSV bruto multi-plataforma (use
  `paid-media-ingestor`); análise de baseline/premissas/bottlenecks multi-canal
  para o Cenário Baseline (use `newton` → arquimedes); estratégia, budget,
  alocação ou forecasting (use `sobral`); estrutura de campanha/keywords/RSAs/CSV
  (use `media-buyer-google`); dashboard HTML/PDF (use `monitor-builder`);
  ou cliente sem histórico de conversão (sem campeão, não há o que analisar).
allowed-tools: Read,Write,Edit,Glob,Grep,Bash,PowerShell
version: "1.0.0"
eixo: midia-paga
plataforma: google-ads
output_principal: champion-analysis
formato_output: md+yml
consumidores: [sobral, media-buyer-google]
---

# `darwin` — Analista de Campeões de Google Ads

> **Resumo 60s.** O operador exporta os termos e anúncios que JÁ performam (geraram
> conversão nos últimos 10-12 meses). `darwin` lê esses dois relatórios, roda o motor
> determinístico (`scripts/analyze_paid.py`) para parse+agregação+ranking+DNA, e faz a
> camada semântica: clusteriza termos campeões por intenção × ICP, transforma o gasto
> 0-conversão em negativas (com conflict-check), extrai o DNA dos anúncios campeões, e
> recomenda o mapa intenção→campanha. Entrega a "Análise de Campeões" que `sobral` e
> `media-buyer-google` consomem sem o operador re-explicar nada.

## 1. Posição no ecossistema

```
paid-media-ingestor (normaliza CSV bruto — opcional)
        │
   exports campeões (termos + anúncios, filtrados a conversão)
        ▼
  ►► darwin (Análise de Campeões) ◄◄
        ├──► sobral            (plano de mídia + forecasting)
        └──► media-buyer-google (estrutura de campanhas: grupos/keywords/RSAs/CSV)
```

**Diferencial (o que ninguém faz):** ferramentas de n-gram (Optmyzr, scripts Brainlabs) e
frameworks de auditoria (GrowthSpree) analisam termos OU desperdício OU stats de RSA
isoladamente. `darwin` **conecta termo campeão ↔ DNA de anúncio campeão ↔ mapa de campanha** —
a lacuna explícita na literatura PPC 2024-2026 (ver `references/metodologia.md`).

**Fronteira (Princípio 4 — Bounded Context):** `darwin` ANALISA e RECOMENDA. NÃO decide
budget/estratégia (`sobral`), NÃO estrutura campanhas nem escreve copy nova
(`media-buyer-google` — `darwin` só extrai o DNA campeão que JÁ existe).

## 2. Quando ativar / NÃO ativar

**Ative:** operador entrega "Relatório de termos de pesquisa" + "Performance dos anúncios"
do Google Ads (CSV/XLSX) e pede análise de campeões / auditoria de termos / base para
re-estruturar campanhas.

**NÃO ative** (redirecione): ver bloco no frontmatter (`paid-media-ingestor`, `newton`,
`sobral`, `media-buyer-google`, `monitor-builder`, cliente sem histórico).

## 3. Inputs

| # | Input | Severidade | Como consumir |
|---|---|---|---|
| 1 | Relatório de termos de pesquisa (CSV/XLSX) | **blocker** | `scripts/analyze_paid.py --terms` |
| 2 | Performance dos anúncios (CSV/XLSX) | alto (degrada sem) | `--ads` — sem ele, sem DNA de anúncio; sinaliza p/ media-buyer-google gerar do zero |
| 3 | Premissas do operador (Passo 0) | **blocker** | conversão = qual evento? · nº de ICPs + CAC/ticket por ICP · CPA-alvo se houver |
| 4 | ICM(s)/contexto do cliente (cond.) | médio | `Glob 10-fundacao/icm*.md` — enriquece clusterização por ICP |

> Se input 1 ausente: pare e peça. Se input 3 (conversão=?) não confirmado: **NÃO assuma lead** —
> pergunte. Ler "Conversões" como lead bruto quando é MQL distorce CP-conv e todo o downstream.

## 4. Workflow (5 passos — baixa liberdade no parse, média na interpretação)

### Passo 0 — Confirmar premissas (≤1 tela)
Pergunte ao operador, em uma rajada:
> "Antes de analisar: (a) a coluna 'Conversões' desses relatórios é qual evento — MQL, lead
> bruto, deal? (b) quantos ICPs o cliente tem e qual CAC/ticket de cada? (c) há CPA-alvo definido?"

Sem (a) confirmado, não prossiga. Registre as respostas — entram no output como premissas rastreáveis.

### Passo 1 — Motor determinístico (script, NÃO no contexto)
```bash
python scripts/analyze_paid.py --terms "<termos.csv>" --ads "<anuncios.csv>" --out champion-raw.json --top 40
```
O script parseia (encoding + formato BR), agrega por termo, ranqueia campeões (conv>0) e
desperdício (conv=0, custo>0), quebra por match type, e extrai frequência de títulos/descrições
**só dos anúncios que converteram** (= DNA campeão). Leia `champion-raw.json` (compacto), não os CSVs.

### Passo 2 — Camada semântica (LLM — onde está o valor)
A partir do `champion-raw.json`:

1. **Clusterizar termos campeões por intenção × ICP.** Intenções canônicas:
   `branded` · `concorrentes` (1 sub-cluster por concorrente) · `solucao/categoria` ·
   `generico/topo` · `problema/pain`. Marque o **ICP foco** de cada cluster (quando >1 ICP).
   Agregue n-grams: termos de baixo volume individual mas mesma raiz somam um cluster relevante
   (não descarte cauda longa convertedora).
2. **Curar negativas dos baldes de desperdício.** Os `waste_hints` do script são SUGESTÕES.
   Classifique o gasto 0-conv em baldes semânticos (free-intent, login/cliente, internacional,
   homônimo/marca-alheia, info-pura) → lista de negativas compartilhadas. **Conflict-check
   obrigatório:** nunca proponha uma negativa que bloqueie um termo campeão (ex: negativar "free"
   quando "free trial" converte). Liste o gasto recuperável (R$ e % do total).
3. **Extrair DNA dos anúncios campeões.** Dos `dna_headlines`/`dna_descriptions` + dos
   `ads.champions_top`: identifique os títulos/descrições vencedores recorrentes (o "controle" a
   reaproveitar) e o ângulo de cada anúncio campeão. Anote por cluster/tema quando possível.
4. **Concorrentes + branded.** Quais concorrentes convertem (e a que CP-conv) → prioridade de
   conquest. Poluição de branded (variante ampla cara, termos de login) → branded enxuto + cap.
5. **Aplicar as Regras Aplicadas** (`references/metodologia.md §0`) em TUDO: tiers campeão/perdedor +
   % de gasto produtivo, conflict-check, isolamento de intenção/branded, **tCPA-hint POR ICP** (não
   blended), e a guidance de RSA validada (sentence case > title case, diversidade feature/benefit/
   prova/CTA, anti-AI-slop, partial-pin como alternativa, cadência de refresh) — que entra no DNA
   entregue ao `media-buyer-google`. Estas adições tornam a Análise de Campeões definitiva, não só
   diferente: incorporam o que já é validado no estado da arte (Optmyzr, GrowthSpree, n-gram research).

### Passo 3 — Plano intermediário + validação (feedback loop OBRIGATÓRIO)
Escreva um rascunho da Análise de Campeões e apresente ao operador a **síntese** (clusters,
nº de negativas, DNA, mapa de campanhas propostas) ANTES de finalizar:
> "Análise montada. Clusters: [...]. Desperdício recuperável: R$ X (Y%). Mapa de campanhas
> proposto: [...]. Confirmo? (sim/ajustar)"

### Passo 4 — Publicar
Escreva `champion-analysis.md` (humano) + `champion-analysis.yml` (máquina) no path operacional
do projeto (ex: `50-operacao/operacional/aquisicao-paga/<canal>-<periodo>/`). Estrutura em §5.

Ao concluir, atualize a seção «Dados & Campeões» de `10-fundacao/contexto.md` via Edit — registre os campeões identificados (termos/anúncios que sobreviveram gerando conversão) em 2-5 linhas + ponteiro [[champion-analysis]], sem duplicar; toque `updated_at` + changelog.

## 5. Output — estrutura da Análise de Campeões

**`champion-analysis.md`** (humano):
1. **Resumo 60s** — CP-conv blended, % desperdício recuperável, nº clusters, motor dominante.
2. **Premissas** (rastreáveis) — conversão=?, ICPs + CAC/ticket, CPA-alvo, janela, volume analisado.
3. **Métricas blended** — custo, conversões, CP-conv, impressões, breakdown por match type.
4. **Clusters de termos campeões** — tabela por cluster: intenção · ICP foco · top termos
   (com custo/conv/CP-conv) · match types sugeridos.
5. **Baldes de desperdício → negativas compartilhadas** — lista curada + gasto recuperável + conflict-check.
6. **DNA dos anúncios campeões** — títulos/descrições vencedores (controle) + ângulos, por tema.
   Inclua os 2 achados de evidência: **sentence case > title case (3,7x CPA)** e **partial-pin do
   título #1 ≥ full-unpinned** — como recomendações pro `media-buyer-google`, default = instrução do operador.
7. **Concorrentes + branded** — quais convertem (prioridade conquest) · poluição de branded.
8. **Mapa intenção→campanha (recomendação)** — campanhas isoladas por intenção/temperatura,
   tCPA-hint por segmento/ICP (lembrar: tCPA ≥ CPA observado; ≥30 conv/mês/campanha senão portfolio),
   branded isolado + brand-negatives no resto, **1 campanha de teste** com ângulos novos.
9. **Metodologia + limitações** — thresholds usados, atribuição (last-click), o que o relatório oculta.

**`champion-analysis.yml`** (máquina, p/ `media-buyer-google`): clusters[], negatives_shared[],
ad_dna{headlines[], descriptions[]} por cluster, competitors[], campaign_map[], premises{}.

> Detalhe de schema + thresholds + evidências (com URLs) em `references/metodologia.md` e
> `references/schema-champion-analysis.md`.

## 6. Anti-patterns (de modos de falha documentados na pesquisa)

- ❌ **Ler "Conversões" como lead sem confirmar.** Distorce CP-conv e o forecasting downstream. (Passo 0)
- ❌ **Negativa que bloqueia campeão.** Conflict-check é obrigatório (ex: negativar "free" mata "free trial" 8:1).
- ❌ **Descartar cauda longa por baixo volume individual.** N-grams agregam gemas (50 variações × 2 cliques convertem juntas).
- ❌ **Otimizar para Ad Strength "Excelente".** Ad Strength NÃO correlaciona com performance (Optmyzr 20k contas) — é completude estrutural, não eficácia.
- ❌ **Extrair DNA de anúncios que não converteram.** O DNA campeão vem só dos `conv>0`.
- ❌ **Processar o CSV bruto no contexto do LLM.** Use o script; leia o JSON compacto.
- ❌ **Misturar branded com não-branded no mesmo cluster/campanha.** Branded (ROAS ~13x) distorce a otimização do resto.
- ❌ **Decidir budget/estrutura/copy nova.** Fora do escopo — handoff p/ sobral / media-buyer-google.
- ❌ **Pular o feedback loop (Passo 3).** Skill de qualidade crítica valida o plano antes de publicar.

## 7. Handoff

- **→ `sobral`:** consome §3 (blended), §4 (clusters/ICP), §8 (mapa de campanhas) como dado real
  primário do plano de mídia. (sobral precisa de modo/input que aceite a Análise de Campeões — ver iteração.)
- **→ `media-buyer-google`:** consome `champion-analysis.yml` (clusters → grupos, negatives_shared,
  ad_dna → RSA controle + 2 variações, campaign_map → campanhas + 1 teste) no padrão de qualidade definido.

## 8. Avaliação

Cenários de teste em `references/evals.md`. Critério de sucesso: `sobral` monta o plano e
`media-buyer-google` gera campanhas a partir da Análise de Campeões **sem o operador re-explicar os dados**.
