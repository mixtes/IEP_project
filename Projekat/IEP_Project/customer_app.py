from flask import Flask, jsonify, request
from store_configuration import Config

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required 
from flask_jwt_extended import get_jwt_identity 

from blockchain_config import deploy_contract, is_valid_address, CONTRACT_ABI, w3, OWNER_ADDRESS, OWNER_PRIVATE_KEY

from store_models import *

from decorators import customer_required

from web3 import Web3

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

@app.route("/search")
@customer_required()
def search():
    product_name = request.args.get("name", "")
    category_name = request.args.get("category", "")

    products_query = Product.query

    if product_name:
        products_query = products_query.filter(Product.name.like(f"%{product_name}%"))

    if category_name:
        products_query = products_query.join(Product.categories).filter(Category.name.like(f"%{category_name}%"))

    products = products_query.all()

    categories_query = Category.query

    if category_name:
        categories_query = categories_query.filter(Category.name.like(f"%{category_name}%"))

    if product_name:
        categories_query = categories_query.join(Category.products).filter(Product.name.like(f"%{product_name}%"))

    categories = categories_query.distinct().all()

    response = {
        "categories": [category.name for category in categories],
        "products": [
            {
                "categories": [category.name for category in product.categories],
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]
    }

    return jsonify(response), 200

@app.route("/order", methods=["POST"])
@customer_required()
def order():
    try:
        data = request.get_json()
        customer_email = get_jwt_identity()

        # Validation
        if 'requests' not in data:
            return jsonify({"message": "Field requests is missing."}), 400

        requests_list = data['requests']

        for index, req in enumerate(requests_list):
            if 'id' not in req:
                return jsonify({"message": f"Product id is missing for request number {index}."}), 400
            
            if 'quantity' not in req:
                return jsonify({"message": f"Product quantity is missing for request number {index}."}), 400
            
            product_id = req['id']
            quantity = req['quantity']

            if not isinstance(product_id, int) or product_id <= 0:
                return jsonify({"message": f"Invalid product id for request number {index}."}), 400
            
            if not isinstance(quantity, int) or quantity <= 0:
                return jsonify({"message": f"Invalid product quantity for request number {index}."}), 400
            
            product = Product.query.filter_by(id=product_id).first()
            if not product:
                return jsonify({"message": f"Invalid product for request number {index}."}), 400
            
        if 'address' not in data or not data['address']:
            return jsonify({"message": "Field address is missing."}), 400
        
        customer_address = data['address']

        if not is_valid_address(customer_address):
            return jsonify({"message": "Invalid address."}), 400
            
        # Calculate total price and prepare order items
        total_price = 0
        order_items = []

        for req in requests_list:
            product = Product.query.filter_by(id=req['id']).first()
            quantity = req['quantity']
            item_price = product.price * quantity
            total_price += item_price

            order_items.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': product.price
            })

        # Convert price to wei
        price_in_wei = int(total_price * 100)
        
        print(f"DEBUG: Deploying contract...")
        print(f"  Customer address: {customer_address}")
        print(f"  Total price: {total_price}")
        print(f"  Price in wei: {price_in_wei}")

        # Deploy contract
        contract_address = deploy_contract(customer_address, price_in_wei)
        
        print(f"  Contract deployed at: {contract_address}")

        # Create order
        new_order = Order(
            customer_email=customer_email,
            customer_address=customer_address,
            total_price=total_price, 
            contract_address=contract_address,
            status=OrderStatus.CREATED
        )
        db.session.add(new_order)
        db.session.flush()

        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)

        db.session.commit()

        print(f"  Order created with ID: {new_order.id}")

        return jsonify({"id": new_order.id}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"ERROR in /order endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Failed to create order and deploy contract."}), 400

@app.route("/status", methods=["GET"])
@customer_required()
def status():
    current_user_email = get_jwt_identity()

    orders = Order.query.filter_by(customer_email=current_user_email).all()

    orders_list = []
    for order in orders:
        if order.status == OrderStatus.CREATED:
            status_str = "CREATED"
        elif order.status == OrderStatus.PENDING:
            status_str = "PENDING"
        elif order.status == OrderStatus.COMPLETE:
            status_str = "COMPLETE"
        else:
            status_str = "CREATED" # default fallback, should not happen

        products_list = []
        for item in order.items:
            product = item.product

            categories = [category.name for category in product.categories]

            products_list.append({
                "categories": categories,
                "name": product.name,
                "price": item.price,
                "quantity": item.quantity
            })
        
        orders_list.append({
            "products": products_list,
            "price": order.total_price,
            "status": status_str,
            "timestamp": order.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") # ISO 8601 format
        })

    return jsonify({"orders": orders_list}), 200

