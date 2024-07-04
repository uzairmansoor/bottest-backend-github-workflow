from fastapi import APIRouter

from src.api.v1.analytics import router as analyics_router
from src.api.v1.baselines import router as baselines_router
from src.api.v1.bots import router as bots_router
from src.api.v1.environments import router as environments_router
from src.api.v1.evaluations import router as evaluations_router
from src.api.v1.organizations import router as organizations_router
from src.api.v1.suite_runs import router as suite_runs_router
from src.api.v1.suites import router as suites_router
from src.api.v1.test_runs import router as test_runs_router
from src.api.v1.tests import router as tests_router
from src.api.v1.users import router as users_router
from src.api.v1.variant_runs import router as variant_runs_router
from src.api.v1.variants import router as variants_router

router = APIRouter(prefix="/v1")

router.include_router(bots_router)
router.include_router(environments_router)
router.include_router(suites_router)
router.include_router(suite_runs_router)
router.include_router(tests_router)
router.include_router(test_runs_router)
router.include_router(baselines_router)
router.include_router(variants_router)
router.include_router(variant_runs_router)
router.include_router(evaluations_router)
router.include_router(users_router)
router.include_router(organizations_router)
router.include_router(analyics_router)
