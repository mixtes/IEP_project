To set up the backend environment, follow these steps:
    pip install -r requirements.txt

To run the backend server, use the command:
    python main.py

Docker commands
    docker build -f auth_app.dockerfile --tag auth_app:v1 .
    docker build -f owner_app.dockerfile --tag owner_app:v1 .
    docker build -f customer_app.dockerfile --tag customer_app:v1 .
    docker build -f courier_app.dockerfile --tag courier_app:v1 .

    docker compose -f deployment.yaml up
    docker compose -f deployment.yaml down (-v to remove volumes)

    docker container ls -a
    docker container rm $(docker container ls -aq)

    docker container stop $(docker container ls -aq)

Postman request example:
    http://127.0.0.1:5000/register_customer

Adminer:
    localhost:8080

solc compiler:
    npm install -g solc
    npm install -g solc@0.7.6
    solcjs --bin --abi OrderContract.sol

    python main.py --type all --authentication-url http://127.0.0.1:5000 --jwt-secret JWT_SECRET_DEV_KEY --roles-field roles --owner-role owner --customer-role customer --courier-role courier --with-authentication --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --courier-url http://127.0.0.1:5003 --with-blockchain --provider-url http://127.0.0.1:8545 --owner-private-key 0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60
    