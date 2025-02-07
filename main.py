from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet
import json

# Initialize the FastAPI app
app = FastAPI()

# Define the request model using Pydantic
class ForecastRequest(BaseModel):
    data: list
    periods: int
    freq: str

    #Add model parameters
    changepoint_prior_scale: float = 0.05
    seasonality_prior_scale: float = 10.0
    seasonality_mode: str = "additive"

# Define the /forecast endpoint
@app.post("/forecast")
def forecast(request: ForecastRequest):
    # Convert input data to a Pandas DataFrame
    df = pd.DataFrame(request.data, columns=["ds", "y"])

    # Initialize and fit the prophet model
    model = Prophet(
        changepoint_prior_scale=request.changepoint_prior_scale,
        seasonality_prior_scale=request.seasonality_prior_scale,
        seasonality_mode=request.seasonality_mode
    )

    # Fit the model to the historical data
    model.fit(df)

    # Create a future DataFrame for predictions
    future = model.make_future_dataframe(periods=request.periods, freq=request.freq)

    #Generate predictions
    forecast = model.predict(future)

    # Return the forecasted values (dates, predictions, and confidence intervals)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_dict(orient="records")

# Define the /parameters/default endpoint
@app.get("/parameters/default")
def get_default_parameters():
    # Intialize a prophet model
    model = Prophet()

    # Return the default parameters of the model
    return model.__dict__
    