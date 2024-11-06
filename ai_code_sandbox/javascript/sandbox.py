import textwrap
import typing

from ai_code_sandbox.sandbox import BaseCodegenSandbox


class NodejsCodegenSandbox(BaseCodegenSandbox):
    """Sandbox environment for executing Node.js code safely."""

    def _init_image_config(self):
        self._base_image_name = "node:22.10.0-slim"
        self._coding_language = "javascript"

    def _custom_image_dockerfile(self, image_name: str) -> str:
        return f"FROM {image_name}\nRUN npm install {' '.join(self.requirements)}"

    def _compliance_script(self, requirements: typing.List[str]) -> str:
        compliance_script = """
        const { execSync } = require('child_process');
        
        const requirements = {requirements};

        requirements.forEach(req => {
            try {
                const [pkg, version] = req.split('@');
                const installedVersion = execSync(`npm list ${pkg} --depth=0`).toString().match(/@([0-9.]+)/)[1];
                if (installedVersion !== version) {
                    throw new Error(`Version mismatch for ${pkg}. Expected: ${version}, Installed: ${installedVersion}`);
                }
            } catch (error) {
                console.error(`Package check failed: ${error.message}`);
                process.exit(1);
            }
        });

        console.log('All packages are compliant.');
        process.exit(0);
        """
        return compliance_script.format(requirements=requirements)

    def _prepare_code_command(self, code: str) -> str:
        code = textwrap.dedent(code)
        escaped_code = code.replace("'", "'\"'\"'")
        exec_command = f"node -e '{escaped_code}'"
        return exec_command
