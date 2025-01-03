FROM python:3.12
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pip-audit && pip-audit -r requirements.txt
COPY . .
CMD python app.py