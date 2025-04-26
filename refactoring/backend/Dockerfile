FROM python:3.10

# Install iptables and other necessary dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
