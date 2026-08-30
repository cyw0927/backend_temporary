from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    is_correct: bool
    message: str


class DeterministicEvaluator:
    """MVP evaluator that never executes submitted code.

    It compares normalized source text with the task reference solution. Replace this
    adapter with a constrained Docker-backed evaluator for real code execution.
    """

    def evaluate(self, submitted_code: str, reference_solution: str) -> EvaluationResult:
        normalize = lambda value: "\n".join(line.rstrip() for line in value.strip().splitlines())
        correct = normalize(submitted_code) == normalize(reference_solution)
        return EvaluationResult(correct, "correct" if correct else "incorrect")


evaluator = DeterministicEvaluator()
