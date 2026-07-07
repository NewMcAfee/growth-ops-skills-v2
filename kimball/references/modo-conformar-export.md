# Modo `conformar-export` — export cru → staging no schema de um alvo vivo

> Validado no caso Martins Locações (2026-07-02): export HubSpot "negócios fechados 14d"
> → stagings pras abas `leads_pipeline` (102 cols) e `bd_buy` (7 cols) do growthpack.
> Script do caso: `<vault-martins>/20-snapshots/2026-07/_higienizar_deals_14d.py`.

## Quando é este modo (e não a consolidação)

| | Modo consolidação (default) | Modo `conformar-export` |
|---|---|---|
| Destino | Datasets analíticos do kimball (`leads_master`, `campanhas_consolidada`…) | **Schema de um dataset-alvo que já existe e continua vivo** (aba de planilha canônica, feed, tabela) |
| Quem define o schema | O kimball (tidy, átomos aditivos) | **O alvo** — headers e convenções observados nele são contrato |
| Dedupe | Entre registros das fontes (identidade) | **Anti-join contra o alvo** por chave (deal_id etc.) |
| Fim da linha | Análise consome direto | Operador/pipeline faz o **append** no alvo (staging nunca aplica direto) |

Gatilhos típicos: "higieniza esse export pra eu colar na planilha X mantendo o padrão",
"gera só as linhas novas pro bd Y", "conforma esse CSV do CRM ao layout da aba Z".

## Workflow (6 passos)

**0. Perfilar o export — sujeira real vs aparente.**
- **Encoding**: decodifique os bytes de verdade (`utf-8` vs `cp1252`) antes de concluir mojibake —
  paste/preview mente. Mojibake real (🔴 virando `ð´`, `Ã§`) repara com round-trip
  `latin1→utf-8`; char inválido NÃO repara na cegueira.
- **Fill-rate por coluna** (mesma doutrina do Passo 0): coluna 100% constante, 100% vazia ou
  100% erro (`#ERROR!` de fórmula) é **morta** → descartar documentando, ou substituir por
  derivação (ver passo 3).
- **Placeholders não-resolvidos**: `{creative}`, `{campaignid}`, `{gclid}` → vazio.
- **Chars invisíveis** (U+2060, U+200B/E/F, U+FEFF) e **emojis** em campos de texto → strip.
- **Linhas de teste** (nomes "teste", telefones inválidos): flagar no relatório, não excluir
  em silêncio.

**1. Perfilar o ALVO — o schema é contrato, as convenções também.**
- Headers do alvo = colunas do staging, na mesma ordem.
- Convenções se **observam em linhas reais recentes**, nunca se assumem: formato de data
  (`DD/MM/YYYY HH:MM:SS` vs ISO), separador decimal (`500,00`), booleans (`TRUE`/`FALSE`),
  forma da chave de identidade (telefone sem DDI? ticket como fallback?), separador de
  multi-valor (`;`), vocabulário de enums (`5. GANHO`/`PERDIDO`).
- Múltiplos alvos (ex.: aba de pipeline + aba de ganhos) = múltiplos stagings, cada um no
  seu schema.

**2. Reparos de conteúdo** — aplicar o perfilado no 0, célula a célula, preservando o
arquivo-fonte imutável.

**3. Derivação por precedência com guardas** (mesmo padrão da atribuição do Passo 4 do
modo default: precedência declarada + auditável):
- Campo morto no export mas exigido pelo alvo → derivar em cascata declarada
  (ex.: telefone: contato associado → dígitos no nome do negócio → vazio).
- **Guardas anti-falso-positivo**: rejeitar candidato igual a outro identificador
  (telefone == ticket_id), validar tamanho/forma canônica antes de aceitar.
- Correção **semântica** (ex.: canal `paid_google` fixo corrigido por `utm_source=META`)
  é permitida SE documentada no relatório e com a coluna original preservada em algum
  output pra auditoria.

**4. Conformar ao schema-alvo** — mapear coluna a coluna nas convenções do passo 1;
campos sem fonte ficam vazios (nunca inventar); enums traduzidos pro vocabulário do alvo.

**5. Dedupe anti-join contra o alvo + entrega dupla.**
- Carregar as chaves do alvo ATUAL (ele é vivo — não usar cópia velha).
- Emitir **dois stagings por alvo**: `-completo` (tudo, pra update de linhas existentes)
  e `-novos` (anti-join por chave, pronto pra append sem duplicar).
- Reportar o overlap (N já existem / M novos) — se linhas existentes no alvo estão
  desatualizadas vs o export, dizer explicitamente (append ≠ update).

**6. QA e relatório** (mini-DAMA do modo):
- Chave do staging 100% preenchida; contagens in/out reconciliam; soma de valor do
  `-completo` ≈ soma do export.
- Relatório: colunas descartadas e por quê, reparos aplicados, derivações e suas taxas
  de acerto, correções semânticas, linhas de teste flagadas, overlap por alvo.

## Anti-patterns do modo

- ❌ Aplicar o staging direto no alvo — o append/update é do operador ou do pipeline dele.
- ❌ Assumir convenção do alvo pelo header — observar linhas reais (data BR vs ISO muda tudo).
- ❌ Dedupar contra snapshot velho do alvo — recarregar antes do anti-join.
- ❌ Corrigir semanticamente sem trilha (canal, stage) — auditabilidade > "dado bonito".
- ❌ Excluir linha suspeita em silêncio — flagar e deixar a decisão pro operador.

## Números do caso de validação (Martins)

724 deals; Telefone 100% `#ERROR!` (derivado: 689 por contato + fallback nome, 0 vazios nas
chaves do bd-buy); canal fixo `paid_google` com 14 deals Meta (corrigido por utm_source,
original preservado); 6 colunas mortas descartadas; overlap 619/724 no pipeline e 71/100
no bd-buy — sem o anti-join, o operador teria duplicado 85% do append.
