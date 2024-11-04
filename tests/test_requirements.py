import pytest

from ai_code_sandbox.error import SandboxRequirementsError 
from ai_code_sandbox.requirements import compliance


def test_compliance():
    compliance(["twine>5", "docker>7"])


def test_compliance_missing_requirements():
    requirements = ["numpy>2"]
    
    with pytest.raises(SandboxRequirementsError) as excinfo:
        compliance(requirements)


def test_compliance_version_conflict():
    requirements = ["docker<7"]
    
    with pytest.raises(SandboxRequirementsError):
        compliance(requirements)
