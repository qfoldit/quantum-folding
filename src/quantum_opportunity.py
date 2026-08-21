"""Quantum opportunity scoring for interactive qFoldIT missions.

The scorer is intentionally solver-agnostic: it estimates whether a quantum
call is worth scheduling at the current mission state. It does not claim a
quantum advantage and must be evaluated against classical baselines.
"""

from __future__ import annotations

from dataclasses import dataclass


def _clamp01(value: float) -> float:
    """Clamp a scalar into the closed interval [0, 1]."""
    return max(0.0, min(1.0, value))


@dataclass(frozen=True, slots=True)
class QuantumOpportunityState:
    """Normalized mission-state features used by the quantum scheduler."""

    uncertainty: float
    diversity: float
    plateau: float
    constraint_pressure: float
    expected_gain: float
    quantum_cost: float
    quantum_latency: float
    player_checkpoint: float
    mission_priority: float


@dataclass(frozen=True, slots=True)
class QuantumOpportunityPolicy:
    """Policy thresholds for deciding whether a quantum call is justified."""

    min_qos: float = 0.55
    min_expected_gain: float = 0.35
    max_cost: float = 0.75
    max_latency: float = 0.75


@dataclass(frozen=True, slots=True)
class QuantumOpportunityScore:
    """Computed score and decision for one mission state."""

    qos: float
    expected_value: float
    invoke: bool


def score_quantum_opportunity(
    state: QuantumOpportunityState,
    policy: QuantumOpportunityPolicy = QuantumOpportunityPolicy(),
) -> QuantumOpportunityScore:
    """Estimate whether a quantum call is justified at the current state.

    The weights are deliberately conservative defaults, not a scientific law.
    Mission teams should calibrate them against measured classical/quantum
    outcomes for each mission family.
    """

    uncertainty = _clamp01(state.uncertainty)
    diversity = _clamp01(state.diversity)
    plateau = _clamp01(state.plateau)
    constraint_pressure = _clamp01(state.constraint_pressure)
    expected_gain = _clamp01(state.expected_gain)
    quantum_cost = _clamp01(state.quantum_cost)
    quantum_latency = _clamp01(state.quantum_latency)
    player_checkpoint = _clamp01(state.player_checkpoint)
    mission_priority = _clamp01(state.mission_priority)

    opportunity = (
        0.18 * uncertainty
        + 0.10 * diversity
        + 0.18 * plateau
        + 0.14 * constraint_pressure
        + 0.22 * expected_gain
        + 0.08 * player_checkpoint
        + 0.10 * mission_priority
    )
    friction = 0.55 * quantum_cost + 0.45 * quantum_latency
    qos = _clamp01(opportunity - 0.35 * friction)
    expected_value = _clamp01(
        0.65 * expected_gain
        + 0.20 * mission_priority
        + 0.15 * constraint_pressure
        - 0.35 * friction
    )

    invoke = (
        qos >= policy.min_qos
        and expected_gain >= policy.min_expected_gain
        and quantum_cost <= policy.max_cost
        and quantum_latency <= policy.max_latency
    )
    return QuantumOpportunityScore(qos=qos, expected_value=expected_value, invoke=invoke)
