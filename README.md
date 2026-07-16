# Growth Ops Skills v2 — Claude Code

Repositório de referência para as skills do Growth IA Ops v2.0, com foco no stack operacional de dados, mídia, vault e monitoramento.

> **Status:** espelho versionado do ambiente local do operador.
> **Versão:** v2.0 (sincronizada com o pipeline dados-fonte 2.0 do Sigo ERP)
> **Idioma:** pt-BR.
> **Stack:** Claude Code (CLI / desktop / extensão IDE).

---

## Como o processo funciona

Este repositório não é o ponto de origem das skills; ele funciona como versão controlada e compartilhável do estado do ambiente local.

Fluxo correto:

1. Editar/ajustar a skill no ambiente local.
2. Validar o resultado no contexto do vault ou do fluxo operacional.
3. Sincronizar os arquivos atualizados para este repositório.
4. Commitar e publicar a mudança no GitHub.

Em outras palavras: o ambiente local é o estado de execução; o GitHub é o espelho de distribuição e histórico.

---

## Mapa do stack

```
vault-architect ──► estrutura do vault (estado)
feed-planilha-vault ──► extração diária de dados (Google Sheets → raw/ + cadeia)
motor-dados-vault ──► contrato + transform + derivados + QA
growth-review / falconi / darwin ──► consumo canônico do derivado/monitor
monitor-builder ──► visualização (dashboard/cockpit HTML)
darwin ──► análise de campeões Google Ads
sobral ──► plano de mídia + forecasting (decisão)
media-buyer-google ──► estruturação Google Ads (CSVs importáveis)
media-buyer-meta ──► execução Meta Ads (via MCP Marketing API)
```

---

## Skills incluídas

### 1. `vault-architect`
Estrutura do vault, cascata sináptica e setup de estado.

### 2. `feed-planilha-vault`
Fluxo de extração, raw, QA, transform, render, publish e notify para o pipeline dados-fonte 2.0.

### 3. `motor-dados-vault`
Contrato de dados, transform determinístico, derivados e QA gates para o pipeline dados-fonte 2.0.

### 4. `monitor-builder`
Renderer HTML de dashboards e cockpits com consumo do derivado/monitor do vault.

### 5. `darwin`
Análise de campeões do Google Ads.

### 6. `sobral`
Plano de mídia + forecasting.

### 7. `media-buyer-google`
Estruturação de campanhas Google Ads.

### 8. `media-buyer-meta`
Execução Meta Ads.

---

## Instalação

Copie as pastas desejadas para `~/.claude/skills/` (ou `.claude/skills/` do projeto):

```powershell
Copy-Item -Recurse .\<skill> "$env:USERPROFILE\.claude\skills\<skill>"
```

## Sincronização do repositório

```powershell
git add .
git commit -m "Atualiza skills para v2"
git push origin main
```
