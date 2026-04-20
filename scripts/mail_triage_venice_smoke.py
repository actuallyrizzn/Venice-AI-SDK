#!/usr/bin/env python3
"""
Mini Venice benchmark for mailbox triage (JSON buckets) + one enrichment stub.

Loads VENICE_API_KEY from the environment (optionally dotenv from repo root).
Does not print secrets.

Usage (from repo root):
  set -a && [ -f .env ] && . ./.env && set +a && python3 scripts/mail_triage_venice_smoke.py

Offline (no API; validates JSON parsing + gold-label scorers):
  python3 scripts/mail_triage_venice_smoke.py --offline
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

BASE = os.environ.get("VENICE_API_BASE", "https://api.venice.ai/api/v1").rstrip("/")


def _infer_key_from_venice_key_md(path: str) -> str:
    """Parse `VENICE_IMAGE_ANALYSIS_API_KEY=...` from athena-venice-usage/venice_key.md."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("VENICE_IMAGE_ANALYSIS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def _default_workspace_venice_key_md() -> str:
    """projects/athena-venice-usage/venice_key.md relative to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(
        os.path.join(here, "..", "..", "athena-venice-usage", "venice_key.md")
    )


def _load_key() -> str:
    env = (os.environ.get("VENICE_API_KEY") or "").strip()
    file_key = ""
    auto = _default_workspace_venice_key_md()
    if os.path.isfile(auto):
        file_key = _infer_key_from_venice_key_md(auto)
    # Short values in .env are often placeholders; prefer workspace inference key.
    if file_key and len(env) < 24:
        return file_key
    if env:
        return env
    path = (os.environ.get("VENICE_API_KEY_FILE") or "").strip()
    if path and os.path.isfile(path):
        raw = open(path, "r", encoding="utf-8").read().strip()
        if "VENICE_IMAGE_ANALYSIS_API_KEY=" in raw or "VENICE_API_KEY=" in raw:
            k = _infer_key_from_venice_key_md(path)
            if k:
                return k
        return raw
    if file_key:
        return file_key
    return ""


def _strip_fences(text: str) -> str:
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", t, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    t = _strip_fences(text)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _triage_prompt() -> Tuple[str, str]:
    system = (
        "You classify email snippets. Reply with ONLY a JSON object, no markdown, "
        "no commentary. Schema: "
        '{"results":[{"id":int,"bucket":str,"confidence":number}]} '
        'where bucket is one of: person, list, promo, transactional.'
    )
    user = """Classify each snippet (id matches order).

1) From: Sarah Chen <sarah.chen@acmecorp.com> Subject: Re: Q4 roadmap — quick sync Thursday?
   Body preview: Can we do 3pm your time? I'll send a calendar hold.

2) From: deals@megastore.com Subject: 🔥 48 HOUR FLASH — 60% off everything
   Body preview: Unsubscribe | View in browser | Shop now

3) From: GitHub <noreply@github.com> Subject: [org/repo] Issue #442 closed: fix login redirect
   Body preview: This issue was closed by dependabot[bot].

Return JSON only, shape: {"results":[{"id":1,"bucket":"...","confidence":0.0-1.0}, ...]}"""
    return system, user


def _enrichment_prompt() -> Tuple[str, str]:
    system = (
        "Extract structured facts from an email thread excerpt. "
        "Reply with ONLY JSON: "
        '{"contact_name":str|null,"organization":str|null,"relationship_hint":str|null,'
        '"topics":["..."]}'
    )
    user = """Thread excerpt:

From: Jordan Lee <jordan@initech.com>
To: you
Subject: intro — data pipeline contractor

Hey — I'm the eng manager for billing. We're looking for someone who has done
Postgres CDC → Kafka before. Are you free for a 20m call next Tuesday?

