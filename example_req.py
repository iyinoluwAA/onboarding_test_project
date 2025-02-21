import pandas as pd
import requests
from datetime import datetime # <-- New import for timestamps

# Debug mode switch (True = show logs, False - silent)
debug_mode = True # You can flip this to false later!

def log_message(message: str):
    """Print messages if debug_mode is True"""
    if debug_mode:
        timestamp = datetime.now().strftime("%H:%M:%S") # Get current time
        print(f"[{timestamp}] DEBUG: {message}")

def load_and_prepare_data(csv_path: str):
    """
    Load time series data from CSV file.
    Expects CSV to have at least two columns:
    - date column (can be named 'date', 'timestamp', etc.)
    - value column (can be named 'value', 'sales', etc.)
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Identify date column (assumes first column is date)
    date_col = df.columns[0]
    value_col = df.columns[1]
     
    log_message(f"Detected date column: '{date_col}', value column: '{value_col}'")
    
    # Convert dates to datetime if they aren't already
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Sort by date
    df = df.sort_values(by=date_col)
    
    # Prepare data in the format expected by the API
    data = {
        "data": [
            {"ds": row[date_col].strftime('%Y-%m-%d'),"y": row[value_col]}
            for _, row in df.iterrows()
        ],
        "periods": 30,  # Forecast 30 periods ahead
        "freq": "D", # Daily frequency
        "changepoint_prior_scale": 0.08,
        "seasonality_prior_scale": 12.0,
        "seasonality_mode": "multiplicative"
    }
    
    return data

def get_forecast(data: dict, api_url: str = "http://localhost:8000/forecast"):

    """Send request to the forecasting service and get predictions"""
    log_message("Sending forecast request to server...")

    try:
        response = requests.post(api_url, json=data)
        response.raise_for_status()  # Raise exception for bad status codes
        log_message("Forecast request successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        log_message(f"Request failed: {e}")
        return None

def save_forecast(forecast: dict, output_path: str):
    """Save the forecast results to a CSV file"""
    log_message(f"Saving forecast to {output_path}...")

    # Create DataFrame with forecast results
    df = pd.DataFrame({
        'date': [point["ds"] for point in forecast],
        'forecast': [point["yhat"] for point in forecast],
        'lower_bound': [point["yhat_lower"] for point in forecast],
        'upper_bound': [point["yhat_upper"] for point in forecast]
    })
    
    # Add components if they exist
    if 'components' in forecast and forecast['components']:
        for component, values in forecast['components'].items():
            df[f'component_{component}'] = values
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Forecast saved to {output_path}")
    log_message("Forecast saved successfully!")

def main():
    csv_path = "Electric_Production.csv"  
    output_path = "results.csv"
    
    # Load and prepare data
    log_message("Starting forecast pipeline...")
    data = load_and_prepare_data(csv_path)
    
    # Get forecast
    log_message("Requesting forecast...")
    forecast = get_forecast(data)
    
    if forecast:
        # Save results
        save_forecast(forecast, output_path)
        log_message("Pipeline completed! 🎉")
        
        # Print some basic stats
        print("\nForecast Summary:")
        print(f"Number of periods forecasted: {len(forecast)}")
        print(f"Last historical date: {forecast[0]['ds']}")
        print(f"Last forecast date: {forecast[-1]['ds']}")

if __name__ == "__main__":
    main()