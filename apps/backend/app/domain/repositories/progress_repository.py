import uuid
from typing import Protocol

from app.domain.entities.progress import (
    PracticeEvaluation,
    PracticeSubmission,
    StudentPracticeAttempt,
    StudentProgress,
)


class StudentPracticeAttemptRepository(Protocol):
    def get_by_id(self, attempt_id: uuid.UUID) -> StudentPracticeAttempt | None: ...

    def count_for_user_and_practice(self, user_id: uuid.UUID, practice_id: uuid.UUID) -> int: ...

    def add(self, attempt: StudentPracticeAttempt) -> StudentPracticeAttempt: ...

    def update(self, attempt: StudentPracticeAttempt) -> StudentPracticeAttempt: ...


class PracticeSubmissionRepository(Protocol):
    def get_by_id(self, submission_id: uuid.UUID) -> PracticeSubmission | None: ...

    def add(self, submission: PracticeSubmission) -> PracticeSubmission: ...


class PracticeEvaluationRepository(Protocol):
    def add(self, evaluation: PracticeEvaluation) -> PracticeEvaluation: ...

    def get_by_submission_id(self, submission_id: uuid.UUID) -> PracticeEvaluation | None: ...


class StudentProgressRepository(Protocol):
    def get_by_user_and_practice(
        self, user_id: uuid.UUID, practice_id: uuid.UUID
    ) -> StudentProgress | None: ...

    def add(self, progress: StudentProgress) -> StudentProgress: ...

    def update(self, progress: StudentProgress) -> StudentProgress: ...
