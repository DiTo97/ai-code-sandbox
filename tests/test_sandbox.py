from ai_code_sandbox.sandbox import AICodeSandbox


def test_sandbox_simple():
    with AICodeSandbox(packages=[]) as sandbox:
        code = """
        print("hello, I'm a sandbox")
        """
        
        output = sandbox.run_code(code)

        assert "hello, I'm a sandbox" in output.stdout
        assert output.stderr == ""


def test_sandbox_with_environment():
    sandbox = AICodeSandbox(packages=[])
    
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


def test_sandbox_with_packages():
    sandbox = AICodeSandbox(packages=["requests"])
    
    try:
        code = """
        import requests
        """
        
        output = sandbox.run_code(code)
        
        assert output.stdout == ""
        assert output.stderr == ""
    finally:
        sandbox.close()


def test_sandbox_with_timeout():
    sandbox = AICodeSandbox(packages=[])
    
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
    sandbox = AICodeSandbox(packages=[])
    
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


def test_sandbox_without_packages():
    sandbox = AICodeSandbox(packages=[])
    
    try:
        code = """
        import requests
        """

        output = sandbox.run_code(code)

        assert output.stdout == ""
        assert "ModuleNotFoundError: No module named 'requests'" in output.stderr
    finally:
        sandbox.close()

    
def test_sandbox_without_timeout():
    sandbox = AICodeSandbox(packages=[])
    
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
