import socket

import pytest

from backend.app.reports.audit import screen
from backend.app.schemas import ScreenRequest
from benchmarks.evaluate import evaluate


def test_rank_and_provenance_are_deterministic(repo):
    request = ScreenRequest(row_ids=[1, 2, 3])
    result = screen(request, repo)
    assert result.model_dump() == screen(request, repo).model_dump()
    assert [c.row_id for c in result.candidates] == [3, 2, 1]
    assert [c.rank for c in result.candidates] == [1, 2, 3]
    assert len(result.groups) == 1
    for c in result.candidates:
        assert c.raw_source_record["DOI"] == c.source_doi
        assert c.inputs_with_units["activation_energy"].unit == "meV"
        assert c.inputs_with_units["prefactor"].unit == "K S/cm"
        assert c.review_required and c.source_location and c.trace
    assert len(result.code_version["calculation_source_sha256"]) == 64
    assert result.source.dataset_record_id == "18947543"


def test_separate_source_groups_and_type(repo):
    result = screen(
        ScreenRequest(
            goal="Find bulk oxygen-ion conductors",
            temperature=1100,
            temperature_unit="K",
            row_ids=[1, 2, 3, 39],
        ),
        repo,
    )
    assert len(result.groups) == 2
    assert all(c.conductivity_type == "bulk" for c in result.candidates)
    assert sum(c.rank == 1 for c in result.candidates) == 2


def test_no_candidates_for_unknown_type(repo):
    result = screen(ScreenRequest(row_ids=[66], conductivity_type="total"), repo)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert not result.candidates
    assert {w.code for w in result.excluded[0].warnings} >= {
        "TYPE_NOT_COMPARABLE",
        "AMBIGUOUS_REGIME",
    }


@pytest.mark.parametrize(
    "screen_request",
    [
        ScreenRequest(goal="Screen at 600"),
        ScreenRequest(goal="Find conductors at 600 C", temperature=500),
        ScreenRequest(goal="Find conductors at 900 °F"),
        ScreenRequest(goal="Find stable bulk conductors at 600 C"),
        ScreenRequest(goal="Find bulk and total at 600 C"),
        ScreenRequest(material_class="Unobtainium"),
        ScreenRequest(goal="Find total conductors at 600 C", conductivity_type="bulk"),
        ScreenRequest(goal="Find bulk conductors above 600 C"),
    ],
)
def test_unsupported_or_conflicting_goals_abstain(repo, screen_request):
    result = screen(screen_request, repo)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert "PLAN_REJECTED" in {w.code for w in result.warnings}


def test_explicit_kelvin_and_class_and_formula(repo):
    request = ScreenRequest(
        goal="Find perovskites bulk conductors at 700 K formula La0.95", row_ids=[1, 2, 3]
    )
    result = screen(request, repo)
    assert result.resolved_plan.temperature_k == 700
    assert result.resolved_plan.material_class == "Perovskites"
    assert all(c.regime == "LT" for c in result.candidates)


def test_no_matches_and_fixture_missing_ids(repo):
    result = screen(ScreenRequest(row_ids=[10]), repo)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert "ROWS_NOT_LOADED" in {w.code for w in result.warnings}


def test_top_n_applies_within_each_group(repo):
    result = screen(ScreenRequest(row_ids=[1, 2, 3], top_n=1), repo)
    assert len(result.candidates) == 1
    assert result.groups[0].eligible_count == 3
    assert result.groups[0].shown_count == 1


def test_offline_pipeline_never_opens_network(repo, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline workflow attempted network access")

    monkeypatch.setattr(socket, "socket", forbidden)
    result = screen(ScreenRequest(row_ids=[1]), repo)
    assert result.runtime_mode == "OFFLINE_DETERMINISTIC"
    assert result.candidates


def test_measured_guard_benchmark():
    result = evaluate()
    assert result["sample_size"] == 8
    assert result["baseline_correct_decisions"] == 1
    assert result["audited_correct_decisions"] == 8
