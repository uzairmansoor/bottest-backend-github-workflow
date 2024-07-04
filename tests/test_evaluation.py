from tests.conftest import client
from unittest.mock import patch
from src.core.evaluations import evaluate_conversation
from random import choice


def test_evaluation():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})

    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})

    ENV_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})

    SWT_ID = response.json()["id"]

    # Create test
    response = client.post(
        "/v1/tests",
        json={"suite_id": SWT_ID, "name": "My Test"},
    )

    TST_ID = response.json()["id"]

    # Create variant
    response = client.post(
        "/v1/variants",
        json={"test_id": TST_ID, "replay_json": {"0": {"action": "foo"}, "1": {"action": "bar"}}},
    )

    # Create baseline
    response = client.post(
        "/v1/baselines",
        json={
            "test_id": TST_ID,
            "name": "Baseline",
            "html_blob": "<></>",
        },
    )

    # Create a suite run
    response = client.post(
        "/v1/suite_runs",
        json={"suite_id": SWT_ID, "environment_id": ENV_ID, "initiation_type": "Manual"},
    )

    SRN_ID = response.json()["id"]

    # Create test run
    response = client.post(
        "/v1/test_runs",
        json={"test_id": TST_ID, "environment_id": ENV_ID, "suite_run_id": SRN_ID, "initiation_type": "Manual"},
    )

    TRN_ID = response.json()["id"]

    # Create variant run
    response = client.post(
        "/v1/variant_runs",
        json={"test_run_id": TRN_ID, "variant_id": "variant_1", "initiation_type": "Manual"},
    )

    assert len(response.json()) == 10
    VRN_ID = response.json()["id"]

    # Create evaluations
    with patch("src.core.utils.parse_conversation_dict_from_html") as parse_mock, patch(
        "src.core.evaluations.summarize_failure_reasons"
    ) as summarize_mock, patch("src.core.evaluations.evaluate_against_baseline") as eval_mock:

        def parse_side_effect(html_blob, get_selector=False):
            d = {
                "conversation": {
                    0: {"author": "user", "message": "Hello"},
                    1: {"author": "bot", "message": "Hi! How can I help?"},
                }
            }
            if get_selector:
                d["selector"] = "example"
            return d

        def summarize_side_effect(failure_reasons):
            return "summary reason"

        def eval_side_effect(success_criteria, baseline_conversation_json, evaluation_conversation_json):
            return choice([{"pass": False, "reason": "fail reason"}, {"pass": True}])

        parse_mock.side_effect = parse_side_effect
        summarize_mock.side_effect = summarize_side_effect
        eval_mock.side_effect = eval_side_effect

        # Create 5 evaluations
        EVL_IDS = []
        for i in range(0, 5):
            response = client.post(
                "/v1/evaluations",
                json={
                    "variant_run_id": VRN_ID,
                    "html_blob": "<>",
                    "replayed_elapsed_seconds": 1.2,
                    "initiation_type": "Manual",
                },
            )

            assert len(response.json()) == 10
            EVL_IDS.append(response.json()["id"])

        # Evaluate each conversation
        for EVL_ID in EVL_IDS:
            evaluate_conversation(EVL_ID)

        # Check that each evaluation was updated with pass/fail
        # keep track of pass rate
        pass_count = 0
        for EVL_ID in EVL_IDS:
            response = client.get(f"/v1/evaluations/{EVL_ID}")

            assert response.json()["status"] in ["Pass", "Fail"]
            if response.json()["status"] == "Pass":
                pass_count += 1

        # Expected pass/fail/mixed
        expected = "Pass" if pass_count == len(EVL_IDS) else "Fail" if pass_count == 0 else "Mixed"

        # Check that variant run was updated
        response = client.get(f"/v1/variant_runs/{VRN_ID}")

        assert response.json()["status"] == expected
        assert response.json()["pass_rate"] == pass_count / 5

        # Check that test run was updated
        response = client.get(f"/v1/test_runs/{TRN_ID}")

        assert response.json()["status"] == expected

        # Check that suite run was updated
        response = client.get(f"/v1/suite_runs/{SRN_ID}")

        assert response.json()["status"] == expected
