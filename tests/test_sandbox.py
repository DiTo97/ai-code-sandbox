import pytest

from ai_code_sandbox.sandbox import AICodeSandbox, SandboxError


@pytest.fixture(scope="function")
def sandbox():
    sandbox = AICodeSandbox()
    yield sandbox
    sandbox.close()


def test_sandbox():
    with AICodeSandbox(requirements=[]) as sandbox:
        code = """
        print("hello, I'm a sandbox")
        """
        
        output = sandbox.run_code(code)

        assert "hello, I'm a sandbox" in output.stdout
        assert output.stderr == ""


def test_sandbox_with_environment():
    sandbox = AICodeSandbox(requirements=[])
    
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
    sandbox = AICodeSandbox(requirements=["requests>2"])
    
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
    with AICodeSandbox(requirements=["requests>2"]) as sandbox:
        output = sandbox.run_compliance(["requests>2"])

        assert output.stdout == ""
        assert output.stderr == ""


def test_sandbox_free_requirements_compliance():
    with AICodeSandbox(requirements=[]) as sandbox:
        output = sandbox.run_compliance(["requests>2"])

        assert output.stdout == ""
        assert output.stderr == "SandboxRequirementsError: requirements-free sandbox"


def test_sandbox_with_timeout():
    sandbox = AICodeSandbox(requirements=[])
    
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
    sandbox = AICodeSandbox(requirements=[])
    
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
    sandbox = AICodeSandbox(requirements=[])
    
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
    with AICodeSandbox(requirements=["requests>2"]) as sandbox:
        output = sandbox.run_compliance(["requests<2", "numpy>2"])

        assert output.stdout == ""
        assert "SandboxRequirementsError" in output.stderr

    
def test_sandbox_without_timeout():
    sandbox = AICodeSandbox(requirements=[])
    
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


def test_write_and_read_file(sandbox: AICodeSandbox):
    filename = "output.txt"
    content = "hello, I'm a sandbox"
    sandbox.write_file(filename, content)
    assert content == sandbox.read_file(filename)


def test_write_and_read_binary_file(sandbox: AICodeSandbox):
    filename = "output.bin"
    content = b"\x00\x01\x02\x03"
    sandbox.write_file(filename, content)
    assert content == sandbox.read_file(filename).encode("latin1")


def test_delete_file(sandbox: AICodeSandbox):
    filename = "output.txt"
    content = ""
    sandbox.write_file(filename, content)
    sandbox.delete_file(filename)

    with pytest.raises(SandboxError):
        sandbox.read_file(filename)


def test_write_dir(sandbox: AICodeSandbox):
    directory = "output"
    sandbox.write_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code == 0


def test_write_nested_dir(sandbox: AICodeSandbox):
    directory = "output/nested"
    sandbox.write_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code == 0


def test_delete_dir(sandbox: AICodeSandbox):
    directory = "output"
    sandbox.write_dir(directory)
    sandbox.delete_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code != 0
