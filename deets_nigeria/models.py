from deets_nigeria import db
from datetime import datetime


class Base(object):
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Product(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer)
    product_info = db.relationship("ProductInfo", backref="product", lazy="select", cascade="all, delete-orphan")
    order_info = db.relationship("OrderItem", backref="product", lazy="select", cascade="all, delete-orphan")



    def __init__(self, product_name, price):
        self.product_name = product_name
        self.price = price
        self.quantity = 0  #total quantity of bags produced..

    def __repr__(self):
        return str(self.id)
        # return "Product name is {} quantity is {} price is {} ".format(self.product_name, self.quantity, self.price)



class ProductInfo(Base, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    def __init__(self, quantity,date):
        self.quantity = quantity
        self.date = date

    def __repr__(self):
        return str(self.id)



class Customer(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(200))
    orders = db.relationship("Orders", backref="customer", lazy="select", cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="customer", lazy="select",cascade="all, delete-orphan" )


    def __init__(self, name, address, phone_number,total_amount=0):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.total_amount = total_amount

    def __repr__(self):
        return str(self.id)
        # return "Customer name is {} and address is {}".format(self.name, self.address)

class OrderItem(Base, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.String(200), db.ForeignKey("orders.order_id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)



    def __init__(self, quantity,rate, amount):
        self.quantity = quantity
        self.rate = rate
        self.amount = amount

class Orders(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    order_id = db.Column(db.String(200), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    paid_status = db.Column(db.Boolean, default=False, nullable=False)
    total_amount = db.Column(db.Float)
    orders = db.relationship("OrderItem", backref="order", lazy="select", cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="order", lazy="select", cascade="all, delete-orphan")

    def __init__(self, date, order_id,total_amount=0):
        self.date = date
        self.order_id = order_id
        self.total_amount = total_amount


class Payment(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    bank_name = db.Column(db.String(200), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    order_id = db.Column(db.String, db.ForeignKey("orders.order_id"))
    amount_paid = db.Column(db.Float, nullable=False)

    def __init__(self, date, bank_name, amount_paid):
        self.date = date
        self.bank_name = bank_name
        self.amount_paid = amount_paid

















