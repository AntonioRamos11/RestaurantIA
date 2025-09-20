from prefect import flow, task
from ml.models.demand.train import train_demand_model
from ml.models.churn.train import train_churn_model
from ml.models.recommender.train import train_recommender_model

@task
def train_models():
    train_demand_model()
    train_churn_model()
    train_recommender_model()

@flow
def training_flow():
    train_models()

if __name__ == "__main__":
    training_flow()