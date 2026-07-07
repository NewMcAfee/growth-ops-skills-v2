# CSV Google Ads Editor — Performance Max (PMax)

## Diferenças fundamentais do PMax em relação a Search/Display

| Aspecto | Search/Display | PMax |
|---------|---------------|------|
| Nível 2 | Ad Groups | Asset Groups |
| Keywords | Sim | Não (usa Search Themes) |
| Anúncios | RSA, Expanded Text | Assets individuais (não linhas de RSA) |
| Campaign type | `Search Network` | `Performance max` |
| Controle | Alto | Baixo (confia no algoritmo) |

**PMax não tem linhas de Ad Group nem de Keyword no CSV.** Tem linhas de Asset Group e linhas de assets individuais (headlines, descriptions, images, videos).

---

## Quando usar PMax

- Conta com **30+ conversões/mês** (mínimo para o algoritmo aprender)
- Objetivo é maximizar conversões em múltiplos canais com um único setup
- Estratégia do Sobral indicou explicitamente PMax

**Se a conta for nova (0 conversões): use Search, não PMax.**

---

## Cabeçalho CSV para PMax

```
Campaign,Campaign type,Campaign status,Budget,Bid strategy type,Target CPA,Target ROAS,Languages,Location,Asset group,Asset group status,Final URL,Headline 1,Headline 2,Headline 3,Headline 4,Headline 5,Headline 6,Headline 7,Headline 8,Headline 9,Headline 10,Headline 11,Headline 12,Headline 13,Headline 14,Headline 15,Long headline 1,Long headline 2,Long headline 3,Long headline 4,Long headline 5,Description 1,Description 2,Description 3,Description 4,Description 5,Business name,Search theme 1,Search theme 2,Search theme 3,Search theme 4,Search theme 5,Search theme 6,Search theme 7,Search theme 8,Search theme 9,Search theme 10
```

---

## Linha de Campanha PMax

| Coluna | Valor | Notas |
|--------|-------|-------|
| `Campaign` | `TEST_GOOG_LEAD_ProdutoX_LandingPage` | Taxonomia Dante — mesmo padrão |
| `Campaign type` | `Performance max` | Exato — p minúsculo em "max" |
| `Campaign status` | `Enabled` | |
| `Budget` | `100` | Valor diário — sem símbolo |
| `Bid strategy type` | `Maximize conversions` ou `Target CPA` ou `Target ROAS` | |
| `Target CPA` | `150` | Apenas se Bid strategy = Target CPA |
| `Target ROAS` | `3.5` | Apenas se Bid strategy = Target ROAS |
| `Languages` | `Portuguese (Brazil)` | |
| `Location` | `Brazil` | |

Exemplo:
```
TEST_GOOG_LEAD_BootcampVendas_LandingPage,Performance max,Enabled,100,Maximize conversions,,,Portuguese (Brazil),Brazil,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
```

---

## Linha de Asset Group

| Coluna | Valor | Notas |
|--------|-------|-------|
| `Campaign` | nome da campanha pai | |
| `Asset group` | `AGP-ICP-A-PROD-1_IcpPrincipal_001` | Nomenclatura Dante PMax |
| `Asset group status` | `Enabled` | |
| `Final URL` | `https://site.com/pagina` | URL da landing page |

**Nomenclatura Asset Group:** `AGP-[ICP_REF]-[PROD_REF]_[TEMA]_[N]`
- Ex: `AGP-ICP-A-PROD-1_GestoresVendas_001`
- Ex: `AGP-ICP-B-PROD-1_DiretoresComerciais_001`

Cada Asset Group deve mapear para exatamente uma combinação `icp_product_map`.

---

## Assets no Asset Group

**Headlines (Títulos curtos):** mínimo 3, máximo 15 — até 30 chars cada
**Long Headlines (Títulos longos):** mínimo 1, máximo 5 — até 90 chars cada  
**Descriptions:** mínimo 2, máximo 5 — até 90 chars cada
**Business name:** Nome da empresa/marca — até 25 chars

