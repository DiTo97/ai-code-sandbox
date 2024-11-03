from ai_code_sandbox.sandbox import AICodeSandbox


def test_sandbox_simple():
    sandbox = AICodeSandbox(packages=[])
    
    try:
        code = """
        print("hello, I'm a sandbox")
        """
        
        output = sandbox.run_code(code)
        assert "hello, I'm a sandbox" in output
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
