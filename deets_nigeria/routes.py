from flask import render_template, flash, redirect,url_for, request,jsonify
from deets_nigeria.forms import WarehouseForm, CustomerForm, UpdateProductForm, LoginForm
from deets_nigeria import app,db
from deets_nigeria.models import Product, Customer, ProductInfo, Order, OrderItem
import json
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import string


#items = None

#load json file that contains credentials..
with open('deets_nigeria/credentials.json') as f:
    data = json.load(f)

@app.route('/dashboard')
def index():
    return render_template("dashboard.html")

@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == data["user_name"] and form.password.data == data["password"]:
            return redirect(url_for("index"))

        else:
            flash("Wrong username and Password", "danger")
    return render_template("login.html",form=form)



@app.route("/add_order", methods=["GET", "POST"])
def add_order():
    product = Product.query.all()
    #get customers
    customers = Customer.query.all()

    product_names = list([p.product_name for p in product])
    product_names_json = json.dumps(product_names)#this allows us to get list of products to user..
    customer = None

    if request.method == "POST":
        date = request.form["date"]

        # convert to date object.
        date = datetime.strptime(date, '%m/%d/%Y')

        #grab form data.
        customer_name = request.form["customerName"]
        payment_status = request.form["payment_status"]
        counters = int(request.form["counters"])
        names = [request.form["choice" + str(i)] for i in range(counters)]
        quantity = [request.form["quantity" + str(i)] for i in range(counters)]
        rate = [request.form["rate" + str(i)] for i in range(counters)]
        amount = [request.form["amount" + str(i)] for i in range(counters)]
        total_amount = request.form["totalAmount"]
        order_details = list(zip(names, quantity, rate, amount))

        #get customer and product from db..
        customer = Customer.query.filter_by(name=customer_name).first()

        # generate unqiue order code ..
        order_id = ''.join(random.choice(string.digits) for _ in range(5))
        # create a new order...
        ord = Order(date, order_id, payment_status, total_amount)



        for i in range(len(order_details)):
            product = Product.query.filter_by(product_name=order_details[i][0]).first()
            #check if product quantity is sufficient...
            if int(order_details[i][1]) <= product.quantity: #TODO ..FIX THIS BUG..
                product.quantity -= int(order_details[i][1])
                product.save_to_db()


                o = OrderItem(order_details[i][1], order_details[i][2], order_details[i][3])
                o.order = ord
                o.product = product
                o.save_to_db()
            else:
                return jsonify({"success": 0})

        #save order info to database..
        ord.customer = customer
        ord.save_to_db()



        return jsonify({"success":1})
    return render_template("add_order.html", product_names=product_names, product_names_json=product_names_json, customers=customers)

#what is input??.i.e.ee

@app.route("/get_rate", methods=["POST"])
def get_quantity():
    product_name = request.form["product_name"]
    price = Product.query.filter_by(product_name=product_name).first().price
    return jsonify({"price": price})



@app.route("/register_product", methods=["GET", "POST"])
def register_product():
    form = WarehouseForm()
    if form.validate_on_submit():
        #TODO check if product already registered and raise exception!!!..
        product = Product(form.name_of_product.data, form.price.data)
        product.save_to_db()
        flash("sucessfully added {}".format(form.name_of_product.data), "success")
        return redirect(url_for("register_product"))
    return render_template("register_product.html", form=form)

@app.route("/register_customer", methods=["GET", "POST"])
def register_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        #store customer in DB..
        customer = Customer(form.name.data, form.address.data, form.phone_number.data)
        customer.save_to_db()
        flash("sucessfully added Customer - {}".format(form.name.data), "success")
        return redirect(url_for("register_customer"))
    return render_template("register_customer.html", form=form)



#TODO FIX ME... use set data structure
@app.route("/view_product", methods=["POST", "GET"])
def view_product():
    #query for all the products registered.

    get_quantity = lambda x: ProductInfo.query.filter_by(id=x).first().quantity
    get_id = lambda x: x.id


    if request.method == "POST":

        date = request.form["date"] #this is a str
        #convert to date object.
        date = datetime.strptime(date, '%m/%d/%Y')

        #get list of product and remove possible NULL values..
        products = ProductInfo.query.filter(ProductInfo.date == date).filter(ProductInfo.product_id != None).all()
        #create set data structure to hold product id
        s = set(p.product_id for p in products)

        #FIX ME....
        data = {Product.query.filter_by(id=p).first().product_name: ProductInfo.query.filter(ProductInfo.date==date)\
            .filter(ProductInfo.product_id ==p).all()
                for p in s}
        #add all the quantity bags..
        for k, v in data.items():
            #get product id..
            v = map(get_id, v)
            data[k] = sum(list(map(get_quantity, v)))
        return jsonify(data)
    return render_template("view_product.html")



