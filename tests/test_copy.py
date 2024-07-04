from tests.conftest import client
from random import choice


def test_copy_suite():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert len(response.json()) == 11
    SWT_ID = response.json()["id"]

    # Create tests
    for i in range(3):
        response = client.post(
            "/v1/tests",
            json={"suite_id": SWT_ID, "name": f"Test {i}"},
        )
        assert response.status_code == 200
        TEST_ID = response.json()["id"]

        # Create baseline
        response = client.post(
            "/v1/baselines",
            json={
                "test_id": TEST_ID,
                "name": "Baseline",
                "html_blob": "html",
            },
        )
        assert response.status_code == 200

        # Create variant
        response = client.post(
            "/v1/variants",
            json={
                "test_id": TEST_ID,
                "replay_json": {"0": {"action": "foo"}, "1": {"action": "bar"}},
            },
        )
        assert response.status_code == 200

    # Update suite values
    response = client.patch(
        f"/v1/suites/{SWT_ID}",
        json={
            "reporting_comparison_configuration": "specific_suite_run",
            "reporting_comparison_suite_run_id": "original",
        },
    )
    assert response.status_code == 200

    # Copy suite
    response = client.post(f"/v1/suites/{SWT_ID}/copy")
    assert response.json()["name"] == "My Suite (Copy)"
    assert response.json()["reporting_comparison_configuration"] == "specific_suite_run"
    assert response.json()["reporting_comparison_suite_run_id"] == "original"

    NEW_SWT_ID = response.json()["id"]

    # Check new suite has 3 tests
    response = client.get(f"/v1/suites/{NEW_SWT_ID}/tests")
    assert len(response.json()["data"]) == 3


def test_copy_bot():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environments
    old_env_ids = []
    for i in range(2):
        response = client.post(
            "/v1/environments",
            json={
                "name": f"Environment {i}",
                "url": "http://localhost",
                "bot_id": BOT_ID,
            },
        )
        old_env_ids.append(response.json()["id"])

    # Create suites
    old_suite_ids = []
    for i in range(3):
        response = client.post("/v1/suites", json={"name": f"Suite {i}", "bot_id": BOT_ID})
        SWT_ID = response.json()["id"]
        old_suite_ids.append(SWT_ID)

        # update suites data
        response = client.patch(
            f"/v1/suites/{old_suite_ids[-1]}",
            json={
                "reporting_comparison_configuration": "specific_suite_run",
                "reporting_comparison_suite_run_id": choice(old_suite_ids),
            },
        )
        assert response.status_code == 200

        # Create tests
        for j in range(2):
            response = client.post(
                "/v1/tests",
                json={"suite_id": SWT_ID, "name": f"Test {j}"},
            )
            assert response.status_code == 200
            TEST_ID = response.json()["id"]

            # Create baseline
            response = client.post(
                "/v1/baselines",
                json={
                    "test_id": TEST_ID,
                    "name": "Baseline",
                    "html_blob": "html",
                },
            )
            assert response.status_code == 200

            # Create variant
            response = client.post(
                "/v1/variants",
                json={
                    "test_id": TEST_ID,
                    "replay_json": {"0": {"action": "foo"}, "1": {"action": "bar"}},
                },
            )
            assert response.status_code == 200

    # Copy bot
    response = client.post(f"/v1/bots/{BOT_ID}/copy")
    NEW_BOT_ID = response.json()["id"]
    assert response.json()["name"] == "My Bot (Copy)"

    # check that all new suites reference new reporting values
    response = client.get(f"/v1/bots/{NEW_BOT_ID}/suites")
    for suite in response.json()["data"]:
        assert suite["id"] not in old_suite_ids
        assert suite["reporting_comparison_suite_run_id"] not in old_suite_ids

    # check new envs were created
    response = client.get(f"/v1/bots/{NEW_BOT_ID}/environments")
    for env in response.json()["data"]:
        assert env["id"] not in old_env_ids
