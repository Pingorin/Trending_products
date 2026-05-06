FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Playwright browsers aur dependencies install karna
RUN playwright install chromium
RUN playwright install-deps

COPY . .

EXPOSE 7860

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "7860"]
