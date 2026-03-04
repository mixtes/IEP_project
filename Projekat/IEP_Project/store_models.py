from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(256), unique=True, nullable=False)
    price       = db.Column(db.Float, nullable=False)

    categories = db.relationship('Category', secondary='product_categories', back_populates='products')

    def __repr__(self):
        return f"<Procuct id={self.id} name={self.name} price={self.price}>"

class Category(db.Model):
    __tablename__ = 'categories'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(256), unique=True, nullable=False)

    products    = db.relationship('Product', secondary='product_categories', back_populates='categories')

    def __repr__(self):
        return f"<Category id={self.id} name={self.name}>"
    
class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id          = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<ProductCategory id={self.id} product_id={self.product_id} category_id={self.category_id}>"
    
class OrderStatus(enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    COMPLETE = "complete"

class Order(db.Model):
    __tablename__ = 'orders'
    id          = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(256), nullable=False)
    customer_address = db.Column(db.String(256), nullable=False) # blockchain support
    courier_address = db.Column(db.String(256), nullable=True) # blockchain support
    total_price = db.Column(db.Float, nullable=False)
    contract_address = db.Column(db.String(256), nullable=True) # blockchain support
    status      = db.Column(db.Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    items       = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id          = db.Column(db.Integer, primary_key=True)
    order_id    = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity    = db.Column(db.Integer, nullable=False, default=1)
    price       = db.Column(db.Float, nullable=False) # price at the time of order

    order       = db.relationship('Order', back_populates='items')
    product     = db.relationship('Product')