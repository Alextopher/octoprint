FROM python:3

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run with gunicorn
CMD ["gunicorn", "-w 2", "--bind", "0.0.0.0:4500", "app:app"]
