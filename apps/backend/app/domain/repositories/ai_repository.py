import uuid
from typing import Protocol

from app.domain.entities.ai_session import AIMessage, AISession, AIToolCall


class AISessionRepository(Protocol):
    def add(self, session: AISession) -> AISession: ...

    def update(self, session: AISession) -> AISession: ...

    def get_by_id(self, session_id: uuid.UUID) -> AISession | None: ...


class AIMessageRepository(Protocol):
    def add(self, message: AIMessage) -> AIMessage: ...

    def list_by_session(self, session_id: uuid.UUID) -> list[AIMessage]: ...


class AIToolCallRepository(Protocol):
    def add(self, tool_call: AIToolCall) -> AIToolCall: ...

    def list_by_session(self, session_id: uuid.UUID) -> list[AIToolCall]: ...
