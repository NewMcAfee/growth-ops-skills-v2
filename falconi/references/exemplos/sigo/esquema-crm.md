# Exemplo — Esquema do CRM (projeto Sigo ERP)

Exemplo concreto de como o **Passo 0** mapeia as fontes de evidência de um projeto real. Sigo ERP = ERP B2B para construção civil. **Não é gabarito** — outro cliente terá outro esquema; este mostra o *tipo* de mapeamento a fazer.

> Dado distribucional agregado (sem PII de contato). `crm-completo.csv` é git-ignored e tem PII em claro — a `falconi` lê em runtime, nunca reexporta valores individuais.

## Fontes do projeto

- **Snapshot:** `90-referencias/dados-fonte/monitor.json` (o quê — volume/taxa por etapa, OKR calendário pré-computado).
- **CRM completo:** `90-referencias/dados-fonte/crm-completo.csv` (~6,2k leads, 2024–2026; o porquê profundo — qualificadores + motivo de perda).
- **Calls:** MCP de calls (Flow/BigQuery) — o que foi dito na demo.
- **Mensagens:** MCP de WhatsApp — voz/feedback do cliente.
- **Contexto:** NotebookLM do projeto.

## Mapa de funil (flag + data)

`first_contact → mql → sal → sql → connection → scheduled_meeting → show_meeting → proposal_sent → in_negotiation → win | lost`, cada um com seu `_at`. Definições canônicas do Sigo: **MQL operacional = `sal`** (SDR valida; `mql` = qualificação automática do form); **demo realizada = `show_meeting`** (meta 92/mês); **close = clientes ÷ demos realizadas**.

## Onde mora o "porquê" (evidência do CRM)

**Motivo de perda — `lost_reason`** (tagueado por etapa; ~2.944 preenchidos): a fonte #1 de causa-raiz. Vocabulário real (top): "(MQL/SAL) Fora do perfil — não é lead", "(SAL) Não conseguimos contato", "Não responde mais", "(SAL/SQL/DEMO) Não é o momento", "Reagendamento esgotado", "Fechou com outro ERP", "Faltam funcionalidades", "Telefone/e-mail inválido".

**Qualidade do lead:** `temperatura` (Frio/Morno/Quente/Forecast) e `score` (Baixo/Médio/Alto) — esparsos (~150–220 preenchidos; só leads que avançam). `segmento` (Construtora, Incorporadora, Obras Públicas, Serviços, "Não sou da Construção Civil" = não-ICP…).

**Qualificadores (BANT) — instrumentação PARCIAL:**
- **Preenchidos:** `qualificador_tamanho` (nº de obras: 1-2 / 3-5 / +5 / nenhuma), `qualificador_cargo` (Gestor sócio-diretor / Autônomo / Colaborador…), `qualificador_maturidade` (planilha Excel / nenhuma ferramenta / sistema…), `qualificador_dor` (**texto livre** — relatório BANT do SDR com empresa/CNPJ → PII; leitura caso-a-caso, não agregar).
- **100% vazios (não instrumentados):** `qualificador_interesse`, `qualificador_urgencia`, `qualificador_orçamento`, `decision_committee`, `tier_tamanho`. → Não buscar evidência aqui; a ausência de urgência/orçamento no funil é **causa-raiz candidata** de qualificação cega.

## Atribuição (mídia)

`canal` (paid_meta ~59% · paid_google ~19% · direct ~17% · SEO), `utm_campaign`, `utm_medium` (audiência), `utm_content` (**criativo** — segue a convenção `CRT-###_…`), `ad_id` (join com campanhas ~95%). Permite causa-raiz de topo por **canal × criativo**.

## Higiene conhecida (Sigo)

- Capitalização inconsistente nos qualificadores (`+5 obras` vs `+5 Obras`; `1-2 Obras` vs `1-2 obras`) → normalizar.
- Registros de teste (e-mails `@dojos.com`, `full_name`="Teste") → filtrar.
- `value_mensalidade` só existe a partir de 2026 (sem tracking de receita antes) → DRE 2025 = "s/ receita", não prejuízo.
- Campos de qualificador `dor` carregam PII (CNPJ/empresa) → nunca agregar nem reexportar.
