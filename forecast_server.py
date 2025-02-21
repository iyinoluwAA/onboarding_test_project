import grpc
from concurrent import futures
import time
import forecaster_pb2
import forecaster_pb2_grpc

class TimeSeriesForecasterServicer(forecaster_pb2_grpc.TimeSeriesForecasterServicer):
    def Forecast(self, request, context):
        # Mock forecasting logic (replace with your Prophet/ARIMA code)
        forecast_points = []
        last_date = request.data[-1].ds  # Get last date in input
        
        for i in range(1, request.periods + 1):
            forecast_points.append(forecaster_pb2.ForecastPoint(
                ds=f"2023-01-{i+1}",  # Simplified date logic
                yhat=100 + i*5,
                yhat_lower=90 + i*5,
                yhat_upper=110 + i*5
            ))
        
        return forecaster_pb2.ForecastResponse(forecast=forecast_points)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    forecaster_pb2_grpc.add_TimeSeriesForecasterServicer_to_server(
        TimeSeriesForecasterServicer(), server
    )
    server.add_insecure_port("[::]:8000")
    server.start()
    print("Server running on port 8000")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()