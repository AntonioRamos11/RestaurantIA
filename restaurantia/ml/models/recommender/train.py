from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import joblib

class RecommenderModel:
    def __init__(self, data):
        self.data = data
        self.model = None

    def preprocess_data(self):
        # Example preprocessing steps
        self.data.fillna(0, inplace=True)
        self.data['user_id'] = self.data['user_id'].astype('category').cat.codes
        self.data['item_id'] = self.data['item_id'].astype('category').cat.codes

    def train(self):
        self.preprocess_data()
        X = self.data[['user_id', 'item_id']]
        y = self.data['rating']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Example model training (using a simple collaborative filtering approach)
        from sklearn.neighbors import NearestNeighbors
        self.model = NearestNeighbors(metric='cosine', algorithm='brute')
        self.model.fit(X_train)

        # Evaluate the model
        predictions = self.model.kneighbors(X_test, return_distance=False)
        mse = mean_squared_error(y_test, predictions)
        print(f'Model Mean Squared Error: {mse}')

    def save_model(self, filename):
        joblib.dump(self.model, filename)

if __name__ == "__main__":
    # Load your data here
    data = pd.read_csv('path_to_your_data.csv')
    recommender = RecommenderModel(data)
    recommender.train()
    recommender.save_model('recommender_model.pkl')