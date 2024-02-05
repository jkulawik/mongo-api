FROM python:3.10-slim

WORKDIR /mongo_app

COPY ./requirements.txt /mongo_app/
COPY ./connect_info.txt /mongo_app/

COPY ./api/main.py /mongo_app/api/
COPY ./api/__init__.py /mongo_app/api/

COPY ./api/data/models.py /mongo_app/api/data/
COPY ./api/data/validation.py /mongo_app/api/data/

RUN pip install --no-cache-dir --upgrade -r /mongo_app/requirements.txt

RUN pip install uvicorn

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
