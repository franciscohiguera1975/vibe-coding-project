"""AI Tutor Agent (Prompt Maestro §11): orquestacion controlada y determinista de
las herramientas de `tools.py`, no un planificador LLM libre. La decision de que
herramientas invocar la toma este codigo Python segun la intencion explicita del
llamador (parametros de la peticion), no el modelo de lenguaje — el modelo solo
sintetiza la respuesta final a partir del contexto ya reunido. Esta eleccion prioriza
control, trazabilidad y proteccion contra ciclos infinitos sobre autonomia abierta,
como pide la seccion §11 ("objetivo, contexto, herramientas permitidas, limites de
iteraciones/tokens, control de permisos, trazabilidad, manejo de errores y
proteccion contra ciclos infinitos"). No ejecuta ninguna accion administrativa o
destructiva: todas las herramientas son de lectura o generacion.

Cada llamada a herramienta (permitida, denegada o fallida) queda registrada en
ai_tool_calls; cada ejecucion crea una fila en ai_sessions con el conteo de
iteraciones y una estimacion de tokens usados."""

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.application.ports.ai_provider import AIProvider
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services.agent.tools import TOOL_REGISTRY
from app.domain.entities.ai_session import (
    AIMessage,
    AIMessageRole,
    AISession,
    AISessionStatus,
    AIToolCall,
    AIToolCallStatus,
)
from app.domain.entities.identity import User
from app.domain.exceptions import AgentLimitExceededError, DomainError, PermissionDeniedError

AGENT_SYSTEM_PROMPT = (
    "Eres el tutor de IA de una plataforma de Vibe Coding. Respondes en base "
    "unicamente al contexto entregado (practica, progreso, envio, analisis de "
    "imagen o pista ya generados). No inventas datos que no esten en ese contexto "
    "ni ejecutas acciones administrativas."
)

TOOL_ALLOWLIST = frozenset(TOOL_REGISTRY.keys())


@dataclass(frozen=True, slots=True)
class AgentRunResult:
    session_id: uuid.UUID
    response: str
    iterations_used: int
    tokens_used: int
    tool_results: dict[str, Any] = field(default_factory=dict)


def _approx_tokens(value: Any) -> int:
    """Estimacion aproximada (palabras, no un tokenizador real) solo para presupuestar
    y registrar consumo relativo entre sesiones; no pretende exactitud."""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return max(1, len(text.split()))


def _build_final_prompt(user_message: str, gathered: dict[str, Any]) -> str:
    context_json = json.dumps(gathered, ensure_ascii=False, default=str)
    return (
        f"Mensaje del estudiante: {user_message}\n\n"
        f"Contexto reunido por las herramientas: {context_json}\n\n"
        "Responda al estudiante de forma breve y concreta usando solo este contexto."
    )


