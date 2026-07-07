# Estrutura DCO — Doutrina e Regras Operacionais

Documento de **doutrina estratégica** sobre Dynamic Creative Optimization no Meta Ads. Complementa `taxonomia-entidade-meta.md` (que cobre só o naming dos 2 níveis hierárquicos).

> **Origem do padrão:** validado no projeto Grupo Manchester em mai/2026 (drop maio, 13 criativos organizados em 3 containers DCO). Decisão do operador documentada no plano Sobral v3.4. Reaproveitável em qualquer conta B2B/B2C com ≥2 hipóteses de mensagem distintas a testar no mesmo público.

---

## 1. O que é DCO neste padrão

DCO no Meta = **1 ad-container** que recebe arrays de assets (imagens/vídeos) + bodies + headlines + descriptions + CTAs. A Meta combina as peças em runtime e mostra, pra cada impressão, a combinação que ela estima maior chance de conversão pra aquele usuário.

Em vez de subir N ads separados (1 por creative), sobe-se **1 ad-container DCO por hipótese de mensagem** e a Meta resolve o A/B/n internamente.

## 2. Princípio estratégico — agrupar por NARRATIVA, não por formato

A decisão não-óbvia é: **cada container DCO = 1 hipótese de mensagem (narrativa)**, não 1 formato (Feed × Stories) nem 1 placement.

**Por quê:**
- O teste estratégico real numa campanha de aquisição B2B/B2C considered é **qual mensagem move o ICP** (dor × solução × premium técnico × prova social, etc).
- Separar por placement (Feed × Stories) só reproduz fato já conhecido em 2026 — vídeo vertical domina.
- Separar por formato (estático × vídeo) também é fato resolvido na maioria das verticais.
- Separar por narrativa permite que o DCO da Meta otimize automaticamente avatar/B-roll/headline DENTRO da hipótese e revele a narrativa vencedora via breakdown por Ad. Aprendizado estratégico vai pro próximo brief de copy/criativo.

**Quando NÃO aplicar este padrão:**
- Single-creative deliberado (ex: ad de prova com 1 vídeo único e foco em frequência) → seguir `AD-*` legacy.
- Conta com 1 só hipótese de mensagem testada (raro fora de remarketing puro) → 1 container DCO faz sentido se há ≥2 variações; abaixo disso, single-creative.
- Padrão C do framework Sobral (single-creative declarado) → naming `AD-*` legacy mantido.

## 3. Decisão DCO no início do MODO ESTRUTURAR

Antes de montar a Matriz de Estrutura (Fase 2 do SKILL.md), responda:

```
DECISÃO DCO
1. Quantas hipóteses de mensagem (narrativas) distintas vão entrar nesta campanha?
   - 1 só → single-creative AD-* (Padrão C)
   - ≥2 → DCO por narrativa (Padrão A) — default 2026

2. Cada narrativa tem ≥2 variações de asset/avatar/headline disponíveis?
   - Sim → DCO confirmado
   - Não (1 só asset por narrativa) → pausar narrativa até completar ou degradar pra single-creative

3. Resultado:
   - DCO por narrativa → M containers (1 por hipótese), cada um com ≥2 assets
   - Single-creative → AD-* legacy
```

Decisão registrada explicitamente pro operador antes da Matriz de Estrutura.

## 4. Hierarquia de campanha com DCO

```
1 campanha (CBO)
├── adset A (persona/audiência 1)
│   ├── container DCO 1 (narrativa "Dor")
│   ├── container DCO 2 (narrativa "Solução")
│   └── container DCO 3 (narrativa "Premium")
├── adset B (persona 2)
│   ├── container DCO 1 (mesma narrativa "Dor", replicado)
│   ├── container DCO 2
│   └── container DCO 3
└── adset C (persona 3)
    └── ... (mesma replicação)
```

**Total de entradas no Ads Manager:** M containers × N adsets.

**Regra dura:** o MESMO container DCO replica em TODOS os adsets. Não existe distribuição manual de criativo por audiência — DCO em cima da segmentação por persona descobre sozinho qual combinação asset+texto+headline performa melhor em cada audiência. Forçar 1:1 (narrativa X só no adset Y) reduz combinações e atrasa aprendizado em volume baixo.

## 5. Regras operacionais

### 5.1 Mínimo 2-3 variações por container

DCO precisa de pelo menos 2 assets pra otimizar. Container com 1 só asset não produz decisão estatística.
- Container completo: 3+ variações (asset diferente × avatar diferente × ângulo diferente).
- Container mínimo viável: 2 variações.
- Container com 1 asset: **pausar até completar** OU degradar pra single-creative `AD-*` no adset (decisão do operador).

### 5.2 Estrutura de pastas no vault do projeto

```
criativos-ads/
└── {DROP}/                         ← ex: 01_drop_maio_2026/
    ├── {DROP}_{ID_SEQ}_..._DCO/    ← 1 pasta por container
    │   ├── CRT-001_..._Feed1x1.png
    │   ├── CRT-001_..._Stories9x16.png
    │   ├── CRT-003_..._Feed1x1.png
    │   └── ...
    └── {DROP}_{ID_SEQ}_..._DCO/
        └── ...
```

