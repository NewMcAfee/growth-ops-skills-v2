# MODO ADICIONAR-CRIATIVOS — subir criativos em campanha/grupo existente

Fluxo para **adicionar anúncios a uma campanha/conjunto que já existe**, espelhando o padrão dos anúncios atuais. Não cria estrutura nova — usa a que está lá.

## Workflow

### 1. Mapear o existente (read-only)
```
ads_get_ad_entities (level=campaign, filtering name) → localiza a campanha-alvo + objetivo + status
ads_get_ad_entities (level=adset,    filtering campaign_id) → os conjuntos
ads_get_ad_entities (level=ad,       filtering campaign_id, fields inc. creative) → os ads + creative_id
ads_get_creatives (creative_ids=[...]) → o miolo dos creatives atuais
```
Extraia o **padrão**: object_type (imagem/vídeo/DCO), `body` (legenda) + `title` (headline) disponíveis, `call_to_action_type`, página (`effective_object_story_id` → page_id), Instagram conectado (`effective_instagram_media_id`).

### 2. Resolver o link de destino
O `link_url` costuma vir **vazio** na API quando o creative é um object_story (post). `ads_get_ad_preview` devolve um iframe **ofuscado** — não dá pra extrair a URL. **Peça o link + UTMs ao operador** (ele copia do campo "Site/URL" no Ads Manager). Não invente o destino.

### 3. Resolver as imagens (GOTCHA CRÍTICO)
**O MCP não faz upload de imagem.** `ads_create_creative` exige `image_hash` (pré-existente na conta) ou `image_url` (público). Dois caminhos:
- **Operador sobe na biblioteca** (Ads Manager → Recursos da conta → Imagens). A Meta **preserva o nome do arquivo** → você acha o hash por nome:
  ```
  ads_get_ad_images(name="<substring>", fields=["name","hash","width","height"])
  ```
- **Hospedar em URL pública** (ex.: servidor do cliente) e passar `image_url`.

### 4. Mapear criativo → conjunto + legenda
Cada criativo novo recebe a legenda/headline/CTA do **padrão existente** que melhor casa. **Confirme o mapa com o operador** antes de criar — você escolhe a melhor combinação, mas não inventa copy nova (se não houver legenda adequada, ofereça rodar `ad-copy-meta`, não escreva você).

### 5. Criar (PAUSED)
```
Para cada criativo:
  ads_create_creative(
    ad_account_id, page_id,
    image_hash=<hash>,                 # ou image_url=<url pública>
    link_url="https://.../?utm_source=...&utm_medium={{adset.name}}&utm_content={{ad.name}}&utm_id={{ad.id}}&utm_placement={{placement}}",
    message=<legenda>, headline=<headline>, call_to_action_type=<CTA>,
    instagram_user_id=<IG id>          # ver GOTCHA Instagram abaixo
  ) → creative_id

Para cada (criativo × conjunto-alvo):
  ads_create_ad(ad_set_id, ad_name=<CRT-...>, creative={"creative_id": <id>})  # nasce PAUSED
```
Reuse o **mesmo creative** em múltiplos conjuntos (igual o padrão de ads que se repetem entre conjuntos).

### 6. Validar
`ads_get_ad_preview(ad_id, MOBILE_FEED_STANDARD)` em ≥1 anúncio por narrativa — confirme imagem certa + legenda certa no anúncio certo.

### 7. Handoff
IDs criados + pendências (Instagram, ativação). Tudo segue PAUSED.

---

## Gotchas do MCP Meta (validados em produção)

| Gotcha | Contorno |
|---|---|
| **Sem upload de imagem** via MCP | Operador sobe na biblioteca (case hash por nome) ou URL pública (passo 3) |
| **Instagram via API instável** — `ads_get_ig_accounts` em rollout (pode falhar); o "Instagram account ID" da UI pode ser **rejeitado** por `instagram_user_id` (falta permissão `instagram_basic`) | Crie o creative **sem** `instagram_user_id` (entrega só Facebook) e oriente o operador a ligar o IG em **edição múltipla** no Ads Manager (dropdown "Perfil do Instagram"). Sinalize como pendência |
| **Sem placement customization** em `ads_create_creative` (1 imagem/anúncio; feed 4:5 + story 9:16 no mesmo ad exige Ads Manager) | Use a versão Feed (4:5) como o "1 imagem" (cobre todos os placements, igual ao padrão single-image). Stories ficam p/ placement customization manual |
| **`ads_update_entity` não renomeia creative** (só ad/ad_set/campaign) | O nome interno do creative na biblioteca não é editável por API; não afeta entrega/tracking. O nome do **anúncio** (`ad.name`) é o que vira `utm_content` |
| **Link com macros** `{{...}}` no `link_url` é aceito | OK passar a query string completa com `{{adset.name}}`/`{{ad.name}}`/`{{ad.id}}`/`{{placement}}` |
| Link de destino não extraível da API (object_story) | Peça ao operador (passo 2) |

---

## Exemplo de referência (Onco Import, drop jun/2026)

Sessão real que originou este modo: 8 anúncios adicionados a `V4_TEST_META_LEAD_CotacaoPaciente` (2 conjuntos × 4 conceitos), 100% via MCP.
- 4 criativos de feed → hashes casados por nome (operador subiu na biblioteca).
- Legendas reusadas: havia 2 bodies distintos (jurídico × paciente) → mapeados por narrativa.
- IG `instagram_user_id` rejeitado → criados só com FB, IG ligado depois via Ads Manager.
- Link confirmado pelo operador: `https://oncoimport.com.br/lp/cotacao-paciente/` + UTMs com macros.
- Naming dos anúncios no padrão de entidade `CRT-...` (não `crv-`, que é UTM/tracking — erro comum, ver `taxonomia-entidade-meta.md`).

> Este exemplo é ilustrativo. A skill é genérica — parametrize conta, campanha, narrativas e legendas por projeto.
