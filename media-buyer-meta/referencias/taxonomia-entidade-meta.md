# Taxonomia de Entidade Meta (Growth IA Ops) — Referência para Media Buyer META

Naming das **entidades** no Ads Manager (campanha → conjunto → anúncio). Validado vivo na conta Sigo (jun/2026). Distinto da taxonomia de UTM/ID (`crv-`/`cmp-`/`adg-` do `taxonomia.yml` do vault), que é **tracking** — não confundir.

---

## Nível 1 — Campanha

**Sintaxe:** `{STATUS}_{CANAL}_{OBJ}_{PRODUTO}_{TEMP}`

| Campo | Valores aceitos |
|-------|----------------|
| STATUS | `HALL` (validada) · `TEST` (teste) · `EVER` (evergreen) |
| CANAL | `META` · `GOOG` · `LINK` · `TIKT` |
| OBJ | **Evento de conversão / estágio de funil que a campanha otimiza** — `LEAD` · `MQL` · `SAL` · `SQL` · `SALES` · `PURCHASE` · `TRFC` · `AWAR` · `MSNG`. ⚠️ **NÃO assumir `LEAD` por default** — use o evento realmente otimizado (ex.: campanha com form qualificador value-based otimiza **`MQL`**, não `LEAD`). |
| PRODUTO | CamelCase, sem espaços (ex: `SigoERP`, `CursoLongo`, `BootcampVendas`) |
| TEMP | **Temperatura da campanha:** `Frio` · `Morno` · `Quente` |

**Exemplos:** `EVER_META_SAL_SigoERP_Frio` (validado vivo Sigo jun/26) · `TEST_META_MQL_CursoLongo_Frio` (IGA Blumenau — fria, otimiza MQL) · `HALL_META_MQL_CursoLongo_Quente` (RMKT).

> **Correção 2026-07-05 (reconciliação com o SKILL.md — fonte vigente).** Versões anteriores desta ref traziam `{...}_{OBJETIVO}_{PRODUTO}_{DESTINO}` com OBJETIVO limitado a tipos de objetivo do Meta (`LEAD/SALES/...`) e um 5º campo de **destino** (`FormNativo/WhatsApp/...`). Isso **conflitava** com o SKILL.md (`..._{OBJ}_{PRODUTO}_{TEMP}`, ex. `EVER_META_SAL_SigoERP_Frio`) e induziu naming errado no caso IGA Blumenau (2026-07-02/05). Corrigido: **(a)** OBJ = evento/estágio de conversão real otimizado (não o tipo de objetivo Meta, e não `LEAD` por default); **(b)** 5º campo = **temperatura**, não destino. O **destino** (form nativo / WhatsApp / LP) é definido no `optimization_goal`/link do conjunto e anúncio — **não** entra no nome da campanha.

---

## Nível 2 — Conjunto de Anúncios

**Sintaxe:** `AUD-{HIERARQUIA}-{ID_SEQ}_{FUNIL}_{TIPO}_{PÚBLICO}_{GEO}_{DEMO}_{FORMATO}`

| Campo | Valores aceitos |
|-------|----------------|
| HIERARQUIA | Dígito 0–9 (ver tabela waterfall) |
| ID_SEQ | Sequencial 3 dígitos: `001`, `002`… |
| FUNIL | `COLD` · `WARM` · `HOT` |
| TIPO | `LAL` · `INT` · `RTG` · `CRM` · `BROAD` |
| PÚBLICO | CamelCase (ex: `Clientes`, `GerenteMktB2B`) |
| GEO | Código geográfico (ex: `BR`, `SP`, `LAM`) |
| DEMO | `{IDADEMIN}-{IDADEMAX}-{GENERO}` — Gênero: `M` · `F` · `HM` |
| FORMATO | `STA` · `VID` · `CAR` · `MOT` · `MIX` |

**Exemplo:** `AUD-7-001_COLD_LAL_Clientes_BR_25-60-HM_VID`

### Mapeamento temperatura → dígito (regra da cascata)