Esses campos ficam na **mesma linha** do Asset Group:

```
TEST_GOOG_LEAD_BootcampVendas_LandingPage,,,,,,,,,,AGP-ICP-A-PROD-1_GestoresVendas_001,Enabled,https://site.com/bootcamp,Título 1,Título 2,Título 3,Título 4,Título 5,Título 6,Título 7,Título 8,,,,,,,Headline longa 1 aqui,Headline longa 2 aqui,,,Descrição 1,Descrição 2,Descrição 3,Descrição 4,,NomeDaMarca,buscar bootcamp vendas,treinamento vendas b2b,curso vendas online,bootcamp comercial,fechar mais clientes,,,,
```

---

## Search Themes (crucial para PMax)

Search Themes funcionam como "sinais" para o algoritmo de PMax — não são keywords exatas, mas direcionam o tipo de busca que o grupo deve capturar. Cada Asset Group suporta até **25 Search Themes**.

**Como definir os Search Themes:**
- Use as keywords identificadas pelo Sobral (estratégia SEM)
- Foque em intenções mid e bottom of funnel
- Prefira temas com alta relevância para o ICP da combinação
- Evite temas genéricos demais (ex: "vendas") — preferir "bootcamp de vendas b2b"

Os Search Themes aparecem nas colunas `Search theme 1` até `Search theme 25` (ou quantas o cabeçalho suportar) na linha do Asset Group.

---

## Negative Keywords em PMax

**Atenção:** O Google Ads Editor **não suporta adição de negative keywords a nível de campanha PMax via CSV** na maioria das versões. Negative keywords para PMax precisam ser configuradas como:
1. **Account-level negative keyword lists** (listas de negativas da conta) — aplicáveis a PMax
2. Configuradas diretamente na interface web do Google Ads

Documente no documento explicativo que o operador precisa adicionar as negativas manualmente.

---

## Template PMax Completo — Exemplo

```csv
Campaign,Campaign type,Campaign status,Budget,Bid strategy type,Languages,Location,Asset group,Asset group status,Final URL,Headline 1,Headline 2,Headline 3,Headline 4,Headline 5,Headline 6,Headline 7,Headline 8,Long headline 1,Long headline 2,Description 1,Description 2,Description 3,Description 4,Business name,Search theme 1,Search theme 2,Search theme 3,Search theme 4,Search theme 5
TEST_GOOG_LEAD_BootcampVendas_LandingPage,Performance max,Enabled,100,Maximize conversions,Portuguese (Brazil),Brazil,,,,,,,,,,,,,,,,,,,,,,,,,
TEST_GOOG_LEAD_BootcampVendas_LandingPage,,,,,,,,AGP-ICP-A-PROD-1_GestoresVendas_001,Enabled,https://site.com/bootcamp,Título 1,Título 2,Título 3,Título 4,Título 5,Título 6,Título 7,Título 8,Headline longa completa 1,Headline longa completa 2,Descrição 1 aqui,Descrição 2 aqui,Descrição 3 aqui,Descrição 4 aqui,Empresa,bootcamp vendas b2b,treinamento equipe vendas,como aumentar conversão,fechar contratos b2b,gestor de vendas
```

---

## Checklist PMax antes de salvar

- [ ] `Campaign type` = `Performance max` (p minúsculo em "max")
- [ ] Sem colunas `Ad group`, `Keyword`, `Criterion type` preenchidas
- [ ] Cada Asset Group mapeado a uma combinação icp_product_map
- [ ] Asset Group com mínimo 3 headlines, 1 long headline, 2 descriptions
- [ ] Search Themes refletem as keywords do Sobral
- [ ] Nota no documento explicativo sobre negativas manuais
- [ ] Conta tem 30+ conversões/mês (documentar se não tiver)
