# AICodeSandbox

AICodeSandbox is a Python library designed to provide a secure and isolated environment for executing AI and machine learning code, particularly for Language Models (LLMs). It leverages Docker containers to create sandboxes, enabling safe execution of potentially untrusted AI-generated code.

## Features

- Create isolated Python environments using Docker containers
- Securely run AI-generated code or LLM outputs
- Install custom Python packages in the sandbox
- Execute Python code safely within the sandbox
- Read and write files within the sandbox environment
- Automatically clean up resources after use

## Key Advantages

- **Security**: Isolates AI-generated code execution, protecting your system from potentially harmful operations.
- **Speed**: Optimized container creation and management for quick sandbox setup and execution.
- **Customization**: Easily add specific Python packages or use custom Docker images to suit your AI and ML needs.
- **Resource Control**: Limit CPU and memory usage to prevent resource abuse.
- **Flexibility**: Run various types of AI models and code snippets without worrying about system integrity.
- **Easy Clean-up**: Automatic resource management ensures no leftover containers or images.

## Requirements

To run AICodeSandbox, you need:

- Python 3.7+
- Docker installed and running on your system
- `docker` Python package
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

Here's a basic example of how to use AICodeSandbox:

```python
from ai_code_sandbox import AICodeSandbox


code = """
import numpy
import pandas
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential


X = numpy.random.rand(1000, 10)
y = numpy.random.randint(0, 2, 1000)

print(X.shape, y.shape)

X_training, X_test, y_training, y_test = train_test_split(X, y, test_size=0.2)

model = Sequential([
    Dense(64, activation="relu", input_shape=(10,)),
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

history = model.fit(X_training, y_training, epochs=10, validation_split=0.2, verbose=0)

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"test accuracy — {accuracy:.4f}")
"""


if __name__ == "__main__":
    sandbox = AICodeSandbox(
        requirements=["numpy", "pandas", "scikit-learn", "tensorflow"], mem_limit="1g"
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

You can also run AICodeSandbox inside a Docker container. This setup uses Docker-in-Docker (DinD) to allow the AICodeSandbox to create and manage Docker containers from within a Docker container.

Example `Dockerfile`:

```dockerfile
FROM docker:dind

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt .
COPY README.md .
COPY ai_code_sandbox/ ./ai_code_sandbox/
COPY setup.py .

RUN python3 -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install -e .

COPY examples/ ./examples/

CMD ["python3", "examples/classifcation.py"]
```

The docker compose `docker-compose.yml`:

```yaml
services:
  ai_sandbox:
    build: .
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    privileged: true
    environment:
      - DOCKER_TLS_CERTDIR=""
```

## API Reference

### `AICodeSandbox(custom_image=None, requirements=None)`

Create a new sandbox environment.

- `custom_image` (optional): Name of a custom Docker image to use.
- `requirements` (optional): List of Python packages to install in the sandbox.
- `network_mode` (optional): Network mode to use for the sandbox. Defaults to "none".
- `mem_limit` (optional): Memory limit for the sandbox. Defaults to "100m".
- `cpu_period` (optional): CPU period for the sandbox. Defaults to 100000.
- `cpu_quota` (optional): CPU quota for the sandbox. Defaults to 50000.

### `sandbox.run_code(code, env_vars=None)`

Execute Python code in the sandbox.

- `code`: String containing Python code to execute.
- `env_vars` (optional): Dictionary of environment variables to set for the execution.
- `timeout` (optional): Execution timeout in seconds.

### `sandbox.write_file(content, filename)`

Write content to a file in the sandbox.

- `content`: String content to write to the file.
- `filename`: Name of the file to create or overwrite.

### `sandbox.read_file(filename)`

Read content from a file in the sandbox.

- `filename`: Name of the file to read.

### `sandbox.close()`

Remove all resources created by the sandbox.

## Security Considerations

While AICodeSandbox provides a secure environment for running AI-generated code, it's important to note that no sandbox solution is completely foolproof. Users should still exercise caution and implement additional security measures when dealing with potentially malicious or untrusted AI-generated code.

## Contributing

Contributions to AICodeSandbox are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.