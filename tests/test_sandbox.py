from ai_code_sandbox.sandbox import AICodeSandbox


def test_sandbox_simple():
    with AICodeSandbox(packages=[]) as sandbox:
        code = """
        print("hello, I'm a sandbox")
        """
        
        output = sandbox.run_code(code)
        assert "hello, I'm a sandbox" in output


def test_sandbox_with_environment():
    sandbox = AICodeSandbox(packages=[])
    
    try:
        code = """
        import os
        print(os.environ["example"])
        """
        
        output = sandbox.run_code(code, env_vars={"example": "1"})
        assert output.strip() == "1"
    finally:
        sandbox.close()


def test_sandbox_with_packages():
    sandbox = AICodeSandbox(packages=["requests"])
    
    try:
        code = """
        import requests
        """
        
        output = sandbox.run_code(code)
        assert output == "No output"
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
        assert "exit code 124" in output
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
        assert "KeyError: 'example'" in output
    finally:
        sandbox.close()


def test_sandbox_without_packages():
    sandbox = AICodeSandbox(packages=[])
    
    try:
        code = """
        import requests
        """

        output = sandbox.run_code(code)
        assert "ModuleNotFoundError: No module named 'requests'" in output
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
        assert output == "No output"
    finally:
        sandbox.close()
