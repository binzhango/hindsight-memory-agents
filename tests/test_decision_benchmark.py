from memory_agents.decision_benchmark import grade, summarize


def test_withholding_is_not_automatic_success():
    assert not grade("Requires review", "review", "SQLite")
    assert not grade("Requires review", "review", None)
    assert not grade("Clarify", "clarify", "SQLite")
    assert grade("Clarify", "clarify", None)
    assert grade('{"answer":null}', "answered", None)
    assert not grade('{"answer":"SQLite"}', "answered", None)
    assert not grade("SQLite appears somewhere", "answered", "SQLite")


def test_all_denominators_include_errors_and_rejections():
    base = dict(
        mode="combined",
        expected="SQLite",
        correct=False,
        error=None,
        total_seconds=1,
        recall_seconds=0,
        worker_seconds=0,
        jev_seconds=0,
    )
    rows = [dict(base, disposition="review", review_draft_correct=True), dict(base, error="TimeoutError")]
    result = summarize(rows)["combined"]
    assert result["n"] == 2 and result["correct"] == 0
    assert result["good_drafts_withheld"] == 1
    assert result["errors"] == 1
