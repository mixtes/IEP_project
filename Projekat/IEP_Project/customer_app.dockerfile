FROM python:3

COPY ./store_configuration.py /store_configuration.py
COPY ./customer_app.py /customer_app.py
COPY ./store_models.py /store_models.py
COPY ./store_requirements.txt /store_requirements.txt
COPY ./blockchain_config.py /blockchain_config.py
COPY ./decorators.py /decorators.py

RUN pip install -r /store_requirements.txt

CMD ["python", "/customer_app.py"]