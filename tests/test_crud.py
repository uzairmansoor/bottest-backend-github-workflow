from tests.conftest import client


def test_bot():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert len(response.json()) == 7
    BOT_ID = response.json()["id"]

    # Update bot
    response = client.patch(f"/v1/bots/{BOT_ID}", json={"name": "Not My Bot"})
    assert response.json()["name"] == "Not My Bot"

    # Get environments in bot
    for i in range(3):
        response = client.post("/v1/environments", json={"name": f"Env {i}", "url": f"http://{i}", "bot_id": BOT_ID})
        assert response.status_code == 200
    response = client.get(f"/v1/bots/{BOT_ID}/environments")
    assert len(response.json()["data"]) == 3

    # Get suites in bot
    for i in range(3):
        response = client.post("/v1/suites", json={"name": f"Suite {i}", "bot_id": BOT_ID})
        assert response.status_code == 200
    response = client.get(f"/v1/bots/{BOT_ID}/suites")
    assert len(response.json()["data"]) == 3

    # Get bot
    response = client.get(f"/v1/bots/{BOT_ID}")
    assert len(response.json()) == 7

    # Delete bot
    response = client.delete(f"/v1/bots/{BOT_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/bots/{BOT_ID}")
    assert response.status_code == 404


def test_environment():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert len(response.json()) == 8
    ENV_ID = response.json()["id"]

    # Update environment
    response = client.patch(f"/v1/environments/{ENV_ID}", json={"name": "Not My Env"})
    assert response.json()["name"] == "Not My Env"

    # Get suite runs in environment
    for i in range(3):
        response = client.post(
            "/v1/suite_runs",
            json={"suite_id": f"suite_{i}", "environment_id": ENV_ID, "initiation_type": "Manual"},
        )
        assert response.status_code == 200
    response = client.get(f"/v1/environments/{ENV_ID}/suite_runs")
    assert len(response.json()["data"]) == 3

    # Get test runs in environment
    for i in range(3):
        response = client.post(
            "/v1/test_runs",
            json={"test_id": f"test_{i}", "environment_id": ENV_ID, "initiation_type": "Manual"},
        )
        assert response.status_code == 200
    response = client.get(f"/v1/environments/{ENV_ID}/test_runs")
    assert len(response.json()["data"]) == 3

    # Get environment
    response = client.get(f"/v1/environments/{ENV_ID}")
    assert len(response.json()) == 8

    # Delete environment
    response = client.delete(f"/v1/environments/{ENV_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/environments/{ENV_ID}")
    assert response.status_code == 404


def test_suite():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert response.status_code == 200
    ENV_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert len(response.json()) == 11
    SWT_ID = response.json()["id"]

    # Update suite
    response = client.patch(f"/v1/suites/{SWT_ID}", json={"default_success_criteria": "Fail every test!"})
    assert response.json()["default_success_criteria"] == "Fail every test!"

    # Get suite runs in suite
    for i in range(3):
        response = client.post(
            "/v1/suite_runs",
            json={"suite_id": SWT_ID, "environment_id": ENV_ID, "initiation_type": "Manual"},
        )
        assert response.status_code == 200
    response = client.get(f"/v1/suites/{SWT_ID}/suite_runs")
    assert len(response.json()["data"]) == 3

    # Get tests in suite
    for i in range(3):
        response = client.post(
            "/v1/tests",
            json={"suite_id": SWT_ID, "name": f"Test {i}"},
        )
        assert response.json()["success_criteria"] == "Fail every test!"
    response = client.get(f"/v1/suites/{SWT_ID}/tests")
    assert len(response.json()["data"]) == 3

    # Get suite
    response = client.get(f"/v1/suites/{SWT_ID}")
    assert len(response.json()) == 11

    # Delete suite
    response = client.delete(f"/v1/suites/{SWT_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/suites/{SWT_ID}")
    assert response.status_code == 404


def test_suite_run():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert response.status_code == 200
    ENV_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert response.status_code == 200
    SWT_ID = response.json()["id"]

    # Create suite run
    response = client.post(
        "/v1/suite_runs",
        json={"suite_id": SWT_ID, "environment_id": ENV_ID, "initiation_type": "Manual"},
    )
    assert len(response.json()) == 10
    SRN_ID = response.json()["id"]

    # Get test runs in suite run
    for i in range(3):
        response = client.post(
            "/v1/test_runs",
            json={
                "test_id": f"test_{i}",
                "suite_run_id": SRN_ID,
                "environment_id": ENV_ID,
                "initiation_type": "Manual",
            },
        )
        assert response.status_code == 200
    response = client.get(f"/v1/suite_runs/{SRN_ID}/test_runs")
    assert len(response.json()["data"]) == 3

    # Get suite run
    response = client.get(f"/v1/suite_runs/{SRN_ID}")
    assert len(response.json()) == 10


