from prefect import flow, task
from ml.models.demand.evaluate import evaluate_model
from ml.models.churn.evaluate import evaluate_churn_model
from ml.models.recommender.evaluate import evaluate_recommender_model

@task
def score_demand_model():
    return evaluate_model()

@task
def score_churn_model():
    return evaluate_churn_model()

@task
def score_recommender_model():
    return evaluate_recommender_model()

@flow
def scoring_flow():
    demand_score = score_demand_model()
    churn_score = score_churn_model()
    recommender_score = score_recommender_model()
    
    return {
        "demand_score": demand_score,
        "churn_score": churn_score,
        "recommender_score": recommender_score
    }