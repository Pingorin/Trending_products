FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Hugging Face ke health check ke liye port expose karna zaroori hai
EXPOSE 7860

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "7860"]
