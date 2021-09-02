import services
from copy import deepcopy


def test_zip_incidents_empty():
    left = []
    right = []
    assert services.zip_incidents(left, right) == []


def test_zip_incidents_left_only():
    left = [{"timestamp": 1}]
    right = []
    assert services.zip_incidents(left, right) == [{"timestamp": 1}]


def test_zip_incidents_right_only():
    left = []
    right = [{"timestamp": 1}]
    assert services.zip_incidents(left, right) == [{"timestamp": 1}]


def test_zip_incidents_right_merge():
    left = [{"timestamp": 1}, {"timestamp": 2}]
    right = [{"timestamp": 1}, {"timestamp": 3}]
    assert services.zip_incidents(left, right) == [
        {"timestamp": 1},
        {"timestamp": 1},
        {"timestamp": 2},
        {"timestamp": 3},
    ]


def test_in_place_merge_incidents_empty():
    left = {}
    right = {}

    assert services.in_place_merge_incidents(left, right) == {}


def test_in_place_merge_incidents_right():
    left = {}
    right = {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }

    assert services.in_place_merge_incidents(left, right) == {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }


def test_in_place_merge_incidents_left():
    left = {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }
    right = {}

    assert services.in_place_merge_incidents(left, right) == {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }


def test_in_place_merge_incidents_nonoverlapping():
    left = {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }
    right = {
        "2": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }

    assert services.in_place_merge_incidents(left, right) == {
        "1": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        },
        "2": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        },
    }


def test_in_place_merge_incidents_merging():
    left = {
        "1": {
            "low": {"count": 1, "incidents": [{"timestamp": 1}]},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 0, "incidents": []},
            "critical": {"count": 0, "incidents": []},
        }
    }

    right = {
        "1": {
            "low": {"count": 2, "incidents": [{"timestamp": 1}, {"timestamp": 2}]},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 1, "incidents": [{"timestamp": 1}]},
            "critical": {"count": 0, "incidents": []},
        },
        "2": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 1, "incidents": [{"timestamp": 1}]},
            "critical": {"count": 0, "incidents": []},
        },
    }

    assert services.in_place_merge_incidents(left, right) == {
        "1": {
            "low": {
                "count": 3,
                "incidents": [{"timestamp": 1}, {"timestamp": 1}, {"timestamp": 2}],
            },
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 1, "incidents": [{"timestamp": 1}]},
            "critical": {"count": 0, "incidents": []},
        },
        "2": {
            "low": {"count": 0, "incidents": []},
            "medium": {"count": 0, "incidents": []},
            "high": {"count": 1, "incidents": [{"timestamp": 1}]},
            "critical": {"count": 0, "incidents": []},
        },
    }