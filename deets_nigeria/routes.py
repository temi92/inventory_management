from flask import render_template, flash, redirect,url_for, request,jsonify
from deets_nigeria.forms import WarehouseForm, CustomerForm, UpdateProductForm
from deets_nigeria import app,db
from deets_nigeria.models import Product, Customer, ProductInfo, Order, OrderItem
import json
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import string

@app.route('/')
def index():
    return render_template("dashboard.html")

@app.route('/warehouse')
def ware_house():
    return render_template("ware_house.html")

@app.route('/customer')
def customer():
    return render_template("customer.html")


@app.route("/order")
def order():
    return render_template("order.html")

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
        #TODO MAKE SURE date was input
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

@app.route("/manage_order", methods=["GET", "POST"])
def manage_order():
    return "manage order"

@app.route("/register_product", methods=["GET", "POST"])
def register_product():
    form = WarehouseForm()
    if form.validate_on_submit():
        #TODO check if product already registered and raise exception!!!..
        product = Product(form.name_of_product.data, form.price.data)
        product.save_to_db()
        flash("sucessfully added {}".format(form.name_of_product.data), "success")
        return redirect(url_for("ware_house"))
    return render_template("register_product.html", form=form)

@app.route("/register_customer", methods=["GET", "POST"])
def register_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        #store customer in DB..
        customer = Customer(form.name.data, form.address.data, form.phone_number.data)
        customer.save_to_db()
        flash("sucessfully added Customer - {}".format(form.name.data), "success")
        return redirect(url_for("customer"))
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
    return render_template("manage_product_1.html")



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

        flash("sucessfully added {} bags to {} product ".format(quantity, product_name), "success")
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



@app.route("/view order", methods=["GET"])
def view_order():
    #get customers who have placed orders..
    orders = Order.query.all()
    customers = set([order.customer_id for order in orders])

    customer_names = [Customer.query.filter_by(id=customer).first().name for customer in customers]
    paid_status = [Customer.query.filter_by(id=customer).first().paid_status for customer in customers]
    totalAmount = [Customer.query.filter_by(id=customer).first().total_amount for customer in customers]
    data = list(zip(customer_names, paid_status, totalAmount))

    print (customer_names, paid_status, totalAmount)
    print (data)




    return render_template("view_order.html", data = data)




@app.route("/view_customer", methods=["GET", "POST"])
def manage_customer():
    #get all customers..
    customers = Customer.query.all()
    return render_template("view_customer.html", customers=customers)





