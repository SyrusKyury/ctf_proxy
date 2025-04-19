FROM python:3.11-slim

# Install iptables and other necessary dependencies
RUN apt-get update && \
    apt-get install -y iptables && \
    apt-get clean

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
