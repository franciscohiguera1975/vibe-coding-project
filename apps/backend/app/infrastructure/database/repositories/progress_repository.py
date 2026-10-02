import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.progress import (
    AttemptStatus,
    EvaluatorType,
    PracticeEvaluation,
    PracticeSubmission,
    ProgressStatus,
    StudentPracticeAttempt,
    StudentProgress,
)
from app.infrastructure.database.models.progress import (
    PracticeEvaluationModel,
    PracticeSubmissionModel,
    StudentPracticeAttemptModel,
    StudentProgressModel,
)


def _attempt_to_domain(model: StudentPracticeAttemptModel) -> StudentPracticeAttempt:
    return StudentPracticeAttempt(
        id=model.id,
        user_id=model.user_id,
        practice_id=model.practice_id,
        attempt_number=model.attempt_number,
        status=AttemptStatus(model.status.value),
        started_at=model.started_at,
        finished_at=model.finished_at,
        data=dict(model.data),
    )


def _submission_to_domain(model: PracticeSubmissionModel) -> PracticeSubmission:
    return PracticeSubmission(
        id=model.id,
        attempt_id=model.attempt_id,
        practice_id=model.practice_id,
        user_id=model.user_id,
        payload=dict(model.payload),
        submitted_at=model.submitted_at,
    )


def _evaluation_to_domain(model: PracticeEvaluationModel) -> PracticeEvaluation:
    return PracticeEvaluation(
        id=model.id,
        submission_id=model.submission_id,
        score=float(model.score),
        passed=model.passed,
        evaluated_by=EvaluatorType(model.evaluated_by.value),
        feedback=model.feedback,
        details=dict(model.details),
        evaluator_user_id=model.evaluator_user_id,
    )


def _progress_to_domain(model: StudentProgressModel) -> StudentProgress:
    return StudentProgress(
        id=model.id,
        user_id=model.user_id,
        practice_id=model.practice_id,
        status=ProgressStatus(model.status.value),
        best_score=float(model.best_score) if model.best_score is not None else None,
        attempts_count=model.attempts_count,
        last_attempt_at=model.last_attempt_at,
        completed_at=model.completed_at,
    )


class SqlAlchemyStudentPracticeAttemptRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, attempt_id: uuid.UUID) -> StudentPracticeAttempt | None:
        model = self._session.get(StudentPracticeAttemptModel, attempt_id)
        return _attempt_to_domain(model) if model else None

    def count_for_user_and_practice(self, user_id: uuid.UUID, practice_id: uuid.UUID) -> int:
        return (
            self._session.scalar(
                select(func.count()).where(
                    StudentPracticeAttemptModel.user_id == user_id,
                    StudentPracticeAttemptModel.practice_id == practice_id,
                )
            )
            or 0
        )

    def add(self, attempt: StudentPracticeAttempt) -> StudentPracticeAttempt:
        model = StudentPracticeAttemptModel(
            user_id=attempt.user_id,
            practice_id=attempt.practice_id,
            attempt_number=attempt.attempt_number,
            status=attempt.status,
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            data=dict(attempt.data),
        )
        self._session.add(model)
        self._session.flush()
        return _attempt_to_domain(model)

    def update(self, attempt: StudentPracticeAttempt) -> StudentPracticeAttempt:
        model = self._session.get(StudentPracticeAttemptModel, attempt.id)
        if model is None:
            raise ValueError(f"StudentPracticeAttemptModel {attempt.id} no encontrado")
        model.status = attempt.status
        model.finished_at = attempt.finished_at
        model.data = dict(attempt.data)
        self._session.flush()
        return _attempt_to_domain(model)


class SqlAlchemyPracticeSubmissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, submission_id: uuid.UUID) -> PracticeSubmission | None:
        model = self._session.get(PracticeSubmissionModel, submission_id)
        return _submission_to_domain(model) if model else None

    def add(self, submission: PracticeSubmission) -> PracticeSubmission:
        model = PracticeSubmissionModel(
            attempt_id=submission.attempt_id,
            practice_id=submission.practice_id,
            user_id=submission.user_id,
            payload=dict(submission.payload),
            submitted_at=submission.submitted_at,
        )
        self._session.add(model)
        self._session.flush()
        return _submission_to_domain(model)


class SqlAlchemyPracticeEvaluationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, evaluation: PracticeEvaluation) -> PracticeEvaluation:
        model = PracticeEvaluationModel(
            submission_id=evaluation.submission_id,
            score=evaluation.score,
            passed=evaluation.passed,
            feedback=evaluation.feedback,
            details=dict(evaluation.details),
            evaluated_by=evaluation.evaluated_by,
            evaluator_user_id=evaluation.evaluator_user_id,
        )
        self._session.add(model)
        self._session.flush()
        return _evaluation_to_domain(model)


class SqlAlchemyStudentProgressRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_and_practice(
        self, user_id: uuid.UUID, practice_id: uuid.UUID
    ) -> StudentProgress | None:
        model = self._session.scalar(
            select(StudentProgressModel).where(
                StudentProgressModel.user_id == user_id,
                StudentProgressModel.practice_id == practice_id,
            )
        )
        return _progress_to_domain(model) if model else None

    def add(self, progress: StudentProgress) -> StudentProgress:
        model = StudentProgressModel(
            user_id=progress.user_id,
            practice_id=progress.practice_id,
            status=progress.status,
            best_score=progress.best_score,
            attempts_count=progress.attempts_count,
            last_attempt_at=progress.last_attempt_at,
            completed_at=progress.completed_at,
        )
        self._session.add(model)
        self._session.flush()
        return _progress_to_domain(model)

    def update(self, progress: StudentProgress) -> StudentProgress:
        model = self._session.get(StudentProgressModel, progress.id)
        if model is None:
            raise ValueError(f"StudentProgressModel {progress.id} no encontrado")
        model.status = progress.status
        model.best_score = progress.best_score
        model.attempts_count = progress.attempts_count
        model.last_attempt_at = progress.last_attempt_at
        model.completed_at = progress.completed_at
        self._session.flush()
        return _progress_to_domain(model)