@app.route("/delivered", methods=["POST"])
@customer_required()
def delivered():
    data = request.get_json()

    customer_email = get_jwt_identity()

    if 'id' not in data:
        return jsonify({"message": "Missing order id."}), 400
    
    order_id = data['id']

    try:
        order_id = int(order_id)
        if order_id <= 0:
            return jsonify({"message": "Invalid order id."}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid order id."}), 400
    
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Invalid order id."}), 400
    
    if order.customer_email != customer_email:
        return jsonify({"message": "Invalid order id."}), 400
    
    try:
        contract_address = Web3.to_checksum_address(order.contract_address)
        contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

        # Check courier assigned
        courier_address = contract.functions.getCourier().call()
        if courier_address == '0x0000000000000000000000000000000000000000':
            return jsonify({"message": "Delivery not complete."}), 400
        
        # Check payment made
        is_paid = contract.functions.isPaid().call()
        if not is_paid:
            return jsonify({"message": "Delivery not complete."}), 400
        
        # Check already confirmed
        is_confirmed = contract.functions.isDeliveryConfirmed().call()
        if is_confirmed:
            return jsonify({"message": "Invalid order id."}), 400
        
        # Check order status
        if order.status != OrderStatus.PENDING:
            return jsonify({"message": "Invalid order id."}), 400
        
        # Get gas price with fallback
        gas_price = w3.eth.gas_price
        if gas_price is None or gas_price == 0:
            gas_price = 1
        
        owner_address_checksum = Web3.to_checksum_address(OWNER_ADDRESS)
        
        transaction = contract.functions.confirmDeliveryByOwner().build_transaction({
            'from': owner_address_checksum,
            'nonce': w3.eth.get_transaction_count(owner_address_checksum),
            'gas': 300000,
            'gasPrice': gas_price
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, OWNER_PRIVATE_KEY)

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # FIXED: raw_transaction

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status != 1:
            return jsonify({"message": "Blockchain transaction failed."}), 500

        order.status = OrderStatus.COMPLETE
        db.session.commit()

        return '', 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error confirming delivery: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Failed to confirm delivery on blockchain."}), 500
    
@app.route("/generate_invoice", methods=["POST"])
@customer_required()
def generate_invoice():
    data = request.get_json()

    customer_email = get_jwt_identity()

    if 'id' not in data:
        return jsonify({"message": "Missing order id."}), 400
    
    order_id = data['id']

    try:
        order_id = int(order_id)
        if order_id <= 0:
            return jsonify({"message": "Invalid order id."}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid order id."}), 400
    
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Invalid order id."}), 400
    
    if order.customer_email != customer_email:
        return jsonify({"message": "Invalid order id."}), 400
    
    if 'address' not in data:
        return jsonify({"message": "Missing address."}), 400
    
    customer_address = data['address']

    if not is_valid_address(customer_address):
        return jsonify({"message": "Invalid address."}), 400
    
    if customer_address.lower() != order.customer_address.lower():
        return jsonify({"message": "Invalid address."}), 400
    
    try:
        contract_address = Web3.to_checksum_address(order.contract_address)
        contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

        is_paid = contract.functions.isPaid().call()
        if is_paid:
            return jsonify({"message": "Transfer already complete."}), 400
        
        price_in_wei = contract.functions.price().call()

        customer_address_checksum = Web3.to_checksum_address(customer_address)

        nonce = w3.eth.get_transaction_count(customer_address_checksum)

        transaction = contract.functions.pay().build_transaction({
            'from': customer_address_checksum,
            'value': price_in_wei,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })

        return jsonify({"invoice": transaction}), 200
    
    except Exception as e:
        print(f"Error generating invoice: {e}")
        return jsonify({"message": "Failed to generate invoice."}), 500

if __name__ == "__main__":
    HOST = os.getenv("HOST", "localhost")
    app.run(host=HOST, port=5000, debug=True)
