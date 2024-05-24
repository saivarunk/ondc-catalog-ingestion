FROM python:3.9-slim-buster as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

FROM python:3.9-slim-buster as runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy Python dependencies from the builder stage
COPY --from=builder /root/.local /root/.local

# Add the local bin folder to PATH
ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN python app/load_model.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--timeout-keep-alive", "600"]