class AITutorAgent:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        ai_provider: AIProvider,
        max_iterations: int = 8,
        max_tokens: int = 4000,
    ) -> None:
        self._uow_factory = uow_factory
        self._ai_provider = ai_provider
        self._max_iterations = max_iterations
        self._max_tokens = max_tokens

    def run(
        self,
        *,
        actor: User,
        practice_slug: str,
        user_message: str,
        submission_id: str | None = None,
        trial_answer: dict[str, Any] | None = None,
        image_base64: str | None = None,
        image_content_type: str = "image/png",
    ) -> AgentRunResult:
        with self._uow_factory() as uow:
            now = datetime.now(UTC)
            session = uow.ai_sessions.add(
                AISession(user_id=actor.id, started_at=now, agent_type="tutor")
            )
            uow.ai_messages.add(
                AIMessage(
                    session_id=session.id, role=AIMessageRole.USER, content=user_message, sequence=0
                )
            )

            iteration = 0
            tokens_used = 0
            gathered: dict[str, Any] = {}

            def finalize(status: AISessionStatus) -> None:
                session.status = status
                session.ended_at = datetime.now(UTC)
                session.iterations_used = iteration
                session.tokens_used = tokens_used
                uow.ai_sessions.update(session)

            def call_tool(name: str, **kwargs: Any) -> dict[str, Any]:
                nonlocal iteration, tokens_used
                iteration += 1
                if iteration > self._max_iterations:
                    uow.ai_tool_calls.add(
                        AIToolCall(
                            session_id=session.id,
                            iteration_index=iteration,
                            tool_name=name,
                            status=AIToolCallStatus.DENIED,
                            arguments=kwargs,
                            error_message="limite de iteraciones excedido",
                        )
                    )
                    finalize(AISessionStatus.ERROR)
                    uow.commit()
                    raise AgentLimitExceededError()

                if name not in TOOL_ALLOWLIST:
                    uow.ai_tool_calls.add(
                        AIToolCall(
                            session_id=session.id,
                            iteration_index=iteration,
                            tool_name=name,
                            status=AIToolCallStatus.DENIED,
                            arguments=kwargs,
                            error_message="herramienta no permitida",
                        )
                    )
                    finalize(AISessionStatus.ERROR)
                    uow.commit()
                    raise PermissionDeniedError(f"ai_tool:{name}")

                try:
                    result = TOOL_REGISTRY[name](uow, actor, self._ai_provider, **kwargs)
                except DomainError as exc:
                    uow.ai_tool_calls.add(
                        AIToolCall(
                            session_id=session.id,
                            iteration_index=iteration,
                            tool_name=name,
                            status=AIToolCallStatus.ERROR,
                            arguments=kwargs,
                            error_message=str(exc),
                        )
                    )
                    finalize(AISessionStatus.ERROR)
                    uow.commit()
                    raise

                tokens_used += _approx_tokens(kwargs) + _approx_tokens(result)
                uow.ai_tool_calls.add(
                    AIToolCall(
                        session_id=session.id,
                        iteration_index=iteration,
                        tool_name=name,
                        status=AIToolCallStatus.SUCCESS,
                        arguments=kwargs,
                        result=result,
                    )
                )
                return result

            practice_info = call_tool("get_practice", practice_slug=practice_slug)
            session.practice_id = uuid.UUID(practice_info["id"])
            gathered["practice"] = practice_info
            gathered["progress"] = call_tool("get_student_progress", practice_slug=practice_slug)

            if submission_id:
                gathered["submission"] = call_tool(
                    "analyze_submission", submission_id=submission_id
                )
                gathered["feedback"] = call_tool("generate_feedback", submission_id=submission_id)
            if trial_answer is not None:
                gathered["trial"] = call_tool(
                    "validate_answer", practice_slug=practice_slug, trial_answer=trial_answer
                )
            if image_base64 and practice_info["type"] == "image":
                gathered["image_analysis"] = call_tool(
                    "analyze_image",
                    image_base64=image_base64,
                    instructions=practice_info["instructions"],
                    content_type=image_content_type,
                )
            if not submission_id and trial_answer is None and not image_base64:
                gathered["hint"] = call_tool(
                    "generate_hint", practice_slug=practice_slug, student_context=user_message
                )

            iteration += 1
            if iteration > self._max_iterations:
                finalize(AISessionStatus.ERROR)
                uow.commit()
                raise AgentLimitExceededError()

            remaining_budget = max(200, self._max_tokens - tokens_used)
            final_prompt = _build_final_prompt(user_message, gathered)
            response_text = self._ai_provider.generate_text(
                final_prompt, system=AGENT_SYSTEM_PROMPT, max_tokens=min(remaining_budget, 600)
            )
            tokens_used += _approx_tokens(final_prompt) + _approx_tokens(response_text)

            uow.ai_messages.add(
                AIMessage(
                    session_id=session.id,
                    role=AIMessageRole.ASSISTANT,
                    content=response_text,
                    sequence=1,
                )
            )
            finalize(AISessionStatus.COMPLETED)
            uow.commit()

            return AgentRunResult(
                session_id=session.id,
                response=response_text,
                iterations_used=iteration,
                tokens_used=tokens_used,
                tool_results=gathered,
            )
