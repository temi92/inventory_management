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
    product_info = db.relationship("ProductInfo", backref="product", lazy="select")
    order_info = db.relationship("Order", backref="product", lazy="select")

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
    order = db.relationship("Order", backref="customer", lazy="select")


    def __init__(self, name, address, phone_number):
        self.name = name
        self.address = address
        self.phone_number = phone_number

    def __repr__(self):
        return str(self.id)
        # return "Customer name is {} and address is {}".format(self.name, self.address)


class Order(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    def __init__(self, date):
        self.date = date




