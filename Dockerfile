# Use Python 3.10 slim image to reduce size
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python build essentials and upgrade pip
RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir setuptools==68.2.2 wheel==0.41.2

# Install Python dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=1000 \
    snet.cli grpcio grpcio-tools pandas

# Install Prophet separately (requires building from source)
RUN pip install --no-cache-dir --default-timeout=1000 prophet

# Install snet-daemon
RUN wget https://github.com/singnet/snet-daemon/releases/download/v5.1.6/snetd-linux-amd64-v5.1.6 \
    && chmod +x snetd-linux-amd64-v5.1.6 \
    && mv snetd-linux-amd64-v5.1.6 /usr/local/bin/snetd

# Add explicit port exposures
EXPOSE 7000 8000 2379 2380

WORKDIR /app
COPY . .

CMD ["bash", "-c", "snetd --config snetd.config.json & python3 forecast_server.py"]