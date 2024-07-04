import requests, random

REQUEST_URL = "https://kkhcslhnef.execute-api.us-east-1.amazonaws.com"
# REQUEST_URL = "http://localhost:8000"
USER_ID = "user_2gphAEuIZHTvnemF4JLAEgFVjww"
ORGANIZATION_ID = "org_2i7WXFMzGiXLVQHsRKXvPAg9fR3"
USE_ORG = True

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer 12345",
    "stubbed": USER_ID,
    "org_id": ORGANIZATION_ID,
}
ENVIRONMENTS = ["Development", "Production"]
SUITES = ["Billing", "Feature"]
POSSIBLE_TESTS = [
    "Support Ticket",
    "Product Question",
    "Billing Inquiry",
    "Technical Issue Report",
    "Customer Feedback",
    "Order Status Update",
    "Return Request",
    "Account Assistance",
    "Service Outage Report",
    "Complaint Resolution",
    "Feature Request",
    "Subscription Query",
    "Warranty Claim",
    "Shipping Information Request",
    "Product Review Submission",
    "Password Reset Request",
    "Order Cancellation",
    "Discount Inquiry",
    "Loyalty Program Information",
    "Appointment Scheduling",
    "Data Privacy Query",
    "Software Update Information",
    "Device Compatibility Check",
    "Referral Program Details",
    "Product Availability Check",
    "Payment Plan Options",
    "Gift Card Balance Inquiry",
    "Membership Renewal",
    "Event Registration",
    "Survey Participation Request",
    "Exchange Policy Information",
    "Lost Item Inquiry",
    "Safety Information Request",
    "Compliance Documentation Request",
    "Environmental Impact Query",
    "Corporate Partnership Inquiry",
    "Donation Request",
    "Volunteering Opportunities Inquiry",
    "Sponsorship Request",
    "Press Inquiry",
    "Job Application Submission",
    "Feedback on Service Experience",
    "Accessibility Services Information",
    "Wholesale Purchase Inquiry",
    "Custom Order Request",
    "Legal Information Request",
    "Product Recall Information",
    "Affiliate Program Details",
    "Insurance Coverage Query",
]

REPLAY_JSON = {
    "events": [
        {
            "type": "click",
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 0,
        },
        {
            "type": "keyup",
            "content": "H",
            "rawData": {"bubbles": True, "cancelable": True, "code": "KeyH", "key": "H", "keyCode": 72, "which": 72},
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 1024,
        },
        {
            "type": "keyup",
            "content": "H",
            "rawData": {
                "bubbles": True,
                "cancelable": True,
                "code": "ShiftLeft",
                "key": "Shift",
                "keyCode": 16,
                "which": 16,
            },
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 1,
        },
        {
            "type": "keyup",
            "content": "Hel",
            "rawData": {"bubbles": True, "cancelable": True, "code": "KeyE", "key": "e", "keyCode": 69, "which": 69},
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 184,
        },
        {
            "type": "keyup",
            "content": "Hel",
            "rawData": {"bubbles": True, "cancelable": True, "code": "KeyL", "key": "l", "keyCode": 76, "which": 76},
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 11,
        },
        {
            "type": "keyup",
            "content": "Hell",
            "rawData": {"bubbles": True, "cancelable": True, "code": "KeyL", "key": "l", "keyCode": 76, "which": 76},
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 132,
        },
        {
            "type": "keyup",
            "content": "Hello",
            "rawData": {"bubbles": True, "cancelable": True, "code": "KeyO", "key": "o", "keyCode": 79, "which": 79},
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div:nth-of-type(2) > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div > textarea",
                    ],
                }
            ],
            "delta": 150,
        },
        {
            "type": "keydown",
            "content": "",
            "rawData": {
                "bubbles": True,
                "cancelable": True,
                "code": "Enter",
                "key": "Enter",
                "keyCode": 13,
                "which": 13,
            },
            "elementPath": [
                {
                    "shadowed": False,
                    "selectors": [
                        "#prompt-textarea",
                        "body > div:nth-of-type(1) > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main.relative.h-full.w-full.flex-1.overflow-auto.transition-width > div:nth-of-type(2) > div.w-full.pt-2 > form.stretch.mx-2.flex.flex-row.gap-3 > div.relative.flex.h-full.flex-1.flex-col > div.flex.w-full.items-center > div.overflow-hidden.flex.flex-col.w-full.flex-grow.relative.border.rounded-2xl.bg-token-main-surface-primary.border-token-border-medium > textarea.m-0.w-full.resize-none.border-0.bg-transparent.pr-10.max-h-52.pl-3",
                        "body > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > main > div:nth-of-type(2) > div:nth-of-type(2) > form > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type(1) > textarea",
                    ],
                }
            ],
            "delta": 106,
        },
        {"type": "mutation", "count": 4, "deltaSum": 489, "deltaMax": 455},
    ]
}