Dentro de cada pasta-container, assets `CRT-*` ficam **flat** (sem subpastas por placement — o sufixo `__Feed1x1`/`__Stories9x16` no nome basta). Facilita upload em batch no Meta sem precisar entrar em pasta por placement.

Padrão de naming completo (container + asset) em [`taxonomia-entidade-meta.md`](taxonomia-entidade-meta.md) seção "Naming hierárquico DCO".

### 5.3 Copy não pareia 1:1 com narrativa

Os N conjuntos de texto (legenda + headline + descrição) produzidos pelo Escriba/Kubrick sobem em **TODOS os containers DCO** da campanha, sem amarração 1:1 com narrativa.

- ❌ Forçar "conjunto de copy 1 só no container Dor, conjunto 2 só no container Solução"
- ✅ Subir os 5 conjuntos em todos os containers, deixar DCO combinar

Razão: forçar pareamento reduz combinações disponíveis e atrasa aprendizado num cenário de volume baixo (típico early-stage). Leitura do conjunto vencedor sai depois via breakdown "Por Body Text" (ver §6).

### 5.4 Status sempre PAUSED na criação

Via MCP, containers DCO nascem em PAUSED — operador ativa manualmente após revisão.

## 6. Leitura de resultado via breakdowns (loop de aprendizado pro Newton)

Como tudo vira combinação automática, o aprendizado NÃO sai lendo ad por ad. Sai via **breakdowns no Ads Manager** (ou via tools `ads_insights_*` do MCP).

| Breakdown | Pergunta que responde | Próxima ação |
|---|---|---|
| **Por Ad** | Qual narrativa converte mais? (Dor × Solução × Premium) | Próximo drop reforça a narrativa vencedora |
| **Por Audience** (adset) | Qual persona converte mais por narrativa? | Realocar budget entre adsets; identificar combinação persona×narrativa mais eficiente |
| **Por Creative Asset** | Dentro de cada container, qual asset venceu? | Revela A/B avatar/variação pré-instalado — input pro próximo brief criativo |
| **Por Body Text** | Qual dos N conjuntos do Escriba pegou? | Input pro próximo brief de copy |
| **Por Title** | Qual headline puxou mais? | Input pro próximo brief de copy |

**Loop fechado:**
1. Mês 1: rodar containers ativos.
2. Newton extrai os 5 breakdowns acima.
3. Identifica narrativa vencedora + asset vencedor + texto/título vencedor.
4. Brief do próximo drop reforça o vencedor + testa novas hipóteses + reativa containers pausados (com variações novas).

**No MCP:** breakdowns disponíveis via `ads_insights_*` com parâmetros `breakdown=body_asset|title_asset|description_asset|image_asset|video_asset|ad|age|gender|placement`. Detalhes em `mcp-meta-workflow.md`.

## 7. Anti-padrões DCO (estratégicos)

- ❌ **DCO por formato** (Feed × Stories como containers separados) — perde o teste de mensagem; resposta de placement já é conhecida em 2026.
- ❌ **Container DCO com 1 asset só** — não otimiza nada; pausar até completar 2+.
- ❌ **Distribuir container por adset manualmente** (narrativa X só no adset Y) — derrota o propósito; deixar DCO + segmentação resolverem.
- ❌ **Pareamento copy↔narrativa 1:1** — atrasa aprendizado em volume baixo.
- ❌ **Ler ad-por-ad em vez de breakdown** — perde insight estratégico (qual mensagem ganhou); ad-por-ad só serve pra dedupe operacional.
- ❌ **Misturar single-creative `AD-*` e container DCO `{DROP}_..._DCO` no mesmo adset sem decisão consciente** — dificulta leitura; decidir padrão por adset (default: tudo DCO se há ≥2 narrativas).
- ❌ **Ativar container direto na criação (sem PAUSED + revisão)** — risco de bug de configuração entrar em produção.

Anti-padrões de **naming** (sufixo, prefixo, capitalização) ficam em `taxonomia-entidade-meta.md` seção "Anti-padrões DCO (validação)".

## 8. Checklist DCO (pré-upload / pré-ativação)

```
[ ] Decisão DCO registrada (§3): ≥2 narrativas justificam containers separados
[ ] Cada container tem ≥2 variações de asset
[ ] Naming dos containers segue {DROP}_{ID_SEQ}_..._DCO (taxonomia-entidade-meta.md)
[ ] Naming dos assets segue CRT-{ID_SEQ}_..._{Placement}.{ext}
[ ] Cada container replica em TODOS os adsets da campanha
[ ] Copy (bodies/titles/descriptions) sobe em todos os containers (sem pareamento 1:1)
[ ] Status PAUSED em todos
[ ] Containers com 1 asset só estão pausados ou marcados como degradar pra AD-*
[ ] naming validado contra taxonomia-entidade-meta.md
```
