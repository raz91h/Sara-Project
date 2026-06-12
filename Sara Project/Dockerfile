# Gunakan Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (jika perlu)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Railway akan inject PORT via environment variable
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Jalankan aplikasi
CMD ["python", "app.py"]
