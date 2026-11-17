FROM python:3.12-slim

WORKDIR /repo
COPY unidad_2 unidad_2
COPY unidad_6 unidad_6
COPY unidad_7 unidad_7
RUN pip install --no-cache-dir -r unidad_7/pre_entrega/requirements.txt

ENV REDIS_URL=redis://redis:6379
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "unidad_7.pre_entrega.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
