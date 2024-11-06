import pytest

from ai_code_sandbox import init_codegen_sandbox, SandboxError


def test_sandbox():
    with init_codegen_sandbox("node") as sandbox:
        code = """
        console.log("hello, I'm a sandbox");
        """
        
        output = sandbox.run_code(code)

        assert "hello, I'm a sandbox" in output.stdout
        assert output.stderr == ""
