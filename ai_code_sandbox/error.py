import typing

from ai_code_sandbox.config import max_available_config


class SandboxError(Exception):
    """captures any sandbox-related errors"""


class SandboxConfigError(Exception):
    """captures any sandbox config errors related to system resources"""
    def __init__(self, config: str):
        message = (
            f"specs configuration '{config}' not available on this system. "
            f"The largest available configuration is: '{max_available_config}'"
        )

        super().__init__(message)


class SandboxRequirementsError(Exception):
    """captures any sandbox requirements-related errors"""
    def __init__(self, requirements: typing.List[str]):
        message = (
            "The following packages are missing or have conflicts: " +
            ", ".join(requirements)
        )

        super().__init__(message)
