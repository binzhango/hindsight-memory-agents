from memory_agents.benchmark import score


def test_scorer_requires_answer_not_just_matching_text() -> None:
    assert score('{"answer": "sqlite"}', "SQLite")
    assert score('{"answer": 4317}', "4317")
    assert not score('{"answer": "Do not use SQLite"}', "SQLite")
    assert not score('{"answer": "unknown", "explanation": "SQLite"}', "SQLite")
    assert not score("SQLite", "SQLite")
    assert not score('{"answer": null}', "SQLite")


def test_unknown_requires_null() -> None:
    assert score('{"answer": null}', None)
    assert not score('{"answer": "null"}', None)
    assert not score('{"answer": "SQLite"}', None)
