from flask import Flask, jsonify, request
from store_configuration import Config

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required 

from store_models import db, Product, Category, Order, OrderItem, OrderStatus, ProductCategory

from sqlalchemy import func, case, desc
from sqlalchemy.exc import ArgumentError

from decorators import owner_required

import time
import os
import io
import csv

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

@app.route("/update", methods=["POST"])
@owner_required()
def update():
    if 'file' not in request.files:
        return jsonify({"message": "Field file is missing."}), 400
    
    uploaded_file = request.files['file']

    try:
        stream = io.TextIOWrapper(uploaded_file.stream, encoding='utf-8') # more efficient, streams file line by line

    except Exception:
        try:
            stream = io.StringIO(uploaded_file.read().decode('utf-8')) # fallback, less efficient (loads entire file into memory)

        except Exception as e:
            return jsonify({"message": f"Could not read uploaded file: {str(e)}"}), 400
        
    csv_reader = csv.reader(stream)

    parsed_rows = []
    product_names_in_file = []

    for line_idx, row in enumerate(csv_reader):
        if len(row) == 0 or (len(row) == 1 and row[0].strip() == ""):
            return jsonify({"message": f"Incorrect number of values on line {line_idx}."}), 400
        
        if len(row) != 3:
            return jsonify({"message": f"Incorrect number of values on line {line_idx}."}), 400
        
        raw_categories, raw_name, raw_price = row

        raw_categories = raw_categories.strip()
        raw_name = raw_name.strip()
        raw_price = raw_price.strip()

        if raw_categories == "":
            categories = []
        else:
            categories = [category.strip() for category in raw_categories.split("|") if category.strip() != ""]

        if raw_name == "":
            return jsonify({"message": f"Incorrect number of values on line {line_idx}."}), 400
        
        try:
            price_value = float(raw_price)
            if price_value <= 0:
                raise ValueError("Price must be a positive integer.")
            
        except Exception:
            return jsonify({"message": f"Incorrect price on line {line_idx}."}), 400
        
        parsed_rows.append((line_idx, categories, raw_name, price_value))
        product_names_in_file.append(raw_name)

    if product_names_in_file:
        existing_products = (db.session.query(Product.name).filter(Product.name.in_(product_names_in_file)).all())
        if existing_products:
            conflict_name = existing_products[0][0]  # Extract the first element of the tuple
            return jsonify({"message": f"Product {conflict_name} already exists."}), 400
        
    try:
        category_cache = {}
        for _, categories, product_name, price in parsed_rows:
            product = Product(name=product_name, price=price)
            db.session.add(product)
            db.session.flush()

            for category_name in categories:
                if category_name in category_cache:
                    category = category_cache[category_name]
                else:
                    category = db.session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).one_or_none()
                    if category is None:
                        category = Category(name=category_name)
                        db.session.add(category)
                        db.session.flush()
                    category_cache[category_name] = category
                
                product.categories.append(category)
            
        db.session.commit()
        return '', 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 400

@app.route("/product_statistics", methods=["GET"])
@owner_required()
def product_statistics():
    stats = db.session.query(
        Product.name, 
        func.sum(
            case(
                (Order.status == OrderStatus.COMPLETE, OrderItem.quantity),
                else_=0
            )
        ).label('sold'),
        func.sum(
            case(
                    (
                        Order.status.in_(
                            [OrderStatus.CREATED, OrderStatus.PENDING]
                        ), 
                        OrderItem.quantity
                    ),
                    else_=0
                )
        ).label('waiting')
    ).join(
        OrderItem, Product.id == OrderItem.product_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).group_by(
        Product.id, Product.name
    ).all()

    statistics = [
        {
            "name": stat.name,
            "sold": int(stat.sold),
            "waiting": int(stat.waiting)
        }
        for stat in stats
    ]

    return jsonify({"statistics": statistics}), 200

@app.route("/category_statistics", methods=["GET"])
@owner_required()
def category_statistics():
    whens = [(Order.status == OrderStatus.COMPLETE, OrderItem.quantity)]

    try:
        case_expr = case(*whens, else_=0)
    except ArgumentError:
        case_expr = case(whens, else_=0)

    delivered_count_expr = func.coalesce(func.sum(case_expr), 0).label('delivered_count')

    stats = db.session.query(
        Category.name,
        delivered_count_expr
    ).outerjoin(
        ProductCategory, Category.id == ProductCategory.category_id
    ).outerjoin(
        OrderItem, ProductCategory.product_id == OrderItem.product_id
    ).outerjoin(
        Order, OrderItem.order_id == Order.id
    ).group_by(
        Category.id, Category.name
    ).order_by(
        desc(delivered_count_expr),
        Category.name.asc()
    ).all()

    statistics = [stat.name for stat in stats]
    return jsonify({"statistics": statistics}), 200

if __name__ == "__main__":
    HOST = os.getenv("HOST", "localhost")
    app.run(host=HOST, port=5000, debug=True)
