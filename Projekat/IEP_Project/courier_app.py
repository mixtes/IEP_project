from flask import Flask, jsonify, request
from store_configuration import Config

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required 
from flask_jwt_extended import get_jwt_identity 

from blockchain_config import w3, CONTRACT_ABI, OWNER_PRIVATE_KEY, OWNER_ADDRESS, is_valid_address
from web3 import Web3

from store_models import *

from decorators import courier_required

import time
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

jwt = JWTManager(app)

retry_count = 0
database_created = False
while not database_created:
    try:
        with app.app_context():
            db.create_all()

            database_created = True
    except Exception as e:
        retry_count += 1
        print(f"Database connection failed. Retrying {retry_count}/5...")
        time.sleep(5)
        if retry_count >= 5:
            print("Max retries reached. Exiting.")
            exit(0) 

@app.route("/orders_to_deliver", methods=["GET"])
@courier_required()
def orders_to_deliver():
    orders = Order.query.filter(Order.status == OrderStatus.CREATED).all()

    orders_list = [
        {
            "id": order.id,
            "email": order.customer_email
        }
        for order in orders
    ]

    return jsonify({"orders": orders_list}), 200

@app.route("/pick_up_order", methods=["POST"])
@courier_required()
def pick_up_order():
    data = request.get_json()

    courier_email = get_jwt_identity()

    if 'id' not in data:
        return jsonify({"message": "Missing order id."}), 400
    
    order_id = data['id']

    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify({"message": "Invalid order id."}), 400
    
    order = Order.query.filter(Order.id == order_id).first()

    if not order or order.status != OrderStatus.CREATED:
        return jsonify({"message": "Invalid order id."}), 400
    
    if 'address' not in data or not data['address']:
        return jsonify({"message": "Missing address."}), 400
    
    courier_address = data['address']

    if not is_valid_address(courier_address):
        return jsonify({"message": "Invalid address."}), 400
    
    try:
        contract_address = Web3.to_checksum_address(order.contract_address)
        contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

        is_paid = contract.functions.isPaid().call()
        if not is_paid:
            return jsonify({"message": "Transfer not complete."}), 400
        
        current_courier = contract.functions.courier().call()
        if current_courier != '0x0000000000000000000000000000000000000000':
            return jsonify({"message": "Invalid order id."}), 400
        
        courier_address_checksum = Web3.to_checksum_address(courier_address)
        owner_address_checksum = Web3.to_checksum_address(OWNER_ADDRESS)

        # Get gas price with fallback
        gas_price = w3.eth.gas_price
        if gas_price is None or gas_price == 0:
            gas_price = 1

        transaction = contract.functions.assignCourier(courier_address_checksum).build_transaction({
            'from': owner_address_checksum,
            'nonce': w3.eth.get_transaction_count(owner_address_checksum),
            'gas': 200000,
            'gasPrice': gas_price
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, OWNER_PRIVATE_KEY)

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status != 1:
            return jsonify({"message": "Blockchain transaction failed."}), 500

        order.status = OrderStatus.PENDING
        order.courier_address = courier_address
        db.session.commit()

        return "", 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error assigning courier: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Failed to assign courier on blockchain."}), 500

if __name__ == "__main__":
    HOST = os.getenv("HOST", "localhost")
    app.run(host=HOST, port=5000, debug=True)
