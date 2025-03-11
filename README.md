# Codegen Sandbox

> [!warning]
> The repository is being maintained independently from [AICodeSanbox](https://github.com/typper-io/ai-code-sandbox), its original fork.

Codegen Sandbox is a Python library designed to provide a secure and isolated environment for executing AI and machine learning code, particularly for Language Models (LLMs). It leverages Docker containers to create sandboxes, enabling safe execution of potentially untrusted AI-generated code.

> [!note]
> At the moment, the library supports Node.js and Python sandboxes.

## TODOs

- [ ] [better base Docker images](https://huggingface.co/docs/smolagents/v1.10.0/en/tutorials/secure_code_execution)
- [ ] reference sandbox agent
- [ ] sandbox as a tool/service

## Features

- Create isolated environments using Docker containers
- Securely run AI-generated code or LLM outputs
- Install custom packages in the sandbox
- Execute code safely within the sandbox
- Read and write files within the sandbox environment
- Automatically clean up resources after use
- Supports any Python or Node.js image, but soon many more!

## Key Advantages

- **Security**: Isolates AI-generated code execution, protecting your system from potentially harmful operations.
- **Speed**: Optimized container creation and management for quick sandbox setup and execution.
- **Customization**: Easily add specific packages or use custom Docker images to suit your AI and ML needs.
- **Resource Control**: Limit CPU and memory usage to prevent resource abuse.
- **Flexibility**: Run various types of AI models and code snippets without worrying about system integrity.
- **Easy Clean-up**: Automatic resource management ensures no leftover containers or images.

## Requirements

To run Codegen Sandbox, you need:

- Python 3.7+
- Docker installed and running on your system
- Sufficient permissions to create and manage Docker containers
- Internet connection (for initial package downloads)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/typper-io/ai-code-sandbox.git
   cd ai-code-sandbox
   ```

2. Install the required Python packages:
   ```
   python -m pip install -r requirements.txt
   ```

3. Install the package:
   ```
   python -m pip install -e .
   ```

## Usage

Here's a basic example of how to use Codegen Sandbox:

```python
from codegen_sandbox import init_codegen_sandbox


code = """
import numpy
import pandas
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential


X = numpy.random.rand(1000, 10)
y = numpy.random.randint(0, 2, 1000)

print(X.shape, y.shape)

X_training, X_test, y_training, y_test = train_test_split(X, y, test_size=0.2)

model = Sequential([
    Input(shape=(10,)),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

history = model.fit(X_training, y_training, epochs=10, validation_split=0.2, verbose=0)

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"test accuracy — {accuracy:.4f}")
"""


if __name__ == "__main__":
    sandbox = init_codegen_sandbox(
        "python",
        requirements=["numpy", "pandas", "scikit-learn", "tensorflow"],
        config="medium"
    )

    try:        
        output = sandbox.run_code(code)

        print(output.stdout)
        print(output.stderr)
    except Exception as e:
        print(str(e))
    finally:
        sandbox.close()
```

## Running in Docker

You can also run Codegen Sandbox inside a Docker container. This setup uses Docker-in-Docker (DinD) to allow the Codegen Sandbox to create and manage Docker containers from within a Docker container.

Example `Dockerfile`:

```dockerfile
FROM docker:dind

RUN apk add --no-cache python3 py3-pip

WORKDIR /service

COPY . ./codegen-sandbox

RUN python3 -m venv /service/.venv
ENV PATH="/service/.venv/bin:$PATH"

RUN pip3 install --upgrade pip
RUN pip3 install -e codegen-sandbox

CMD ["python3", "codegen-sandbox/examples/classifcation.py"]
```

The docker compose `docker-compose.yml`:

```yaml
services:
  sandbox:
    build: .
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    privileged: true
    environment:
      - DOCKER_TLS_CERTDIR=""
```

## API Reference

### `init_codegen_sandbox`

Create a new sandbox environment for a given coding language.

- `coding_language`: Coding language to use for the sandbox.
- `custom_image` (optional): Name of a custom Docker image to use.
- `requirements` (optional): List of packages to install in the sandbox.
- `network_mode` (optional): Network mode to use for the sandbox. Defaults to "none".
- `config` (optional): Ready-made specs configuration for the sandbox. Defaults to "small".

### `BaseCodegenSandbox.run_requirements_compliance`

Check if the specified packages are available in the sandbox.

- `requirements`: List of package requirements.

### `BaseCodegenSandbox.run_code`

Execute code in the sandbox.

- `code`: String containing code to execute.
- `env_vars` (optional): Dictionary of environment variables to set for the execution.
- `timeout` (optional): Execution timeout in seconds.

### `BaseCodegenSandbox.write_file`

Write content to a file in the sandbox.

- `content`: String content to write to the file.
- `filename`: Name of the file to create or overwrite.

### `BaseCodegenSandbox.read_file`

Read content from a file in the sandbox.

- `filename`: Name of the file to read.

### `BaseCodegenSandbox.delete_file`

Delete a file in the sandbox.

- `filename`: Name of the file to delete.

### `BaseCodegenSandbox.write_dir`

Create a directory in the sandbox, including any necessary parent directories.

- `directory`: Path of the directory to create.

### `BaseCodegenSandbox.delete_dir`

Delete a directory in the sandbox.

- `directory`: Path of the directory to delete.

### `BaseCodegenSandbox.close()`

Remove all resources created by the sandbox.

## Security Considerations

While Codegen Sandbox provides a secure environment for running AI-generated code, it's important to note that no sandbox solution is completely foolproof. Users should still exercise caution and implement additional security measures when dealing with potentially malicious or untrusted AI-generated code.

## Contributing

Contributions to Codegen Sandbox are welcome! Please feel free to submit a pull request.

```shell
python -m pip install pytest
```

```shell
python -m pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
