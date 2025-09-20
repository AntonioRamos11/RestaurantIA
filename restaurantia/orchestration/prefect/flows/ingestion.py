from prefect import flow, task
import pandas as pd
from sqlalchemy import create_engine
from backend.app.db.session import get_db_session

@task
def load_data_from_csv(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file into a DataFrame."""
    return pd.read_csv(file_path)

@task
def ingest_data_to_db(data: pd.DataFrame):
    """Ingest data into the database."""
    engine = create_engine("postgresql://user:password@localhost/dbname")
    with get_db_session() as session:
        data.to_sql('your_table_name', con=engine, if_exists='append', index=False)

@flow
def ingestion_flow(file_path: str):
    """Main flow for data ingestion."""
    data = load_data_from_csv(file_path)
    ingest_data_to_db(data)