| Dígito | Temperatura | Tipo de público |
|--------|-------------|-----------------|
| 0 | BOF/Reativação | Clientes Ativos (CRM) |
| 1 | BOF/Reativação | Clientes Inativos (CRM) |
| 2 | BOF/Hot | SQLs (CRM) |
| 3 | MOF/Hot | MQLs (CRM) |
| 4 | MOF/Quente | Visitantes Site/LP (pixel) |
| 5 | MOF/Morno | Video View 50%+ / Assistiram Ads |
| 6 | MOF/Morno | Engajamento em Redes (curtidas, comments, follows) |
| 7 | TOF/Frio | Semelhantes/LAL (a partir de lista CRM ou pixel) |
| 8 | TOF/Frio | Direcionamento Detalhado / Interesses |
| 9 | TOF/Frio | Aberto / Broad |

---

## Nível 3 — Anúncio

**Sintaxe:** `AD-{ID_SEQ}_{FORMATO}_{CONSCIÊNCIA}_{GANCHO}_{AVATAR}_{VARIAÇÃO}`

| Campo | Valores aceitos |
|-------|----------------|
| ID_SEQ | Sequencial 3 dígitos: `001`, `015`… |
| FORMATO | `STA` · `VID` · `CAR` · `MOT` · `MIX` |
| CONSCIÊNCIA | `UNC` · `PRB` · `SOL` · `PRO` · `MIX` |
| GANCHO | `Loss` · `Proof` · `Story` · `Error` · `Fact` · `Contr` |
| AVATAR | CamelCase (ex: `CamilaFarani`, `FundadorV4`) |
| VARIAÇÃO | CamelCase, tema visual/headline (ex: `PerdendoDinheiro`, `Prova3xROI`) |

**Exemplo:** `AD-015_STA_UNC_Loss_CamilaFarani_PerdendoDinheiro`

> ⚠️ **Não confundir com a taxonomia de UTM/ID** (`crv-`/`cmp-`/`adg-` do `taxonomia.yml`): aquela é tracking (vai no `utm_content`/IDs do Growthpack), NÃO o nome da entidade no Ads Manager. O nome do anúncio aqui (`AD-`/`CRT-`) é o que aparece no gerenciador.

---

## Regra de Ouro

O nome de cada nível deve refletir produto/público pelos próprios campos da taxonomia (`PRODUTO`, `PÚBLICO`, `AVATAR`) — naming consistente é o que liga a estrutura à leitura de performance. (Sem dependência de `icp_product_map_id`/Supabase — infra legada removida na v2 MCP-only; validado vivo na conta Sigo jun/2026.)

---

## Naming hierárquico DCO (Dynamic Creative — extensão 2026)

> Este bloco cobre apenas o **naming** dos 2 níveis hierárquicos do DCO. A **doutrina estratégica** (por que agrupar por narrativa, regras operacionais, leitura por breakdowns, decisão DCO no início do MODO CRIAR) vive em [`estrutura-dco.md`](estrutura-dco.md). Os dois documentos se complementam — naming aqui, doutrina lá.

Quando o ad usa Dynamic Creative (DCO), surgem **2 camadas hierárquicas** que precisam de nomes distintos:

| Camada | Padrão | Onde fica |
|---|---|---|
| **Anúncio Meta (container DCO)** | `{DROP}_{ID_SEQ}_{FORMATO}_{NARRATIVA}_{CONSCIÊNCIA}_{GANCHO}_DCO` | Ads Manager (entidade Ad do Meta) |
| **Criativo (asset interno)** | `CRT-{ID_SEQ}_{FORMATO}_{CONSCIÊNCIA}_{GANCHO}_{AVATAR}_{VARIAÇÃO}__{Placement}.{ext}` | Disco do projeto / Asset Library do Meta |

### Sintaxe do anúncio container DCO

```
{DROP}_{ID_SEQ}_{FORMATO}_{NARRATIVA}_{CONSCIÊNCIA}_{GANCHO}_DCO
```

| Campo | Valores | Capitalização |
|---|---|---|
| `DROP` | `DM26` (Drop Maio 2026), `DJ26` (Junho 2026), etc — drop-rolling identifier | UPPER |
| `ID_SEQ` | `001`, `002`, `003`... sequencial 3 dígitos | numérico |
| `FORMATO` | `STA` · `VID` · `CAR` · `MOT` · `MIX` (se múltiplos formatos misturados) | UPPER |
| `NARRATIVA` | descritivo da hipótese de mensagem (ex: `DorObra`, `SolucaoAco`, `BelgoPronto`) | CamelCase |
| `CONSCIÊNCIA` | `PRB` · `SOL` · `PRO` · `UNC` · `MIX` (Schwartz; `MIX` quando varia entre criativos) | UPPER |
| `GANCHO` | `Loss` · `Fact` · `Proof` · `Story` · `Error` · `Contr` · `Mix` (TitleCase quando MIX pra distinguir do FORMATO) | TitleCase |
| `DCO` (sufixo fixo) | sempre presente — sinaliza container Dynamic Creative | UPPER |

