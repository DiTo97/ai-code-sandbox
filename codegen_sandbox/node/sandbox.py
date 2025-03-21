import textwrap
import typing

from codegen_sandbox.node.requirements import compliance_script
from codegen_sandbox.sandbox import BaseCodegenSandbox


class NodejsCodegenSandbox(BaseCodegenSandbox):
    """Sandbox environment for executing Node.js code safely."""

    def _init_image_config(self):
        self._base_image_name = "node:lts-slim"
        self._coding_language = "node"

    def _custom_image_dockerfile(self, image_name: str) -> str:
        return f"FROM {image_name}\nWORKDIR /sandbox\nRUN npm install {' '.join(self.requirements + ['semver@^7.0.0'])}"

    def _compliance_script(self, requirements: typing.List[str]) -> str:
        return compliance_script.replace("{{requirements}}", str(requirements))

    def _prepare_code_command(self, code: str) -> str:
        code = textwrap.dedent(code)
        escaped_code = code.replace("'", "'\"'\"'")
        exec_command = f"node -e '{escaped_code}'"
        return exec_command
