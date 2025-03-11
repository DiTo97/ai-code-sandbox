import pytest

from codegen_sandbox import init_codegen_sandbox, BaseCodegenSandbox, SandboxError


@pytest.fixture(scope="function")
def sandbox():
    sandbox = init_codegen_sandbox("python")
    yield sandbox
    sandbox.close()


def test_write_and_read_file(sandbox: BaseCodegenSandbox):
    filename = "output.txt"
    content = "hello, I'm a sandbox"
    sandbox.write_file(filename, content)
    assert content == sandbox.read_file(filename)


def test_write_and_read_binary_file(sandbox: BaseCodegenSandbox):
    filename = "output.bin"
    content = b"\x00\x01\x02\x03"
    sandbox.write_file(filename, content)
    assert content == sandbox.read_file(filename).encode("latin1")


def test_delete_file(sandbox: BaseCodegenSandbox):
    filename = "output.txt"
    content = ""
    sandbox.write_file(filename, content)
    sandbox.delete_file(filename)

    with pytest.raises(SandboxError):
        sandbox.read_file(filename)


def test_write_dir(sandbox: BaseCodegenSandbox):
    directory = "output"
    sandbox.write_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code == 0


def test_write_nested_dir(sandbox: BaseCodegenSandbox):
    directory = "output/nested"
    sandbox.write_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code == 0


def test_delete_dir(sandbox: BaseCodegenSandbox):
    directory = "output"
    sandbox.write_dir(directory)
    sandbox.delete_dir(directory)
    output = sandbox.container.exec_run(["sh", "-c", f"test -d {directory}"])
    assert output.exit_code != 0
