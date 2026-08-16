"""Typed payloads, multimodal chat messages, and x402 wallet-signer flow."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from venice_sdk.audio import TranscriptionResult, AudioAPI
from venice_sdk.augment import (
    AugmentAPI,
    SearchHit,
    SearchResponse,
    ScrapeResponse,
    ParsedDocument,
)
from venice_sdk.chat import ChatAPI, Message
from venice_sdk.responses import Response, ResponseOutputItem, ResponsesAPI, _output_item_text
from venice_sdk.x402 import (
    X402API,
    X402Balance,
    X402TopUpResult,
    X402Transactions,
    build_payment_payload,
    encode_payment_signature,
    decode_payment_signature,
    _invoke_signer,
)


class TestResponseTyping:
    def test_output_item_text_shapes(self):
        assert _output_item_text(None) == ""
        assert _output_item_text("hi") == "hi"
        assert _output_item_text({"text": "a"}) == "a"
        assert _output_item_text({"output_text": "b"}) == "b"
        assert _output_item_text({"content": "c"}) == "c"
        assert _output_item_text({"content": {"text": "nested"}}) == "nested"
        assert _output_item_text([{"type": "output_text", "text": "x"}, {"text": "y"}]) == "xy"
        assert _output_item_text(12) == "12"
        item = ResponseOutputItem.from_dict("nope")
        assert item.type == "unknown"
        assert item.text() == "nope"

    def test_response_from_dict_variants(self):
        empty = Response.from_dict("x")
        assert empty.id == ""
        parsed = Response.from_dict(
            {
                "id": "r1",
                "created": 9,
                "model": "m",
                "status": "completed",
                "choices": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "hello"}],
                    }
                ],
                "usage": {"input_tokens": 1},
            }
        )
        assert parsed.id == "r1"
        assert parsed.created_at == 9
        assert parsed.output_text == "hello"
        assert parsed.usage["input_tokens"] == 1
        no_list = Response.from_dict({"id": "r2", "output": {"not": "list"}})
        assert no_list.output == []

    def test_create_parses_output_array(self):
        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {
            "id": "resp",
            "created_at": 1,
            "output": [{"type": "message", "content": "done", "id": "o1", "status": "ok"}],
        }
        out = ResponsesAPI(mock_client).create("m", "hi")
        assert out.output_text == "done"
        assert out.output[0].id == "o1"


class TestAugmentTyping:
    def test_search_hit_and_response_shapes(self):
        hit = SearchHit.from_dict("bare")
        assert hit.snippet == "bare"
        nested = SearchResponse.from_dict(
            {
                "query": "q",
                "provider": "brave",
                "data": [{"title": "T", "link": "https://x", "description": "d"}],
            }
        )
        assert nested.results[0].title == "T"
        assert nested.results[0].url == "https://x"
        organic = SearchResponse.from_dict({"organic": [{"name": "N", "href": "h"}]}, query="fallback")
        assert organic.query == "fallback"
        assert organic.results[0].title == "N"
        not_list = SearchResponse.from_dict({"results": {"oops": True}})
        assert not_list.results == []
        markdown_doc = ParsedDocument.from_dict({"markdown": "md"})
        assert markdown_doc.text == "md"
        weird = SearchResponse.from_dict(None, query="q")
        assert weird.query == "q"

    def test_scrape_and_parse_shapes(self):
        scraped = ScrapeResponse.from_dict("md", url="https://a")
        assert scraped.markdown == "md"
        scraped2 = ScrapeResponse.from_dict({"content": "# h", "title": "Hi", "url": "https://b"})
        assert scraped2.markdown.startswith("#")
        empty = ScrapeResponse.from_dict({})
        assert empty.markdown == ""
        parsed = ParsedDocument.from_dict("plain")
        assert parsed.text == "plain"
        parsed2 = ParsedDocument.from_dict({"content": "c", "filename": "f.txt"})
        assert parsed2.text == "c"
        parsed3 = ParsedDocument.from_dict(123)
        assert parsed3.text == "123"

    def test_search_provider_and_organic_via_api(self):
        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {"organic": [{"title": "A", "url": "u"}]}
        out = AugmentAPI(mock_client).search("hello")
        assert len(out.results) == 1


class TestTranscriptionTyping:
    def test_from_dict_variants(self):
        assert TranscriptionResult.from_dict("hi").text == "hi"
        assert TranscriptionResult.from_dict(None).text == ""
        tr = TranscriptionResult.from_dict(
            {
                "transcription": "spoken",
                "language": "en",
                "duration": "1.5",
                "segments": [{"start": 0}],
                "words": [{"word": "spoken"}],
            }
        )
        assert TranscriptionResult.from_dict({"transcript": "alt"}).text == "alt"
        assert tr.duration == 1.5
        assert tr.segments and tr.words
        bad_dur = TranscriptionResult.from_dict({"text": "x", "duration": "nope"})
        assert bad_dur.duration is None

    def test_audio_json_returns_typed(self):
        mock_client = MagicMock()
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"text": "hello", "language": "en"}
        mock_client.post_multipart.return_value = resp
        out = AudioAPI(mock_client).transcribe(b"wav", model="whisper")
        assert isinstance(out, TranscriptionResult)
        assert out.language == "en"


class TestX402WalletFlow:
    def test_payload_and_signature_roundtrip(self):
        payload = build_payment_payload(
            network="base",
            amount=10,
            pay_to="0xabc",
            asset="USDC",
            extra={"nonce": "1"},
        )
        assert payload["payTo"] == "0xabc"
        assert payload["nonce"] == "1"
        encoded = encode_payment_signature(payload)
        assert decode_payment_signature(encoded)["network"] == "base"
        with pytest.raises(ValueError):
            build_payment_payload(network=" ", amount="1", pay_to="0x")
        with pytest.raises(ValueError):
            build_payment_payload(network="base", amount=None, pay_to="0x")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            build_payment_payload(network="base", amount="1", pay_to="")
        with pytest.raises(ValueError):
            encode_payment_signature({})
        with pytest.raises(ValueError):
            decode_payment_signature("")
        with pytest.raises(ValueError):
            decode_payment_signature("!!!!")
        with pytest.raises(ValueError):
            decode_payment_signature(__import__("base64").b64encode(b"[1]").decode())

    def test_typed_from_dict_and_signer(self):
        assert X402Balance.from_dict(5, wallet_address="0x1").balance == 5
        bal = X402Balance.from_dict({"walletAddress": "0x2", "credits": 9})
        assert bal.wallet_address == "0x2"
        assert bal.balance == 9
        top = X402TopUpResult.from_dict("x")
        assert top.raw["value"] == "x"
        top2 = X402TopUpResult.from_dict({"ok": True, "transactionId": "tx1"})
        assert top2.success is True
        assert top2.transaction_id == "tx1"
        top3 = X402TopUpResult.from_dict({"id": "i"})
        assert top3.transaction_id == "i"
        tx = X402Transactions.from_dict([1], wallet_address="0x")
        assert tx.transactions == [1]
        tx2 = X402Transactions.from_dict({"wallet_address": "0x3", "data": [{"id": 1}]})
        assert tx2.wallet_address == "0x3"
        assert tx2.transactions == [{"id": 1}]

        class Wallet:
            def sign_payment(self, payload):
                return encode_payment_signature(payload)

        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {"success": True, "id": "t"}
        api = X402API(mock_client)
        result = api.top_up_with_signer(
            Wallet(),
            network="base",
            amount="1",
            pay_to="0xpay",
            asset="USDC",
            extra={"n": 1},
            body={"note": "hi"},
        )
        assert result.success is True
        assert mock_client.post.call_args.kwargs["headers"]["PAYMENT-SIGNATURE"]

        api.top_up_with_signer(lambda payload: "sig-from-fn", network="base", amount=1, pay_to="0x")
        assert mock_client.post.call_args.kwargs["headers"]["PAYMENT-SIGNATURE"] == "sig-from-fn"

        with pytest.raises(TypeError):
            _invoke_signer(object(), {"a": 1})
        with pytest.raises(ValueError):
            _invoke_signer(lambda p: "", {"a": 1})
        with pytest.raises(ValueError):
            _invoke_signer(lambda p: 12, {"a": 1})  # type: ignore[arg-type, return-value]


class TestMultimodalMessages:
    def test_text_content_and_roundtrip(self):
        assert Message(role="user").text_content() == ""
        assert Message(role="user", content="hi").text_content() == "hi"
        msg = Message(
            role="user",
            content=[
                {"type": "text", "text": "look "},
                {"type": "image_url", "image_url": {"url": "https://x"}},
                {"text": "please"},
                "skip",
            ],
        )
        assert msg.text_content() == "look please"
        payload = msg.to_dict()
        assert payload["content"][0]["type"] == "text"
        cloned = Message.from_dict(
            {
                "role": "assistant",
                "content": "ok",
                "name": "bot",
                "tool_call_id": "t1",
                "tool_calls": [{"id": "1"}],
            }
        )
        dumped = cloned.to_dict()
        assert dumped["name"] == "bot"
        assert dumped["tool_calls"]
        with pytest.raises(ValueError):
            Message.from_dict("nope")  # type: ignore[arg-type]

    def test_complete_accepts_message_and_parts(self):
        mock_client = MagicMock()
        mock_client.post.return_value.json.return_value = {"id": "c"}
        api = ChatAPI(mock_client)
        api.complete(
            [
                Message(role="user", content="hi"),
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "see"},
                        {"type": "image_url", "image_url": {"url": "https://img"}},
                        {"type": "input_audio", "input_audio": {"data": "aaa"}},
                        {"type": "video_url", "video_url": {"url": "https://v"}},
                    ],
                },
            ]
        )
        sent = mock_client.post.call_args.kwargs["data"]["messages"]
        assert sent[0]["content"] == "hi"
        assert sent[1]["content"][1]["type"] == "image_url"

        with pytest.raises(ValueError, match="dictionary or Message"):
            api.complete(["nope"])  # type: ignore[list-item]
        with pytest.raises(ValueError, match="string or a list"):
            api.complete([{"role": "user", "content": 12}])
        with pytest.raises(ValueError, match="must be an object"):
            api.complete([{"role": "user", "content": ["x"]}])
        with pytest.raises(ValueError, match="type"):
            api.complete([{"role": "user", "content": [{"text": "x"}]}])
        with pytest.raises(ValueError, match="unsupported type"):
            api.complete([{"role": "user", "content": [{"type": "file"}]}])
