from functools import lru_cache

from app.application.ports.evaluation import EvaluationPort
from app.infrastructure.evaluation.rule_based_adapter import RuleBasedEvaluationAdapter


@lru_cache
def get_evaluation_port() -> EvaluationPort:
    return RuleBasedEvaluationAdapter()
