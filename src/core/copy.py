from sqlmodel.orm.session import Session

from src.core.utils import has_admin_permissions, has_editor_permissions
from src.db import with_db_session
from src.models.api_schema import (
    BotReadResponse,
    InvalidPermissionsResponse,
    NotFoundResponse,
    SuiteReadResponse,
)
from src.models.db_schema import Baseline, Bot, Environment, Suite, Test, Variant


def create_duplicate_suite(suite: Suite, name: str, actor: dict, db_session: Session) -> Suite:
    new_suite = Suite(
        name=name,
        default_success_criteria=suite.default_success_criteria,
        default_iteration_count=suite.default_iteration_count,
        default_variant_count=suite.default_variant_count,
        reporting_comparison_configuration=suite.reporting_comparison_configuration,
        reporting_comparison_suite_run_id=suite.reporting_comparison_suite_run_id,
        reporting_comparison_environment_id=suite.reporting_comparison_environment_id,
        bot_id=suite.bot_id,
        created_by=actor.get("id", "unknown"),
        last_updated_by=actor.get("id", "unknown"),
    )
    db_session.add(new_suite)
    db_session.commit()
    db_session.refresh(new_suite)

    # for each test in suite, create a duplicate test
    for test in suite.tests:
        new_test = Test(
            name=test.name,
            suite_id=new_suite.id,
            success_criteria=test.success_criteria,
            use_default_success_criteria=test.use_default_success_criteria,
            iteration_count=test.iteration_count,
            use_default_iteration_count=test.use_default_iteration_count,
            variant_count=test.variant_count,
            use_default_variant_count=test.use_default_variant_count,
            full_run_enabled=test.full_run_enabled,
            created_by=actor.get("id", "unknown"),
            last_updated_by=actor.get("id", "unknown"),
        )
        db_session.add(new_test)
        db_session.commit()
        db_session.refresh(new_test)

        # duplicate all variants
        for variant in test.variants:
            new_variant = Variant(
                test_id=new_test.id,
                replay_json=variant.replay_json,
                created_by=actor.get("id", "unknown"),
                last_updated_by=actor.get("id", "unknown"),
            )
            db_session.add(new_variant)
            db_session.commit()
            db_session.refresh(new_variant)

        # duplicate all baselines
        for baseline in test.baselines:
            new_baseline = Baseline(
                name=baseline.name,
                html_blob=baseline.html_blob,
                conversation_json=baseline.conversation_json,
                test_id=new_test.id,
                created_by=actor.get("id", "unknown"),
                last_updated_by=actor.get("id", "unknown"),
            )
            db_session.add(new_baseline)
            db_session.commit()
            db_session.refresh(new_baseline)

    return new_suite


@with_db_session
def copy_bot_by_id(bot_id: str, actor: dict, db_session: Session) -> BotReadResponse:
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_admin_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    # create new bot
    new_bot = Bot(
        name=f"{get_bot.name} (Copy)",
        organization_id=get_bot.organization_id,
        user_id=get_bot.user_id,
        created_by=actor.get("id", "unknown"),
        last_updated_by=actor.get("id", "unknown"),
    )
    db_session.add(new_bot)
    db_session.commit()
    db_session.refresh(new_bot)

    # duplicate all environments
    old_env_to_new_env = {}
    for environment in get_bot.environments:
        new_environment = Environment(
            name=environment.name,
            url=environment.url,
            bot_id=new_bot.id,
            created_by=actor.get("id", "unknown"),
            last_updated_by=actor.get("id", "unknown"),
        )
        db_session.add(new_environment)
        db_session.commit()
        db_session.refresh(new_environment)

        old_env_to_new_env[environment.id] = new_environment.id

    # duplicate all suites
    old_suite_to_new_suite = {}
    for suite in get_bot.suites:
        duplicated_suite = create_duplicate_suite(suite, f"{suite.name} (Copy)", actor, db_session)
        duplicated_suite.bot_id = new_bot.id
        db_session.commit()
        old_suite_to_new_suite[suite.id] = duplicated_suite.id

    # update reporting_comparison_suite_run_id and reporting_comparison_environment_id references
    for suite in new_bot.suites:
        if suite.reporting_comparison_suite_run_id in old_suite_to_new_suite:
            suite.reporting_comparison_suite_run_id = old_suite_to_new_suite[suite.reporting_comparison_suite_run_id]
        if suite.reporting_comparison_environment_id in old_env_to_new_env:
            suite.reporting_comparison_environment_id = old_env_to_new_env[suite.reporting_comparison_environment_id]

    db_session.commit()
    return BotReadResponse.model_validate(new_bot)


@with_db_session
def copy_suite_by_id(suite_id: str, actor: dict, db_session: Session) -> SuiteReadResponse:
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_editor_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    duplicated_suite = create_duplicate_suite(get_suite, f"{get_suite.name} (Copy)", actor, db_session)

    return SuiteReadResponse.model_validate(duplicated_suite)
