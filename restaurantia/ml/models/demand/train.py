from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pandas as pd
import joblib

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def preprocess_data(data):
    # Example preprocessing steps
    data.fillna(0, inplace=True)
    X = data.drop('target', axis=1)
    y = data['target']
    return X, y

def train_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    return mae

def main():
    # Load and preprocess data
    data = load_data('path/to/your/data.csv')
    X, y = preprocess_data(data)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = train_model(X_train, y_train)

    # Evaluate the model
    mae = evaluate_model(model, X_test, y_test)
    print(f'Mean Absolute Error: {mae}')

    # Save the model
    joblib.dump(model, 'demand_forecasting_model.pkl')

if __name__ == '__main__':
    main()