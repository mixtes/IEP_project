FROM python:3

COPY ./auth_configuration.py /auth_configuration.py
COPY ./auth_app.py /auth_app.py
COPY ./auth_models.py /auth_models.py
COPY ./auth_requirements.txt /auth_requirements.txt

RUN pip install -r /auth_requirements.txt

CMD ["python", "/auth_app.py"]