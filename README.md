# Growth Ops Skills v1 — Claude Code

Oito skills para Claude Code que cobrem o **stack operacional de dados + mídia** do Growth IA Ops v2.0: infraestrutura de vault, entrada de dados, consolidação, visualização, planejamento de mídia e execução nas plataformas.

> **Versão:** v1 (em produção — validadas em clientes reais V4 Colli&Co).
> **Idioma:** pt-BR.
> **Stack:** Claude Code (CLI / desktop / extensão IDE).
> **Nota:** os exemplos de referência (`references/exemplos/`, cases de cliente) tiveram valores financeiros e PII substituídos por valores fictícios — a estrutura e a metodologia são as reais.

---

## Mapa do stack

```
vault-architect ──► estrutura do vault (estado)
feed-planilha-vault ──► entrada diária de dados (Google Sheets → CSV no vault)
kimball ──► consolidação/crosswalk marketing+CRM (closed-loop)
monitor-builder ──► visualização (dashboard pontual + cockpit vivo)
darwin ──► análise de campeões Google Ads
sobral ──► plano de mídia + forecasting (decisão)
media-buyer-google ──► estruturação Google Ads (CSVs importáveis)
media-buyer-meta ──► execução Meta Ads (via MCP Marketing API)
```

---

## As 8 skills

### 1. `vault-architect` — camada de estado (v2.2.0)

Bootstrap, retrofit e otimização contínua de vaults Growth IA Ops v2.0 — estrutura de 9 categorias por tipo de output, meta-docs estruturais com slots customizáveis, manifesto versionado e **doutrina sináptica** (`mapa.md` por pasta + TOC navegável + Resumo 60s + helper `atualiza-cascata` exportável pra outras skills).

**Ativar quando:** criar/auditar/otimizar a estrutura de um vault, rodar cascata sináptica, re-sync de identidade do operador.
**Não ativar para:** criar conteúdo de marketing (skills específicas), editar manifesto vivo pós-v0.0 (`system-manifest-builder`).

### 2. `feed-planilha-vault` — entrada de dados

Configura um feed diário que baixa abas de uma planilha Google Sheets pública como CSV e sobrescreve arquivos de nome fixo num vault local (Windows) — com detecção de PII→gitignore, QA de qualidade da origem, tarefa agendada robusta (Task Scheduler) e cascata sináptica.

**Ativar quando:** automatizar a entrada de dados de planilha no vault, ou auditar/replicar um feed existente.
**Não ativar para:** planilhas privadas com OAuth, fontes não-Sheets, análise dos dados (`newton`/`darwin`), agendamento em cloud.

### 3. `kimball` — consolidação e crosswalk marketing+CRM

Consolida e cruza dados brutos multi-fonte (campanhas por plataforma, leads, contatos, deals) num dataset de retorno closed-loop — resolve identidade (email/telefone), normaliza no boundary e produz datasets tratados no grão certo + relatório de qualidade DAMA. Modo `conformar-export` transforma export cru de CRM em staging no schema de um dataset-alvo vivo, com dedup por anti-join.

**Ativar quando:** receber exports crus de cliente e precisar higienizar/deduplicar/cruzar lead→contato→deal→campanha antes da análise.
**Não ativar para:** baixar dados (`feed-planilha-vault`), interpretar retorno (`newton`/`darwin`/`falconi`), modelar banco (`data-engineer`).

### 4. `monitor-builder` — visualização HTML (v2.0.0)

Materializa dados estruturados em HTML single-file (dark-first, brand do operador ou do cliente) em dois modos: **DASHBOARD** (1 página a partir de snapshot dual-format `.md`+`.manifest.yml`) e **MONITOR/COCKPIT** (cockpit multi-tela vivo com sidebar, filtros globais estilo Google Ads, OKR/KRs, funil, cohort de recompra, DRE e drill de mídia — publicável em Cloudflare Pages e regenerável por pipeline).

**Ativar quando:** precisar VER dados estruturados como HTML — dashboard pontual ou monitor recorrente.
**Não ativar para:** ingerir CSV bruto (`paid-media-ingestor`/`feed-planilha-vault`), análise narrativa (`newton`/`falconi`), slides (`deck-renderer`).

### 5. `darwin` — análise de campeões Google Ads

Ingere relatórios de performance já filtrados aos campeões (termos de pesquisa + performance dos anúncios, últimos 10-12 meses) e produz a **Análise de Campeões** (`champion-analysis.md` + `.yml`) — a ponte entre o dado histórico de conversão e a estruturação de campanhas novas.

**Ativar quando:** houver exports de campeões prontos pra virar DNA de campanha.
**Não ativar para:** estruturar campanha (`media-buyer-google`), definir estratégia (`sobral`).

### 6. `sobral` — plano de mídia + forecasting (v2.1.0)

Estrategista de mídia paga da Fundação (Subfase 1.4.2) — produz `plano-midia.md` (alocação canal × ICP×Produto × etapa funil + estrutura de conta + pattern UTM canônico + audiências SHA-256 + cadência de testes) e forecasting com cenários de sensibilidade. Inclui modo `realocacao` (motor de portfólio sobre feed de dados).

**Ativar quando:** produzir/revisar plano de mídia, forecasting, realocação mensal de portfólio.
**Não ativar para:** executar nas plataformas (`media-buyer-*`), analisar campeões (`darwin`).

### 7. `media-buyer-google` — estruturação Google Ads

Estrutura campanhas Search + PMax executáveis a partir da Análise de Campeões (`darwin`) e/ou estratégia (`sobral`), e gera CSVs prontos pra importar no dialeto da UI de destino (Web Bulk Upload ou Google Ads Editor). Padrão cravado: 3 RSAs por grupo, 15 títulos + 4 descrições sem pin, char limits validados em Python, negativas compartilhadas, PMax com Brand Exclusion.

**Ativar quando:** estratégia/análise pronta pra virar estrutura + CSV Google Ads.
**Não ativar para:** definir budget (`sobral`), Meta/LinkedIn/TikTok (`media-buyer-meta`/...), subir campanhas na plataforma.

### 8. `media-buyer-meta` — execução Meta Ads

Braço executor via MCP da Meta (Marketing API): cria estrutura de conta nova (campanha→conjunto→anúncio) a partir de plano aprovado, sobe criativos do vault, audita/corrige nomenclatura contra a taxonomia e executa otimizações direcionadas. Tudo PAUSED por padrão, naming validado, pré-check de `is_ads_mcp_enabled`.

**Ativar quando:** plano+assets prontos pra subir, criativos novos, correção de estrutura, execução direcionada na conta Meta.
**Não ativar para:** definir estratégia (`sobral`), decidir o que otimizar (skill de análise), criar copy/criativo (`escriba`/`kubrick`), Google Ads (`media-buyer-google`).

---

## Instalação

Copie as pastas desejadas para `~/.claude/skills/` (ou `.claude/skills/` do projeto):

```powershell
Copy-Item -Recurse .\<skill> "$env:USERPROFILE\.claude\skills\<skill>"
```
