from concurrent import futures
import grpc 
import pandas as pd 
from prophet import Prophet
from forecaster_pb2 import ForecastResponse, ForecastPoint
from forecaster_pb2_grpc import TimeSeriesForecasterServicer, add_TimeSeriesForecasterServicer_to_server

class ForecasterServicer(TimeSeriesForecasterServicer):
    def Forecast(self, request, context):
        # Convert gRPC request to DataFrame 
        df = pd.DataFrame([
            {"ds": point.ds, "y": point.y}
            for point in request.data
        ])

        # Train Prophet model (Same as before!)
        model = Prophet()
        model.fit(df)

        # Generate future dates
        future = model.make_future_dataframe(
            periods = request.periods,
            freq = request.freq
        )

        # Predict
        forecast = model.predict(future)

        # Convert forecast to gRPC response
        return ForecastResponse(
            forecast=[
                ForecastPoint(
                    ds=row["ds"].strftime("%Y-%m-%d"),
                    yhat=row["yhat"],
                    yhat_lower=row["yhat_lower"],
                    yhat_upper=row["yhat_upper"]
                )
                for _, row in forecast.iterrows()
            ]
        )
    

# Start the server 
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
add_TimeSeriesForecasterServicer_to_server(ForecasterServicer(), server)
server.add_insecure_port("[::]:50051") # Listen on port 50051
server.start()
server.wait_for_termination()