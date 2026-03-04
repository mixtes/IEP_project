FROM python:3

COPY ./store_configuration.py /store_configuration.py
COPY ./owner_app.py /owner_app.py
COPY ./store_models.py /store_models.py
COPY ./store_requirements.txt /store_requirements.txt
COPY ./decorators.py /decorators.py

RUN pip install -r /store_requirements.txt

CMD ["python", "/owner_app.py"]