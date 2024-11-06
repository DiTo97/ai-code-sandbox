import pytest

from ai_code_sandbox import init_codegen_sandbox, SandboxError


def test_sandbox():
    with init_codegen_sandbox("python") as sandbox:
        code = """
        print("hello, I'm a sandbox")
        """
        
        output = sandbox.run_code(code)

        assert "hello, I'm a sandbox" in output.stdout
        assert output.stderr == ""


def test_sandbox_with_environment():
    sandbox = init_codegen_sandbox("python")
    
    try:
        code = """
        import os
        print(os.environ["example"])
        """
        
        output = sandbox.run_code(code, env_vars={"example": "1"})

        assert "1" in output.stdout
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_with_requirements():
    sandbox = init_codegen_sandbox("python", requirements=["requests>2"])
    
    try:
        code = """
        import requests
        """
        
        output = sandbox.run_code(code)
        
        assert output.stdout == ""
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_with_requirements_compliance():
    with init_codegen_sandbox("python", requirements=["requests>2"]) as sandbox:
        output = sandbox.run_requirements_compliance(["requests>2"])

        assert output.stdout == ""
        assert output.stderr == ""


def test_sandbox_free_requirements_compliance():
    with init_codegen_sandbox("python", requirements=[]) as sandbox:
        output = sandbox.run_requirements_compliance(["requests>2"])

        assert output.stdout == ""
        assert output.stderr == "SandboxRequirementsError: requirements-free sandbox"


def test_sandbox_with_timeout():
    sandbox = init_codegen_sandbox("python", requirements=[])
    
    try:
        code = """
        import time
        time.sleep(10)
        """
        
        output = sandbox.run_code(code, timeout=5)

        assert output.stdout == ""
        assert "exit code 124" in output.stderr
    finally:
        sandbox.close()


def test_sandbox_without_environment():
    sandbox = init_codegen_sandbox("python", requirements=[])
    
    try:
        code = """
        import os
        print(os.environ["example"])
        """
        
        output = sandbox.run_code(code)

        assert output.stdout == ""
        assert "KeyError: 'example'" in output.stderr
    finally:
        sandbox.close()


def test_sandbox_without_requirements():
    sandbox = init_codegen_sandbox("python", requirements=[])
    
    try:
        code = """
        import requests
        """

        output = sandbox.run_code(code)

        assert output.stdout == ""
        assert "ModuleNotFoundError: No module named 'requests'" in output.stderr
    finally:
        sandbox.close()


def test_sandbox_without_requirements_compliance():
    with init_codegen_sandbox("python", requirements=["requests>2"]) as sandbox:
        output = sandbox.run_requirements_compliance(["requests<2", "numpy>2"])

        assert output.stdout == ""
        assert "SandboxRequirementsError" in output.stderr

    
def test_sandbox_without_timeout():
    sandbox = init_codegen_sandbox("python")
    
    try:
        code = """
        import time
        time.sleep(10)
        """
        
        output = sandbox.run_code(code)

        assert output.stdout == ""
        assert output.stderr == ""
    finally:
        sandbox.close()