@app.route("/update_product", methods=["GET", "POST"])
def update_product():
    #get list of all products ..
    #TODO update database to accomodate datefield.....
    form = UpdateProductForm() #get date and quantity from user.
    products = Product.query.all() #get all products registered.

    product_names = list([p.product_name for p in products])
    if form.validate_on_submit():
        product_name = request.form["selected_product"]
        quantity = form.product_quantity.data
        date = form.date.data

        product = Product.query.filter_by(product_name=product_name).first()
        #check if cell is NULL
        if product.quantity is None:
            product.quantity = 0

        #update quantity..
        product.quantity+=quantity

        #add product info (qunatity, date) for particular product..
        product.product_info.append(ProductInfo(quantity,date))
        product.save_to_db()

        flash("{} : successfully added {} bags to warehouse ".format(product_name, quantity), "success")
        return redirect(url_for('update_product'))

    return render_template("update_product.html", products=product_names, form=form)

@app.route("/delete_product", methods=["GET", "POST"])
def delete_product():
    products = Product.query.all()
    product_names = list([p.product_name for p in products])
    if request.method == "POST":
        product_name = request.form["selected_product"]
        #delete product..
        products = Product.query.filter(Product.product_name == product_name).all()
        for p in products:
            p.delete_from_db()
        flash("sucessfully deleted product",  "success")


        #get list of product names..
        products = Product.query.all()
        product_names = list([p.product_name for p in products])
        return redirect(url_for("delete_product", products=product_names))
    return render_template("delete_product.html", products=product_names)



@app.route("/product_quantity", methods=["GET"])
def product_quantity():
    products = Product.query.all()
    return render_template("product_quantity.html", products=products)



@app.route("/view_order", methods=["GET"])
def view_order():
    #get customers who have placed orders..
    orders = Order.query.all()


    customers = set([order.customer_id for order in orders])
    customer_names = [Customer.query.filter_by(id=order.customer_id).first().name for order in orders]


    date = [order.date.date() for order in orders]
    order_no = [order.order_id for order in orders]
    paid_status = [order.paid_status for order in orders]
    totalAmount = [order.total_amount for order in orders]

    data = list(zip(customer_names, date, order_no, paid_status, totalAmount))

    return render_template("view_order.html", data=data)

#TODO FIX THIS..
@app.route("/get_order_item", methods=["POST"])
def get_order_item():
    #global items
    items = None
    if request.method == "POST":
        order_id = request.json["order_id"]
        items = OrderItem.query.filter_by(order_id=order_id).all()

        product_names = [Product.query.filter_by(id=item.product_id).first().product_name for item in items]
        quantity = [item.quantity for item in items]
        rate = [item.rate for item in items]
        amount = [item.amount for item in items]
        items = list(zip(product_names, quantity, rate, amount))

        return jsonify({"items":items})



@app.route("/order_details", defaults={"items":""})
@app.route("/order_details/<items>", methods=["GET"])
def order_details(items):
    items = items.split(",")
    items = [items[i:i+4] for i in range(0, len(items), 4)]
    return render_template("order_details.html", items=items)


@app.route("/edit_payment_status", methods=["POST", "GET"])
def edit_paymentStatus():
    if request.method == "POST":
        payment_status = request.form["payment_status"]
        order_code = request.form["order_code"]

        #remove preeciding spaces
        order_code = order_code.strip()

        #change paid status
        order = Order.query.filter_by(order_id=order_code).first()
        order.paid_status = payment_status
        order.save_to_db()
    return redirect(url_for("view_order"))



@app.route("/print_order", methods=["POST"])
def print_order():
    if request.method == "POST":
        customer_name = request.json["customer_name"].strip()
        date = request.json["date"].strip()
        order_id = request.json["order_id"].strip()

        #get address and phone_no
        address = Customer.query.filter_by(name=customer_name).first().address
        phone_no = Customer.query.filter_by(name=customer_name).first().phone_number
        items = OrderItem.query.filter_by(order_id=order_id).all()

        product_names = [Product.query.filter_by(id=item.product_id).first().product_name for item in items]
        quantity = [item.quantity for item in items]


        item_details = list(zip(product_names, quantity))
        return jsonify({"items":item_details,"address":address, "phone_no":phone_no })

        #print(customer_name, date, order_id, address)

    return ""

@app.route("/view_customer", methods=["GET", "POST"])
def manage_customer():
    #get all customers..
    customers = Customer.query.all()
    return render_template("view_customer.html", customers=customers)





