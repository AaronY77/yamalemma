from dataclasses import dataclass
from typing import Literal


ALLOWED_AXIOMS = frozenset({
    "propext",
    "Classical.choice",
    "Quot.sound",
})

AxiomPolicyStatus = Literal["allowed", "forbidden", "unreadable"]


@dataclass(frozen=True)
class AxiomPolicyResult:
    status: AxiomPolicyStatus
    forbidden_axioms: tuple[str, ...]


def assess_axioms(
    axioms: tuple[str, ...] | None,
) -> AxiomPolicyResult:
    if axioms is None:
        return AxiomPolicyResult(
            status="unreadable",
            forbidden_axioms=(),
        )

    forbidden = tuple(sorted(set(axioms) - ALLOWED_AXIOMS))

    if forbidden:
        return AxiomPolicyResult(
            status="forbidden",
            forbidden_axioms=forbidden,
        )

    return AxiomPolicyResult(
        status="allowed",
        forbidden_axioms=(),
    )