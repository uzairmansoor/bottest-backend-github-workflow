from enum import Enum


class RunStatusEnum(str, Enum):
    RUNNING = "Running"
    PASS = "Pass"
    MIXED = "Mixed"
    FAIL = "Fail"
    STOPPED = "Stopped"
    ERROR = "Error"
    SKIPPED = "Skipped"


class InitiationTypeEnum(str, Enum):
    MANUAL = "Manual"
    AUTOMATED = "Automated"
    SCHEDULED = "Scheduled"


class BillingTierEnum(dict, Enum):
    FREE = {"name": "Free", "price": 0}


class ReportingConfigurationEnum(str, Enum):
    MRSE = "most_recent_same_environment"
    MRDE = "most_recent_different_environment"
    SSR = "specific_suite_run"