Return JSON only."""
    return system, user


def chat_once(
    session: requests.Session,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.1,
) -> Tuple[int, Dict[str, Any], float]:
    url = f"{BASE}/chat/completions"
    t0 = time.perf_counter()
    r = session.post(
        url,
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=120,
    )
    elapsed = time.perf_counter() - t0
    try:
        data = r.json()
    except Exception:
        data = {"error": "non-json", "text": r.text[:500]}
    return r.status_code, data, elapsed


def score_triage(obj: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not obj:
        return False, "not_json_object"
    results = obj.get("results")
    if not isinstance(results, list) or len(results) != 3:
        return False, "bad_results_len"
    expected = {1: "person", 2: "promo", 3: "transactional"}
    for i, row in enumerate(results):
        if not isinstance(row, dict):
            return False, f"row_{i}_not_object"
        rid = row.get("id")
        bucket = row.get("bucket")
        conf = row.get("confidence")
        if rid not in expected:
            return False, f"bad_id_{rid}"
        if bucket != expected[int(rid)]:
            return False, f"id_{rid}_want_{expected[int(rid)]}_got_{bucket}"
        if not isinstance(conf, (int, float)):
            return False, f"id_{rid}_bad_confidence"
    return True, "ok"


def score_enrichment(obj: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not obj:
        return False, "not_json_object"
    for k in ("contact_name", "organization", "relationship_hint", "topics"):
        if k not in obj:
            return False, f"missing_{k}"
    if obj.get("contact_name") and "Jordan" not in str(obj["contact_name"]):
        return False, "contact_name_unexpected"
    org = obj.get("organization")
    if org and "initech" not in str(org).lower():
        return False, "organization_unexpected"
    topics = obj.get("topics")
    if not isinstance(topics, list):
        return False, "topics_not_list"
    return True, "ok"


def run_offline_selfcheck() -> int:
    """Validate parsers/scorers with canned assistant strings (no HTTP)."""
    triage_sys, triage_user = _triage_prompt()
    assert "person" in triage_sys

    good_triage = json.dumps(
        {
            "results": [
                {"id": 1, "bucket": "person", "confidence": 0.92},
                {"id": 2, "bucket": "promo", "confidence": 0.88},
                {"id": 3, "bucket": "transactional", "confidence": 0.81},
            ]
        }
    )
    ok, reason = score_triage(_parse_json_object(good_triage))
    assert ok, reason

    fenced = "```json\n" + good_triage + "\n```"
    ok2, _ = score_triage(_parse_json_object(fenced))
    assert ok2, "fence_strip"

    enrich_sys, enrich_user = _enrichment_prompt()
    assert "Jordan" in enrich_user
    good_enrich = json.dumps(
        {
            "contact_name": "Jordan Lee",
            "organization": "initech.com",
            "relationship_hint": "hiring manager outreach",
            "topics": ["Postgres CDC", "Kafka", "contract"],
        }
    )
    ok3, er = score_enrichment(_parse_json_object(good_enrich))
    assert ok3, er

    bad = '{"results":[{"id":1,"bucket":"list"}]}'  # wrong gold
    ok4, _ = score_triage(_parse_json_object(bad))
    assert not ok4

    print("OFFLINE_OK\tparse_json\tscore_triage\tscore_enrichment\tnegative_control")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Venice mail triage mini-benchmark")
    ap.add_argument(
        "--offline",
        action="store_true",
        help="Run JSON/scorer self-check only (no API calls).",
    )
    args = ap.parse_args()
    if args.offline:
        return run_offline_selfcheck()

    # Optional: load .env from repo root (parent of scripts/)
    try:
        from dotenv import load_dotenv

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        load_dotenv(os.path.join(root, ".env"))
    except Exception:
        pass

    key = _load_key()
    if not key:
        print(
            "Missing VENICE_API_KEY. Set env, or VENICE_API_KEY_FILE, or place "
            "projects/athena-venice-usage/venice_key.md with VENICE_IMAGE_ANALYSIS_API_KEY.",
            file=sys.stderr,
        )
        return 2

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    )

    triage_sys, triage_user = _triage_prompt()
    enrich_sys, enrich_user = _enrichment_prompt()

    triage_models = [
        "qwen3-5-9b",
        "openai-gpt-oss-120b",
        "nvidia-nemotron-3-nano-30b-a3b",
        "mistral-small-3-2-24b-instruct",
        "google-gemma-3-27b-it",
    ]
    enrich_models = ["mistral-small-3-2-24b-instruct", "deepseek-v3.2"]

    rows: List[Dict[str, Any]] = []

    print("=== Triage (JSON shape + gold buckets) ===")
    for model in triage_models:
        status, data, elapsed = chat_once(
            session,
            model,
            [
                {"role": "system", "content": triage_sys},
                {"role": "user", "content": triage_user},
            ],
        )
        content = ""
        if status == 200 and isinstance(data, dict):
            choices = data.get("choices") or []
            if choices:
                msg = choices[0].get("message") or {}
                content = (msg.get("content") or "").strip()
        usage = data.get("usage") if isinstance(data, dict) else {}
        pt = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        ct = usage.get("completion_tokens") if isinstance(usage, dict) else None
        tt = usage.get("total_tokens") if isinstance(usage, dict) else None
        parsed = _parse_json_object(content) if content else None
        ok, reason = score_triage(parsed)
        err = None if status == 200 else (data.get("error") if isinstance(data, dict) else data)
        rows.append(
            {
                "phase": "triage",
                "model": model,
                "http": status,
                "seconds": round(elapsed, 3),
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "total_tokens": tt,
                "json_ok": ok,
                "reason": reason if not ok else "",
                "error": err,
            }
        )
        flag = "PASS" if ok else "FAIL"
        print(
            f"{flag}\t{model}\t{elapsed:.2f}s\ttokens={tt}\tpt={pt}\tct={ct}\t{reason or 'ok'}"
        )
        if status != 200:
            print(f"  http_error={err}")
            if status == 401:
                print(
                    "  hint: generate a key at https://venice.ai/settings/api "
                    "and export VENICE_API_KEY (or fix .env).",
                    file=sys.stderr,
                )

    print()
    print("=== Enrichment (structured extract) ===")
    for model in enrich_models:
        status, data, elapsed = chat_once(
            session,
            model,
            [
                {"role": "system", "content": enrich_sys},
                {"role": "user", "content": enrich_user},
            ],
            max_tokens=1024,
        )
        content = ""
        if status == 200 and isinstance(data, dict):
            choices = data.get("choices") or []
            if choices:
                msg = choices[0].get("message") or {}
                content = (msg.get("content") or "").strip()
        usage = data.get("usage") if isinstance(data, dict) else {}
        pt = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        ct = usage.get("completion_tokens") if isinstance(usage, dict) else None
        tt = usage.get("total_tokens") if isinstance(usage, dict) else None
        parsed = _parse_json_object(content) if content else None
        ok, reason = score_enrichment(parsed)
        err = None if status == 200 else (data.get("error") if isinstance(data, dict) else data)
        rows.append(
            {
                "phase": "enrichment",
                "model": model,
                "http": status,
                "seconds": round(elapsed, 3),
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "total_tokens": tt,
                "json_ok": ok,
                "reason": reason if not ok else "",
                "error": err,
            }
        )
        flag = "PASS" if ok else "FAIL"
        print(
            f"{flag}\t{model}\t{elapsed:.2f}s\ttokens={tt}\tpt={pt}\tct={ct}\t{reason or 'ok'}"
        )
        if status != 200:
            print(f"  http_error={err}")

    out_path = os.path.join(os.path.dirname(__file__), "mail_triage_venice_smoke_last.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print()
    print(f"Wrote {out_path}")

    auth_fail = any(r.get("http") == 401 for r in rows)
    if auth_fail:
        return 3

    triage_pass = [r for r in rows if r["phase"] == "triage" and r.get("json_ok")]
    if triage_pass:
        best = min(
            triage_pass,
            key=lambda r: (
                r.get("total_tokens") is None,
                r.get("total_tokens") or 10**9,
                r.get("seconds") or 999,
            ),
        )
        print()
        print(
            "RECOMMENDED_TRIAGE_MODEL\t"
            f"{best['model']}\tseconds={best['seconds']}\ttokens={best.get('total_tokens')}"
        )
    enrich_pass = [r for r in rows if r["phase"] == "enrichment" and r.get("json_ok")]
    if enrich_pass:
        best_e = min(
            enrich_pass,
            key=lambda r: (
                r.get("total_tokens") is None,
                r.get("total_tokens") or 10**9,
                r.get("seconds") or 999,
            ),
        )
        print(
            "RECOMMENDED_ENRICHMENT_MODEL\t"
            f"{best_e['model']}\tseconds={best_e['seconds']}\ttokens={best_e.get('total_tokens')}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