if USE_ORG:
    POST_BOT_BODY = {"name": "Randomized Bot", "organization_id": ORGANIZATION_ID}
else:
    POST_BOT_BODY = {"name": "Randomized Bot", "user_id": USER_ID}

response = requests.post(REQUEST_URL + "/v1/bots", json=POST_BOT_BODY, headers=HEADERS)
BOT_ID = response.json()["id"]
print(f"Created bot with id: {BOT_ID}")

env_to_id = {}
for environment in ENVIRONMENTS:
    POST_ENV_BODY = {"bot_id": BOT_ID, "name": environment, "url": "https://chat.openai.com/"}
    response = requests.post(REQUEST_URL + "/v1/environments", json=POST_ENV_BODY, headers=HEADERS)
    env_to_id[environment] = response.json()["id"]
    print(f"Created environment {environment} with id: {env_to_id[environment]}")


# CREATE SUITES
suite_to_id = {}
suite_to_tests = {}
suite_iteration_count = {}


def create_test_runs(environment, test_id, test_name, suite_run_id=None):
    # create test run
    POST_TEST_RUN_BODY = {
        "environment_id": env_to_id[environment],
        "test_id": test_id,
        "initiation_type": "Manual",
    }
    if suite_run_id:
        POST_TEST_RUN_BODY["suite_run_id"] = suite_run_id

    response = requests.post(REQUEST_URL + "/v1/test_runs", json=POST_TEST_RUN_BODY, headers=HEADERS)
    test_run_id = response.json()["id"]
    print(f"Created test run for test: {test_name} in environment: {environment}")

    variants = requests.get(REQUEST_URL + f"/v1/tests/{test_id}/variants", headers=HEADERS).json()["data"]
    for variant in variants:
        # create variant runs
        POST_VARIANT_RUN_BODY = {
            "test_run_id": test_run_id,
            "variant_id": variant.get("id"),
            "initiation_type": "Manual",
        }
        response = requests.post(REQUEST_URL + "/v1/variant_runs", json=POST_VARIANT_RUN_BODY, headers=HEADERS)
        variant_run_id = response.json()["id"]
        print(f"Created variant run for test: {test_name} in environment: {environment}")

        # get test
        response = requests.get(REQUEST_URL + f"/v1/tests/{test_id}", headers=HEADERS)
        for i in range(response.json()["iteration_count"]):
            # create evaluations
            POST_EVALUATION_BODY = {
                "variant_run_id": variant_run_id,
                "html_blob": "<div>blob</div>",
                "replayed_elapsed_seconds": random.randint(100, 50000) / 100,
                "initiation_type": "Manual",
            }
            response = requests.post(REQUEST_URL + "/v1/evaluations", json=POST_EVALUATION_BODY, headers=HEADERS)
            print(f"Created evaluation for test: {test_name} in environment: {environment}")


