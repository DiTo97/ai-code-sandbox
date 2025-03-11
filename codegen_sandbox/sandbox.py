import io
import os
import shlex
import tarfile
import time
import typing
import uuid
from abc import ABC, abstractmethod
from typing import Any

import docker
import docker.models.containers
import docker.models.images

from codegen_sandbox.config import SandboxConfig, available, readymade
from codegen_sandbox.error import SandboxError, SandboxConfigError
from codegen_sandbox.model import SandboxResponse


class BaseCodegenSandbox(ABC):
    """
    Base sandbox environment for executing code safely.

    This class creates a Docker container with a suitable environment, optionally installs 
    additional requirements, and provides methods to execute code, read, write 
    and delete files, and write and delete directories within the sandbox.

    Attributes:
        client (docker.DockerClient): Docker client for managing containers and images.
        config (SandboxConfig): Specs configuration for the sandbox.
        container (docker.models.containers.Container): The Docker container used as a sandbox.
        requirements (list): List of packages to install in the sandbox.
        temp_image (docker.models.images.Image): Temporary Docker image created for the sandbox.
        _base_image_name (str): Name of the base Docker image to use for the sandbox.
        _coding_language (str): Coding language used in the sandbox.
    """
    client: docker.DockerClient
    config: SandboxConfig
    container: docker.models.containers.Container
    requirements: typing.List[str]
    temp_image: typing.Optional[docker.models.images.Image]
    _base_image_name: str
    _coding_language: str

    def __init__(
        self, 
        custom_image_name: typing.Optional[str] = None, 
        requirements: typing.Optional[typing.List[str]] = None, 
        network_mode: str = "none", 
        config: str = "small"
    ):
        """
        Initialize the sandbox.

        Args:
            custom_image_name (str, optional): Name of a custom Docker image to use. Defaults to None.
            requirements (list, optional): List of packages to install in the sandbox. Defaults to None.
            network_mode (str, optional): Network mode to use for the sandbox. Defaults to "none".
            config (str, optional): Ready-made specs configuration for the sandbox. Defaults to "small".
        """
        if config not in available:
            raise SandboxConfigError(config)
        
        self._init_image_config()

        self.container = None
        self.temp_image = None
        self.requirements = requirements or []
        self.client = docker.from_env()
        self.config = readymade[config]

        self._setup_sandbox(custom_image_name, network_mode)

    @abstractmethod
    def _init_image_config(self):
        """Initialize the necessary image config for the sandbox"""
        ...

    @abstractmethod
    def _custom_image_dockerfile(self, image_name: str) -> str:
        """Generate the Dockerfile for a custom image"""
        ...

    @abstractmethod
    def _compliance_script(self, requirements: typing.List[str]) -> str:
        """Generate the script to check for compliance of package requirements"""
        ...

    @abstractmethod
    def _prepare_code_command(self, code: str) -> str:
        """Prepare the shell command to execute the code"""
        ...

    def _setup_sandbox(self, custom_image_name: typing.Optional[str], network_mode: str):
        """Set up the sandbox environment."""
        image_name = custom_image_name or self._base_image_name
        
        if self.requirements:
            dockerfile = self._custom_image_dockerfile(image_name)
            dockerfile_obj = io.BytesIO(dockerfile.encode('utf-8'))
            self.temp_image = self.client.images.build(fileobj=dockerfile_obj, rm=True)[0]
            image_name = self.temp_image.id

        self.container = self.client.containers.run(
            image_name,
            name=f"{self._coding_language}-sandbox-{uuid.uuid4().hex[:8]}",
            command="tail -f /dev/null",
            detach=True,
            network_mode=network_mode,
            mem_limit=self.config.mem_limit,
            cpu_period=100000,
            cpu_quota=self.config.cpu_quota
        )

    def write_file(self, filename: str, content: Any):
        """
        Write content to a file in the sandbox, creating directories if they don't exist.

        Args:
            filename (str): Name of the file to create or overwrite.
            content (str or bytes): Content to write to the file.

        Raises:
            SandboxError: If writing to the file fails.
        """
        directory = os.path.dirname(filename)

        if directory:
            self.write_dir(directory)

        tar_stream = io.BytesIO()

        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            if isinstance(content, str):
                file_data = content.encode('utf-8')
            else:
                file_data = content

            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(file_data)
            tar.addfile(tarinfo, io.BytesIO(file_data))

        tar_stream.seek(0)

        try:
            self.container.put_archive('/', tar_stream)
        except Exception as e:
            raise SandboxError(f"Failed to write file: {str(e)}")

        check_command = f'test -f {shlex.quote(filename)}'
        check_result = self.container.exec_run(["sh", "-c", check_command])

        if check_result.exit_code != 0:
            raise SandboxError(f"Failed to write file: {filename}")

    def read_file(self, filename: str):
        """
        Read content from a file in the sandbox.

        Args:
            filename (str): Name of the file to read.

        Returns:
            str: Content of the file.

        Raises:
            SandboxError: If reading the file fails.
        """
        result = self.container.exec_run(["cat", filename])
        
        if result.exit_code != 0:
            raise SandboxError(f"Failed to read file: {result.output.decode('utf-8')}")
        
        return result.output.decode('utf-8')
    
    def delete_file(self, filename: str):
        """
        Delete a file in the sandbox.

        Args:
            filename (str): Name of the file to delete.

        Raises:
            SandboxError: If deleting the file fails.
        """
        delete_command = f'rm -f {shlex.quote(filename)}'
        delete_result = self.container.exec_run(["sh", "-c", delete_command])
        
        if delete_result.exit_code != 0:
            raise SandboxError(f"Failed to delete file: {delete_result.output.decode('utf-8')}")

    def write_dir(self, directory: str):
        """
        Create a directory in the sandbox, including any necessary parent directories.

        Args:
            directory (str): Path of the directory to create.

        Raises:
            SandboxError: If creating the directory fails.
        """
        mkdir_command = f'mkdir -p {shlex.quote(directory)}'
        mkdir_result = self.container.exec_run(["sh", "-c", mkdir_command])
        
        if mkdir_result.exit_code != 0:
            raise SandboxError(f"Failed to create directory: {mkdir_result.output.decode('utf-8')}")
        
    def delete_dir(self, directory: str):
        """
        Delete a directory in the sandbox.

        Args:
            directory (str): Path of the directory to delete.

        Raises:
            SandboxError: If deleting the directory fails.
        """
        rmdir_command = f'rm -rf {shlex.quote(directory)}'
        rmdir_result = self.container.exec_run(["sh", "-c", rmdir_command])
        
        if rmdir_result.exit_code != 0:
            raise SandboxError(f"Failed to delete directory: {rmdir_result.output.decode('utf-8')}")
    
    def run_requirements_compliance(self, requirements: typing.List[str]) -> SandboxResponse:
        """
        Check if the specified packages are available in the sandbox.

        Args:
            requirements (list): List of package requirements.
        """
        if not requirements:
            return SandboxResponse(stdout="", stderr="")
        
        if not self.requirements:
            return SandboxResponse(stdout="", stderr="SandboxRequirementsError: requirements-free sandbox")

        output = self.run_code(self._compliance_script(requirements=requirements))
        return output

    def run_code(
        self,
        code: str, 
        env_vars: typing.Optional[typing.Dict[str, Any]] = None, 
        timeout: typing.Optional[int] = None
    ) -> SandboxResponse:
        """
        Execute code in the sandbox.

        Args:
            code (str): Code to execute.
            env_vars (dict, optional): Environment variables to set for the execution. Defaults to None.
            timeout (int, optional): Execution timeout in seconds. Defaults to None, i.e., disabled.

        Returns:
            SandboxResponse: Output (stdout) and error messages (stderr) of the executed code.
        """
        if env_vars is None:
            env_vars = {}
        
        exec_command = self._prepare_code_command(code)

        if timeout:
            exec_command = f"timeout {timeout}s {exec_command}"
        
        exec_result = self.container.exec_run(
            ["sh", "-c", exec_command],
            demux=True,
            environment=env_vars
        )
        
        status = exec_result.exit_code
        stdout, stderr = exec_result.output

        stdout = stdout.decode("utf-8") if stdout else ""
        stderr = stderr.decode("utf-8") if stderr else ""

        if status != 0:
            stderr = f"(exit code {status})" + stderr

        return SandboxResponse(stdout=stdout, stderr=stderr)

    def close(self):
        """
        Remove all resources created by this sandbox.

        This method should be called when the sandbox is no longer needed to clean up Docker resources.
        """
        if self.container:
            try:
                self.container.stop(timeout=10)
                self.container.remove(force=True)
            except Exception as e:
                print(f"Error stopping/removing container: {str(e)}")
            finally:
                self.container = None

        time.sleep(2)

        if self.temp_image:
            try:
                for _ in range(3):
                    try:
                        self.client.images.remove(self.temp_image.id, force=True)
                        break
                    except Exception as e:
                        print(f"Attempt to remove image failed: {str(e)}")
                        time.sleep(2)
                else:
                    print("Failed to remove temporary image after multiple attempts")
            except Exception as e:
                print(f"Error removing temporary image: {str(e)}")
            finally:
                self.temp_image = None

    def __del__(self):
        """Ensure resources are cleaned up when the object is garbage collected."""
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def init_codegen_sandbox(
    coding_language: str,
    *,
    custom_image_name: typing.Optional[str] = None, 
    requirements: typing.Optional[typing.List[str]] = None, 
    network_mode: str = "none", 
    config: str = "small"
) -> BaseCodegenSandbox:
    """
    Initialize the sandbox for a given coding language.

    Args:
        coding_language (str): Coding language to use for the sandbox.
        custom_image_name (str, optional): Name of a custom Docker image to use. Defaults to None.
        requirements (list, optional): List of packages to install in the sandbox. Defaults to None.
        network_mode (str, optional): Network mode to use for the sandbox. Defaults to "none".
        config (str, optional): Ready-made specs configuration for the sandbox. Defaults to "small".

    Returns:
        BaseCodegenSandbox: Instance of the codegen sandbox
    """
    if coding_language == "python":
        from codegen_sandbox.python.sandbox import PythonCodegenSandbox

        #
        return PythonCodegenSandbox(
            custom_image_name=custom_image_name,
            requirements=requirements,
            network_mode=network_mode,
            config=config
        )
    elif coding_language == "node":
        from codegen_sandbox.node.sandbox import NodejsCodegenSandbox

        #
        return NodejsCodegenSandbox(
            custom_image_name=custom_image_name,
            requirements=requirements,
            network_mode=network_mode,
            config=config
        )
    
    raise ValueError(f"unsupported coding language: {coding_language}")
