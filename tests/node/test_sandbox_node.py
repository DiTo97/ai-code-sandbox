from codegen_sandbox import init_codegen_sandbox


def test_sandbox():
    with init_codegen_sandbox("node") as sandbox:
        code = """
        console.log("hello, I'm a sandbox");
        """
        
        output = sandbox.run_code(code)

        assert "hello, I'm a sandbox" in output.stdout
        assert output.stderr == ""


def test_sandbox_with_environment():
    sandbox = init_codegen_sandbox("node")
    
    try:
        code = """
        console.log(process.env.example);
        """
        
        output = sandbox.run_code(code, env_vars={"example": "1"})

        assert "1" in output.stdout
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_with_requirements():
    sandbox = init_codegen_sandbox("node", requirements=["axios@^1.0.0"])
    
    try:
        code = """
        const axios = require('axios');
        """
        
        output = sandbox.run_code(code)
        
        assert output.stdout == ""
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_with_requirements_compliance():
    with init_codegen_sandbox("node", requirements=["axios@^1.0.0"]) as sandbox:
        output = sandbox.run_requirements_compliance(["axios@^1.0.0"])

        assert output.stdout == ""
        assert output.stderr == ""


def test_sandbox_free_requirements_compliance():
    with init_codegen_sandbox("node") as sandbox:
        output = sandbox.run_requirements_compliance(["axios@^1.0.0"])

        assert output.stdout == ""
        assert output.stderr == "SandboxRequirementsError: requirements-free sandbox"


def test_sandbox_with_timeout():
    sandbox = init_codegen_sandbox("node")
    
    try:
        code = """
        setTimeout(() => {
            console.log('timeout');
        }, 10000);
        """
        
        output = sandbox.run_code(code, timeout=5)

        assert output.stdout == ""
        assert "exit code 124" in output.stderr
    finally:
        sandbox.close()


def test_sandbox_without_environment():
    sandbox = init_codegen_sandbox("node")
    
    try:
        code = """
        console.log(process.env.example);
        """
        
        output = sandbox.run_code(code)

        assert "undefined" in output.stdout
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_without_requirements():
    sandbox = init_codegen_sandbox("node")
    
    try:
        code = """
        const axios = require('axios');
        """
        
        output = sandbox.run_code(code)

        assert output.stdout == ""
        assert "Cannot find module 'axios'" in output.stderr
    finally:
        sandbox.close()


def test_sandbox_without_requirements_compliance():
    with init_codegen_sandbox("node", requirements=["axios@^1.0.0"]) as sandbox:
        output = sandbox.run_requirements_compliance(["express", "lodash"])

        assert output.stdout == ""
        assert "SandboxRequirementsError" in output.stderr


def test_sandbox_without_timeout():
    sandbox = init_codegen_sandbox("node")
    
    try:
        code = """
        setTimeout(() => {
            console.log('timeout');
        }, 10000);
        """
        
        output = sandbox.run_code(code)

        assert "timeout" in output.stdout
        assert output.stderr == ""
    finally:
        sandbox.close()
