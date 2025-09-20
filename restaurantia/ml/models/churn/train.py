from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd
import joblib

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def preprocess_data(data):
    # Example preprocessing steps
    data.fillna(0, inplace=True)
    X = data.drop('churn', axis=1)
    y = data['churn']
    return X, y

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model, X_test, y_test

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    print(report)

def save_model(model, file_path):
    joblib.dump(model, file_path)

if __name__ == "__main__":
    data = load_data('path/to/churn_data.csv')
    X, y = preprocess_data(data)
    model, X_test, y_test = train_model(X, y)
    evaluate_model(model, X_test, y_test)
    save_model(model, 'path/to/save/churn_model.pkl')