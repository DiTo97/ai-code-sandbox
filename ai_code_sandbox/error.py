import typing


class SandboxError(Exception):
    """captures any sandbox-related errors"""


class SandboxRequirementsError(Exception):
    """captures any sandbox requirements-related errors"""
    def __init__(self, requirements: typing.List[str]):
        message = (
            "The following packages are missing or have conflicts: " +
            ", ".join(requirements)
        )

        super().__init__(message)
