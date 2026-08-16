# Venice API ↔ SDK parity gap (2026-08-13)

Source of truth: `https://docs.venice.ai/swagger.yaml` (45 paths) + live probes with inference key.

**Status:** SDK **0.3.2** keeps full OpenAPI path parity and closes the 0.3.1 depth follow-ups (typed payloads, multimodal `Message.content`, x402 wallet-signer flow, live tests for new routes).

## P0 — fixed in 0.3.1

| Was | Now |
|-----|-----|
| `POST /images/upscale` (404) | `POST /image/upscale` |
| `GET /images/styles` (404) | `GET /image/styles` |
| `GET /billing/summary` (404) | `GET /billing/balance` (+ analytics/history methods) |
| Traits comment claimed endpoint missing | `ModelsTraitsAPI.get_trait_categories()` → `/models/traits` |

## Client surface map (0.3.1)

| Path | SDK |
|------|-----|
| `/chat/completions` | `client.chat` |
| `/responses` | `client.responses` |
| `/images/generations` | `client.images.generate` |
| `/image/generate` | `client.images.generate_native` |
| `/image/edit|multi-edit|background-remove` | `client.image_edit` |
| `/image/upscale` | `client.image_upscale` |
| `/image/styles` | `client.image_styles` |
| `/audio/speech` | `client.audio.speech*` |
| `/audio/transcriptions` | `client.audio.transcribe` |
| `/audio/voices` | `client.audio.clone_voice` |
| `/audio/queue|retrieve|quote|complete` | `client.music` |
| `/video/queue|retrieve|quote|complete` | `client.video` |
| `/video/transcriptions` | `client.video.transcribe` |
| `/embeddings` | `client.embeddings` |
| `/models`, `/models/traits`, `/models/compatibility_mapping` | `client.models*` |
| `/characters*`, `/characters/{slug}/reviews` | `client.characters` |
| `/api_keys*` | `client.api_keys` |
| `/billing/usage|balance|usage-analytics|usage-history` | `client.billing` |
| `/augment/search|scrape|text-parser` | `client.augment` |
| `/crypto/rpc/networks`, `/crypto/rpc/{network}` | `client.crypto` |
| `/x402/*` | `client.x402` |
| `/tee/*` (live, not in swagger) | `client.tee` |

## Follow-ups (closed in 0.3.2)

- Typed response models for Responses / Augment / STT / x402 — `.raw` keeps the original JSON
- Live tests for new routes: `tests/live/test_new_routes_live.py` (enable with `VENICE_LIVE_TESTS=1`)
- Chat `Message.content` is `Optional[str | list[content-part]]`; `complete()` accepts `Message` objects
- x402 top-up: `top_up_with_signer()` + `build_payment_payload()` — signature still comes from a wallet, not the SDK
