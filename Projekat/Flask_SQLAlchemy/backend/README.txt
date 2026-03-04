To set up the backend environment, follow these steps:
    pip install -r requirements.txt

To run the backend server, use the command:
    python main.py

Docker commands
    docker build -f application.dockerfile --tag backend-app:v1 .
    docker compose -f deployment.yaml up

    docker container ls -a
    docker container rm $(docker container ls -aq)

    docker container stop $(docker container ls -aq)