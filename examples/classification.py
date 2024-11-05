from ai_code_sandbox import AICodeSandbox


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
    sandbox = AICodeSandbox(
        requirements=["numpy", "pandas", "scikit-learn", "tensorflow"], config="medium"
    )

    try:        
        output = sandbox.run_code(code)

        print(output.stdout)
        print(output.stderr)
    except Exception as e:
        print(str(e))
    finally:
        sandbox.close()
