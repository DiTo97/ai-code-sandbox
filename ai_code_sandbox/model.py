from dataclasses import dataclass


@dataclass
class SandboxResponse:
    stdout: str
    stderr: str
