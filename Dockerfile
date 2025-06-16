FROM python:3.10-slim
WORKDIR /opt/moneymaker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "start_all.py"]
