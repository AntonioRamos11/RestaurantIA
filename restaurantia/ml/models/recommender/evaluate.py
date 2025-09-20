from sklearn.metrics import mean_squared_error, mean_absolute_error
import pandas as pd

def evaluate_recommender_model(predictions: pd.Series, actuals: pd.Series) -> dict:
    """
    Evaluate the performance of the recommender model using various metrics.

    Parameters:
    - predictions: A pandas Series containing the predicted values.
    - actuals: A pandas Series containing the actual values.

    Returns:
    - A dictionary containing evaluation metrics.
    """
    mse = mean_squared_error(actuals, predictions)
    mae = mean_absolute_error(actuals, predictions)

    return {
        'mean_squared_error': mse,
        'mean_absolute_error': mae,
        'root_mean_squared_error': mse ** 0.5
    }

def main():
    # Example usage
    # Load predictions and actuals from a data source
    predictions = pd.Series([4, 5, 3, 4, 5])
    actuals = pd.Series([5, 5, 2, 4, 5])

    metrics = evaluate_recommender_model(predictions, actuals)
    print(metrics)

if __name__ == "__main__":
    main()