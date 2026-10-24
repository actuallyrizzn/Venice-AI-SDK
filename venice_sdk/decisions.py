"""
Venice AI SDK - Jev Decisions API (Beta).

``POST /decisions`` evaluates a state against typed questions and returns
structured answers (noul / choice / score), not generated text.

``POST /systemone`` is the same handler (TypeSafe SDK drop-in alias).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient
from .endpoints import DecisionsEndpoints

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]
DecisionState = Union[str, JSONDict, List[Any]]
DecisionImages = Optional[List[Union[str, JSONDict]]]


@dataclass
class DecisionAnswer:
    """One typed answer from ``POST /decisions``."""

    type: str
    noul: Optional[float] = None
    choice: Optional[str] = None
    score: Optional[float] = None
    probabilities: Optional[JSONDict] = None
    confidence: Optional[float] = None
    legend: Optional[JSONDict] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any) -> "DecisionAnswer":
        if not isinstance(data, dict):
            return cls(type="unknown", raw={"value": data})
        noul = data.get("noul")
        score = data.get("score")
        confidence = data.get("confidence")
        return cls(
            type=str(data.get("type") or "unknown"),
            noul=noul if isinstance(noul, (int, float)) else None,
            choice=data.get("choice") if isinstance(data.get("choice"), str) else None,
            score=score if isinstance(score, (int, float)) else None,
            probabilities=data.get("probabilities") if isinstance(data.get("probabilities"), dict) else None,
            confidence=confidence if isinstance(confidence, (int, float)) else None,
            legend=data.get("legend") if isinstance(data.get("legend"), dict) else None,
            raw=data,
        )


@dataclass
class DecisionResult:
    """Typed ``POST /decisions`` / ``POST /systemone`` payload."""

    model: str = ""
    answers: Dict[str, DecisionAnswer] = field(default_factory=dict)
    usage: Optional[JSONDict] = None
    raw: JSONDict = field(default_factory=dict)

    def noul(self, question_id: str) -> Optional[float]:
        """Yes/no probability for a ``noul`` question, if present."""
        answer = self.answers.get(question_id)
        return None if answer is None else answer.noul

    def picked(self, question_id: str) -> Optional[str]:
        """Highest-probability option for a ``choice`` question, if present."""
        answer = self.answers.get(question_id)
        return None if answer is None else answer.choice

    @classmethod
    def from_dict(cls, data: Any) -> "DecisionResult":
        if not isinstance(data, dict):
            return cls(raw={"value": data})
        raw_answers = data.get("answers")
        answers: Dict[str, DecisionAnswer] = {}
        if isinstance(raw_answers, dict):
            for key, value in raw_answers.items():
                answers[str(key)] = DecisionAnswer.from_dict(value)
        usage = data.get("usage")
        return cls(
            model=str(data.get("model") or ""),
            answers=answers,
            usage=usage if isinstance(usage, dict) else None,
            raw=data,
        )


class DecisionsAPI:
    """Beta Jev Decisions client (``POST /decisions``, alias ``POST /systemone``)."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def create(
        self,
        state: DecisionState,
        questions: JSONDict,
        model: str = "jev-latest",
        *,
        images: DecisionImages = None,
        use_systemone: bool = False,
        **kwargs: Any,
    ) -> DecisionResult:
        """
        Evaluate ``state`` against typed ``questions``.

        Question types: ``noul`` (yes/no probability), ``choice`` (option +
        distribution), ``score`` (weighted rubric). Every question is evaluated
        in parallel against the same state.

        Args:
            state: Text or structured data to judge.
            questions: Map of question id → ``{type, instructions, ...}``.
            model: Decision model id (``GET /models?type=decision``).
            images: Up to 4 ``data:`` URIs or ``{content_type, base64}`` objects.
            use_systemone: If True, POST ``/systemone`` instead of ``/decisions``.
        """
        if not model:
            raise ValueError("model is required")
        if not questions or not isinstance(questions, dict):
            raise ValueError("questions must be a non-empty dict")
        if _empty_state(state):
            raise ValueError("state is required")

        data: JSONDict = {
            "state": state,
            "questions": questions,
            "model": model,
            **kwargs,
        }
        if images is not None:
            data["images"] = images

        endpoint = DecisionsEndpoints.SYSTEMONE if use_systemone else DecisionsEndpoints.DECISIONS
        logger.debug("Decisions create model=%s endpoint=%s", model, endpoint)
        response = self.client.post(endpoint, data=data)
        return DecisionResult.from_dict(response.json())

    def systemone(
        self,
        state: DecisionState,
        questions: JSONDict,
        model: str = "jev-latest",
        *,
        images: DecisionImages = None,
        **kwargs: Any,
    ) -> DecisionResult:
        """TypeSafe alias: same payload as :meth:`create` on ``POST /systemone``."""
        return self.create(
            state,
            questions,
            model=model,
            images=images,
            use_systemone=True,
            **kwargs,
        )


def _empty_state(state: DecisionState) -> bool:
    if state is None:
        return True
    if isinstance(state, str):
        return not state.strip()
    if isinstance(state, (dict, list)):
        return len(state) == 0
    return False