def test_test():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert response.status_code == 200
    ENV_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert response.status_code == 200
    SWT_ID = response.json()["id"]

    # Create test
    response = client.post(
        "/v1/tests",
        json={"suite_id": SWT_ID, "name": "My Test"},
    )
    assert len(response.json()) == 14
    TST_ID = response.json()["id"]

    # Update test
    response = client.patch(f"/v1/tests/{TST_ID}", json={"name": "Not My Test"})
    assert response.json()["name"] == "Not My Test"

    # Get test runs in test
    for i in range(3):
        response = client.post(
            "/v1/test_runs",
            json={"test_id": TST_ID, "environment_id": ENV_ID, "initiation_type": "Manual"},
        )
        assert response.status_code == 200
    response = client.get(f"/v1/tests/{TST_ID}/test_runs")
    assert len(response.json()["data"]) == 3

    # Get baselines in test
    for i in range(3):
        response = client.post(
            "/v1/baselines",
            json={
                "test_id": TST_ID,
                "name": f"Baseline {i}",
                "html_blob": "<></>",
            },
        )
        assert response.status_code == 200
    response = client.get(f"/v1/tests/{TST_ID}/baselines")
    assert len(response.json()["data"]) == 3

    # Get test
    response = client.get(f"/v1/tests/{TST_ID}")
    assert len(response.json()) == 14

    # Delete test
    response = client.delete(f"/v1/tests/{TST_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/tests/{TST_ID}")
    assert response.status_code == 404


def test_test_run():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert response.status_code == 200
    ENV_ID = response.json()["id"]

    # Create test run
    response = client.post(
        "/v1/test_runs",
        json={"test_id": "test_1", "environment_id": ENV_ID, "initiation_type": "Manual"},
    )
    assert len(response.json()) == 11
    TRN_ID = response.json()["id"]

    # Get test run
    response = client.get(f"/v1/test_runs/{TRN_ID}")
    assert len(response.json()) == 11


def test_baseline():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert response.status_code == 200
    SWT_ID = response.json()["id"]

    # Create test
    response = client.post(
        "/v1/tests",
        json={"suite_id": SWT_ID, "name": "My Test"},
    )
    assert response.status_code == 200
    TST_ID = response.json()["id"]

    # Create baseline
    response = client.post(
        "/v1/baselines",
        json={
            "test_id": TST_ID,
            "name": "My Baseline",
            "html_blob": "<></>",
        },
    )
    assert len(response.json()) == 8
    BSL_ID = response.json()["id"]

    # Get baseline
    response = client.get(f"/v1/baselines/{BSL_ID}")
    assert len(response.json()) == 9

    # Delete baseline
    response = client.delete(f"/v1/baselines/{BSL_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/baselines/{BSL_ID}")
    assert response.status_code == 404


def test_variant():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert response.status_code == 200
    SWT_ID = response.json()["id"]

    # Create test
    response = client.post(
        "/v1/tests",
        json={"suite_id": SWT_ID, "name": "My Test"},
    )
    assert response.status_code == 200
    TST_ID = response.json()["id"]

    # Create variant
    response = client.post(
        "/v1/variants",
        json={"test_id": TST_ID, "replay_json": {"0": {"action": "foo"}, "1": {"action": "bar"}}},
    )
    assert len(response.json()) == 7
    VAR_ID = response.json()["id"]

    # Get variant
    response = client.get(f"/v1/variants/{VAR_ID}")
    assert len(response.json()) == 7

    # Delete variant
    response = client.delete(f"/v1/variants/{VAR_ID}")
    assert response.json() == {"status": "OK"}
    response = client.get(f"/v1/variants/{VAR_ID}")
    assert response.status_code == 404


def test_variant_run():
    # Create bot
    response = client.post("/v1/bots", json={"name": "My Bot", "user_id": "unknown"})
    assert response.status_code == 200
    BOT_ID = response.json()["id"]

    # Create environment
    response = client.post("/v1/environments", json={"name": "My Env", "url": "http://localhost", "bot_id": BOT_ID})
    assert response.status_code == 200
    ENV_ID = response.json()["id"]

    # Create suite
    response = client.post("/v1/suites", json={"name": "My Suite", "bot_id": BOT_ID})
    assert response.status_code == 200
    SWT_ID = response.json()["id"]

    # Create test
    response = client.post(
        "/v1/tests",
        json={"suite_id": SWT_ID, "name": "My Test"},
    )
    assert response.status_code == 200
    TST_ID = response.json()["id"]

    # Create test run
    response = client.post(
        "/v1/test_runs",
        json={"test_id": TST_ID, "environment_id": ENV_ID, "initiation_type": "Manual"},
    )
    assert response.status_code == 200
    TRN_ID = response.json()["id"]

    # Create variant run
    response = client.post(
        "/v1/variant_runs",
        json={"test_run_id": TRN_ID, "variant_id": "variant_1", "initiation_type": "Manual"},
    )
    assert len(response.json()) == 10
    VRN_ID = response.json()["id"]

    # Get variant run
    response = client.get(f"/v1/variant_runs/{VRN_ID}")
    assert len(response.json()) == 10