**Capitalização proposital:** `MIX` (FORMATO, UPPER) ≠ `Mix` (GANCHO, TitleCase) — quando os 2 coexistirem no mesmo nome, capitalização distingue visualmente.

**Exemplos:**
- `DM26_001_MIX_DorObra_PRB_Loss_DCO` — drop maio, ad 001, mistura estático+vídeo, narrativa "Dor da Obra", problema-aware, gancho de aversão à perda
- `DM26_002_MIX_SolucaoAco_SOL_Mix_DCO` — drop maio, ad 002, mistura formatos, narrativa "Solução Aço", solução-aware, gancho misto (Contr+Fact)
- `DM26_003_VID_BelgoPronto_SOL_Fact_DCO` — drop maio, ad 003, só vídeo, narrativa "Belgo Pronto", solução-aware, gancho de fato/prova

### Sintaxe do criativo individual (asset interno)

Mesma taxonomia do anúncio single-creative (Nível 3 acima), mas com prefixo `CRT-` (em vez de `AD-`) pra evitar colisão semântica com o anúncio Meta. Adicionar sufixo `__{Placement}` antes da extensão:

```
CRT-{ID_SEQ}_{FORMATO}_{CONSCIÊNCIA}_{GANCHO}_{AVATAR}_{VARIAÇÃO}__{Placement}.{ext}
```

| Campo | Valores | Capitalização |
|---|---|---|
| `ID_SEQ` | sequencial único cross-projeto: `001`, `002`, etc | numérico |
| `FORMATO` | `STA` · `VID` · `CAR` · `MOT` (sempre concreto pro asset individual) | UPPER |
| `CONSCIÊNCIA` | `UNC` · `PRB` · `SOL` · `PRO` (sem `MIX` — asset individual tem 1 estágio) | UPPER |
| `GANCHO` | `Loss` · `Fact` · `Proof` · `Story` · `Error` · `Contr` (sem `Mix` — asset tem 1 gancho) | TitleCase |
| `AVATAR` | CamelCase (ex: `EngenheiroCivil`, `MestreEngObra`, `ConstrutoraPME`) | CamelCase |
| `VARIAÇÃO` | CamelCase, tema visual/headline | CamelCase |
| `Placement` | `Feed1x1` · `Stories9x16` · `Reels9x16` · `Marketplace1x1` · etc | TitleCase |

**Exemplos:**
- `CRT-001_STA_PRB_Loss_ConstrutoraPME_CorteErradoCustaCaro__Feed1x1.png`
- `CRT-007_VID_PRB_Loss_EngenheiroCivil_ChegaDeImprovisar__Stories9x16.mp4`

### Quando aplicar

- **Apenas para ads que usam DCO** (Padrão A ou B do framework Sobral). Single-creative segue a taxonomia de Nível 3 `AD-*`.
- Quando o operador mistura múltiplos `CRT-*` num único anúncio Meta → criar pasta no disco com o nome do container `{DROP}_{ID_SEQ}_..._DCO/` e colocar todos os assets dentro. Facilita upload no Meta + atribuição no relatório.
- Capitalização `MIX` vs `Mix` é proposital — não normalizar.

### Anti-padrões DCO (validação)

- ❌ `AD-001_DCO` — sem campos completos. Container DCO precisa de DROP + NARRATIVA + CONSCIÊNCIA + GANCHO mínimos.
- ❌ Container DCO sem narrativa nomeada — perde insight estratégico (qual mensagem ganhou).
- ❌ DROP missing — quando vier o próximo drop, não há como filtrar/arquivar antigo.
- ❌ Anúncio container Meta nomeado como `AD-*` — colide com criativo individual; usar prefixo `{DROP}_` em vez.
- ❌ Asset individual nomeado `AD-*` quando vai entrar em DCO — renomear pra `CRT-*` antes do upload.
