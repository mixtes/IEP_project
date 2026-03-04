docker compose -f deployment.yaml down -v
docker build -f auth_app.dockerfile --tag auth_app:v1 .
docker build -f owner_app.dockerfile --tag owner_app:v1 .
docker build -f customer_app.dockerfile --tag customer_app:v1 .
docker build -f courier_app.dockerfile --tag courier_app:v1 .
docker compose -f deployment.yaml up