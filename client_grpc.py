# Client_grpc.py

import grpc 
import pandas as pd
from forecaster_pb2 import ForecastRequest, DataPoint
from forecaster_pb2_grpc import TimeSeriesForecasterStub

# Load data (same as before)
df = pd.read_csv("Electric_Production.csv")
date_col = df.columns[0]
value_col = df.columns[1]

# Prepare gRPC request
request = ForecastRequest(
    data=[
        DataPoint(ds=row[date_col], y=row[value_col])
        for _, row in df.iterrows()
    ],
    periods = 30,
    freq = "D"
)

# Send request to gRPC server 
channel = grpc.insecure_channel("localhost:50051")
stub = TimeSeriesForecasterStub(channel)
response = stub.Forecast(request)

# Print results 
print(f"Forecasted {len(response.forecast)} periods:")
print(f"First date: {response.forecast[0].ds}")
print(f"Last date: {response.forecast[-1].ds}")