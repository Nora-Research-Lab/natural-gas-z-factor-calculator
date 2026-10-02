FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY natural_gas_z_factor_calculator.py app.py ./

EXPOSE 7860

CMD ["python", "app.py"]
