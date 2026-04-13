FROM python:3.9
WORKDIR /app
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt
COPY . .
# Hugging Face Spaces require listening on port 7860
EXPOSE 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "wsgi:app"]
