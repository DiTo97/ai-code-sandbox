import textwrap
import typing

from codegen_sandbox.sandbox import BaseCodegenSandbox
from codegen_sandbox.python.requirements import compliance_script


class PythonCodegenSandbox(BaseCodegenSandbox):
    """Sandbox environment for executing Python code safely."""
    def _init_image_config(self):
        self._base_image_name = "python:3.9-slim"
        self._coding_language = "python"
    
    def _custom_image_dockerfile(self, image_name: str) -> str:
        return f"FROM {image_name}\nRUN pip install {' '.join(self.requirements + ['packaging'])}"
    
    def _compliance_script(self, requirements: typing.List[str]) -> str:
        return compliance_script.format(requirements=requirements)
    
    def _prepare_code_command(self, code: str) -> str:
        code = textwrap.dedent(code)

        escaped_code = code.replace("'", "'\"'\"'")
        exec_command = f"python -c '{escaped_code}'"

        return exec_command
