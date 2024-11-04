import multiprocessing
import typing
from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion

from ai_code_sandbox.error import SandboxRequirementsError


def _single_compliance(package: str) -> typing.Optional[str]:
    package = package.strip()

    try:
        requirement = Requirement(package)
        version_ = version(requirement.name)

        if requirement.specifier:
            if not requirement.specifier.contains(Version(version_)):
                return f"{package} (version conflict: available {version_})"

        return None
    except PackageNotFoundError:
        return package
    except InvalidVersion:
        return f"{package} (invalid version requirement)"


def compliance(requirements: typing.List[str]):
    """ensures requirements are compliant with the virtual environment"""
    with multiprocessing.Pool() as starpool:
        missing = starpool.map(_single_compliance, requirements)

    missing = [package for package in missing if package]
    
    if missing:
        raise SandboxRequirementsError(missing)
