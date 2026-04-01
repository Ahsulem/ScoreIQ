FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install the project as a package so 'src' is recognized
RUN pip install -e .

# Now train the model
RUN python src/components/data_ingestion.py

EXPOSE 5000

CMD ["python", "application.py"]