from src.quantum_opportunity import (
    QuantumOpportunityPolicy,
    QuantumOpportunityState,
    score_quantum_opportunity,
)


def test_high_value_checkpoint_invokes_quantum() -> None:
    state = QuantumOpportunityState(
        uncertainty=0.9,
        diversity=0.8,
        plateau=0.9,
        constraint_pressure=0.8,
        expected_gain=0.9,
        quantum_cost=0.2,
        quantum_latency=0.2,
        player_checkpoint=0.9,
        mission_priority=1.0,
    )

    result = score_quantum_opportunity(state)

    assert result.invoke is True
    assert result.qos >= 0.55
    assert result.expected_value >= 0.35


def test_low_gain_or_high_cost_does_not_invoke() -> None:
    state = QuantumOpportunityState(
        uncertainty=0.2,
        diversity=0.2,
        plateau=0.1,
        constraint_pressure=0.2,
        expected_gain=0.2,
        quantum_cost=0.9,
        quantum_latency=0.9,
        player_checkpoint=0.2,
        mission_priority=0.3,
    )

    result = score_quantum_opportunity(state)

    assert result.invoke is False


def test_custom_policy_changes_decision_boundary() -> None:
    state = QuantumOpportunityState(
        uncertainty=0.8,
        diversity=0.7,
        plateau=0.8,
        constraint_pressure=0.7,
        expected_gain=0.7,
        quantum_cost=0.3,
        quantum_latency=0.3,
        player_checkpoint=0.7,
        mission_priority=0.8,
    )

    strict = QuantumOpportunityPolicy(min_qos=0.95)
    result = score_quantum_opportunity(state, strict)

    assert result.invoke is False
