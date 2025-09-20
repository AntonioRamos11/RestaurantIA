from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd
import joblib

def evaluate_model(model_path: str, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    model = joblib.load(model_path)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5

    evaluation_metrics = {
        'Mean Absolute Error': mae,
        'Mean Squared Error': mse,
        'Root Mean Squared Error': rmse
    }

    return evaluation_metrics

def main():
    # Load test data
    X_test = pd.read_csv('path/to/X_test.csv')
    y_test = pd.read_csv('path/to/y_test.csv')

    # Path to the trained model
    model_path = 'path/to/trained_model.joblib'

    # Evaluate the model
    metrics = evaluate_model(model_path, X_test, y_test)
    print(metrics)

if __name__ == "__main__":
    main()