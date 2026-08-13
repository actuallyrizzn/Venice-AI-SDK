# Venice API ↔ SDK parity gap (2026-08-13)

Source of truth: `https://docs.venice.ai/swagger.yaml` (45 paths) + live probes with inference key.

**Status:** SDK **0.3.1** brings endpoint coverage to full OpenAPI path parity (client surfaces for every swagger path). Residual work is depth (response typing, richer parsers, live integration tests), not missing routes.

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

## Follow-ups (depth, not missing paths)

- Stronger typed response models for Responses / Augment / STT payloads
- Live integration tests for new routes
- Chat `Message` dataclass still types `content: str` (runtime accepts multimodal lists)
- x402 top-up still needs a real payment signature from wallet flow
