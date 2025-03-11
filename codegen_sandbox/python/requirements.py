compliance_script = """
import multiprocessing
import typing
from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion


class SandboxRequirementsError(Exception):
    def __init__(self, requirements: typing.List[str]):
        message = (
            "The following packages are missing or have conflicts: " +
            ", ".join(requirements)
        )

        super().__init__(message)


def _single_compliance(package: str) -> typing.Optional[str]:
    package = package.strip()

    try:
        requirement = Requirement(package)
        version_ = version(requirement.name)

        if requirement.specifier:
            if not requirement.specifier.contains(Version(version_)):
                return f"{{package}} (version conflict: available {{version_}})"

        return None
    except PackageNotFoundError:
        return package
    except InvalidVersion:
        return f"{{package}} (invalid version requirement)"


def compliance(requirements: typing.List[str]):
    with multiprocessing.Pool() as starpool:
        missing = starpool.map(_single_compliance, requirements)

    missing = [package for package in missing if package]
    
    if missing:
        raise SandboxRequirementsError(missing)

    
if __name__ == "__main__":
    compliance({requirements})
"""