try:
    for suite in SUITES:
        POST_SUITE_BODY = {"bot_id": BOT_ID, "name": suite}
        response = requests.post(REQUEST_URL + "/v1/suites", json=POST_SUITE_BODY, headers=HEADERS)
        suite_to_id[suite] = response.json()["id"]
        print(f"Created suite {suite} with id: {suite_to_id[suite]}")

        PATCH_SUITE_BODY = {
            "default_iteration_count": random.randint(2, 3),
            "default_variant_count": random.randint(2, 3),
        }

        response = requests.patch(
            REQUEST_URL + f"/v1/suites/{suite_to_id[suite]}",
            json=PATCH_SUITE_BODY,
            headers=HEADERS,
        )
        suite_iteration_count[suite] = response.json()["default_iteration_count"]
        print(f"Updated suite {suite} to have {PATCH_SUITE_BODY['default_iteration_count']} iterations")

        # CREATE TESTS
        for i in range(random.randint(5, 10)):
            test_name = random.choice(POSSIBLE_TESTS)
            POST_TEST_BODY = {"suite_id": suite_to_id[suite], "name": test_name}
            response = requests.post(REQUEST_URL + "/v1/tests", json=POST_TEST_BODY, headers=HEADERS)
            test_id = response.json()["id"]
            suite_to_tests[suite] = suite_to_tests.get(suite, []) + [test_id]
            print(f"Created test {test_name} in suite {suite} with id: {test_id}")

            if random.random() < 0.6:
                PATCH_SUITE_BODY = {
                    "success_criteria": random.choice(["always pass", "always fail"]),
                    "use_default_success_criteria": False,
                }
                response = requests.patch(
                    REQUEST_URL + f"/v1/tests/{test_id}",
                    json=PATCH_SUITE_BODY,
                    headers=HEADERS,
                )

            POST_BASELINE_BODY = {
                "test_id": test_id,
                "name": f"Baseline",
                "html_blob": "<div>blob</div>",
            }
            response = requests.post(REQUEST_URL + "/v1/baselines", json=POST_BASELINE_BODY, headers=HEADERS)
            print(f"Created baseline {i} for test: {test_name}")
            # 10% chance for 2 baselines for the test
            if random.random() < 0.1:
                POST_BASELINE_BODY = {
                    "test_id": test_id,
                    "name": f"Baseline 2",
                    "html_blob": "<div>blob</div>",
                }
                response = requests.post(REQUEST_URL + "/v1/baselines", json=POST_BASELINE_BODY, headers=HEADERS)
                print(f"Created baseline 2 for test: {test_name}")

            # create variant for the test
            POST_VARIANT_BODY = {"test_id": test_id, "replay_json": REPLAY_JSON}
            response = requests.post(REQUEST_URL + "/v1/variants", json=POST_VARIANT_BODY, headers=HEADERS)
            variant_id = response.json()["id"]
            print(f"Created variant {i} for test: {test_name}")

            # create a couple test runs for each environment
            for environment in ENVIRONMENTS:
                for i in range(random.randint(2, 8)):
                    # create test run
                    create_test_runs(environment, test_id, test_name)

        # create a couple suite runs for each environment
        for environment in ENVIRONMENTS:
            for i in range(random.randint(2, 4)):
                # create suite run
                POST_SUITE_RUN_BODY = {
                    "suite_id": suite_to_id[suite],
                    "environment_id": env_to_id[environment],
                    "initiation_type": "Manual",
                }
                response = requests.post(REQUEST_URL + "/v1/suite_runs", json=POST_SUITE_RUN_BODY, headers=HEADERS)
                suite_run_id = response.json()["id"]
                print(f"Created suite run for suite: {suite} in environment: {environment} - id: {suite_run_id}")

                # create test runs
                for test_id in suite_to_tests[suite]:
                    create_test_runs(environment, test_id, test_name, suite_run_id)

    print("Completed successfully!")
except Exception as e:
    print(e)
    print(response.json())
