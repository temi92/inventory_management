from flask import render_template, flash, redirect,url_for, request,jsonify, session, g
from deets_nigeria.forms import WarehouseForm, CustomerForm, UpdateProductForm, LoginForm
from deets_nigeria import app,db
from deets_nigeria.models import Product, Customer, ProductInfo, Orders, OrderItem, Payment
from deets_nigeria.utils import getOrderData, customerNamesforOrders, daterange
import json
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import string


#items = None

#load json file that contains credentials..
with open('deets_nigeria/credentials.json') as f:
    data = json.load(f)


@app.before_request
def before_request():
    g.user = None
    g.login_form = LoginForm()

    if "user" in session:
        g.user = session["user"]


@app.route('/dashboard')
def index():
    if g.user:
        return render_template("dashboard.html")
    return redirect(url_for("login"))

@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def login():
    #form = LoginForm()
    form = g.login_form


    if request.method == "POST":
        session.pop("user", None)

        if form.validate_on_submit():
            if form.username.data == data["user_name"] and form.password.data == data["password"]:
                session["user"] = data["user_name"]
                return redirect(url_for("index"))

            else:
                flash("Wrong username and Password", "danger")
    return render_template("login.html",form=form)



@app.route("/add_order", methods=["GET", "POST"])
def add_order():
    if g.user:
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
            #payment_status = request.form["payment_status"]
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
            #ord = Orders(date, order_id, payment_status, total_amount)
            ord = Orders(date, order_id, total_amount)


            #update stock in warehouse...

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
    return render_template("login.html",form=g.login_form)


#what is input??.i.e.ee

@app.route("/get_rate", methods=["POST"])
def get_quantity():
    product_name = request.form["product_name"]
    price = Product.query.filter_by(product_name=product_name).first().price
    return jsonify({"price": price})



@app.route("/register_product", methods=["GET", "POST"])
def register_product():
    if g.user:
        form = WarehouseForm()
        if form.validate_on_submit():
            #TODO check if product already registered and raise exception!!!..
            product = Product(form.name_of_product.data, form.price.data)
            product.save_to_db()
            flash("sucessfully added {}".format(form.name_of_product.data), "success")
            return redirect(url_for("register_product"))
        return render_template("register_product.html", form=form)
    return render_template("login.html",form=g.login_form)

@app.route("/register_customer", methods=["GET", "POST"])
def register_customer():
    if g.user:
        form = CustomerForm()
        if form.validate_on_submit():
            #store customer in DB..
            customer = Customer(form.name.data, form.address.data, form.phone_number.data)
            customer.save_to_db()
            flash("sucessfully added Customer - {}".format(form.name.data), "success")
            return redirect(url_for("register_customer"))
        return render_template("register_customer.html", form=form)
    return render_template("login.html",form=g.login_form)


@app.route("/grab_customer_info", methods=["GET", "POST"])
def grab_customer_info():
    if g.user:

        customers = Customer.query.all()
        if request.method == "POST":
            customer_name = request.form["customer_name"]
            customer_info = Customer.query.filter_by(name=customer_name).first()
            address = customer_info.address
            phone_number = customer_info.phone_number
            return jsonify({"address":address, "phone_number":phone_number})
        return render_template("edit_customer.html",customers=customers )

    return render_template("login.html",form=g.login_form)

@app.route("/edit_customer", methods=["POST"])
def edit_customer():
    #grab customer ...
    customer_name = request.form["customerName"]
    customer = Customer.query.filter_by(name=customer_name).first()
    customer.address = request.form["address"]
    customer.phone_number = request.form["phone_no"]
    customer.save_to_db()
    flash ("Succcesfully updated {} details".format(customer_name), "success")
    return redirect(url_for("grab_customer_info"))



#TODO FIX ME... use set data structure
@app.route("/view_product", methods=["POST", "GET"])
def view_product():
    #query for all the products registered.
    if g.user:

        get_quantity = lambda x: ProductInfo.query.filter_by(id=x).first().quantity
        get_id = lambda x: x.id

        products = Product.query.all()  # get all products registered.

        product_names = list([p.product_name for p in products])


        if request.method == "POST":

            #grab form data...
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            #convert to date time object
            start_date = datetime.strptime(start_date, '%m/%d/%Y')
            end_date = datetime.strptime(end_date, '%m/%d/%Y')


            date_range = {}
            for dt in daterange(start_date, end_date):
                date_range.update({dt.strftime('%Y-%m-%d'):0})


            product_name = request.form["selected_product"]

            id = Product.query.filter_by(product_name=product_name).first().id
            #get all product_info data...
            p = ProductInfo.query.filter_by(product_id=id).all()



            #consider not using nested for loop this could be quite slow with large data..
            for i in p:
                for key, value in date_range.items():
                    #check date
                    if i.date.date().strftime('%Y-%m-%d') == key:
                        date_range[key] = i.quantity

            print (date_range)

            return render_template("productbar_chart.html", date_range=date_range)





            '''
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
            '''
        return render_template("view_product.html",products=product_names)
    return render_template("login.html",form=g.login_form)




@app.route("/update_product", methods=["GET", "POST"])
def update_product():
    if g.user:
        #get list of all products ..
        #TODO update database to accomodate datefield.....
        form = UpdateProductForm() #get date and quantity from user.
        products = Product.query.all() #get all products registered.

        product_names = list([p.product_name for p in products])
        if request.method == "POST":
            product_name = request.form["selected_product"]


            quantity = int(request.form["quantity"])
            date = request.form["date"]
            # convert to date object.
            date = datetime.strptime(date, '%m/%d/%Y')

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

        return render_template("update_product.html", products=product_names)
    return render_template("login.html",form=g.login_form)


@app.route("/delete_product", methods=["GET", "POST"])
def delete_product():
    if g.user:
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

    return render_template("login.html",form=g.login_form)



@app.route("/product_quantity", methods=["GET"])
def product_quantity():
    if g.user:
        products = Product.query.all()
        return render_template("product_quantity.html", products=products)
    return render_template("login.html",form=g.login_form)




@app.route("/view_order", methods=["GET"])
def view_order():
    if g.user:
        #get customers who have placed orders..
        orders = Orders.query.all()


        #customers = set([order.customer_id for order in orders])
        customer_names = [Customer.query.filter_by(id=order.customer_id).first().name for order in orders]


        date = [order.date.date() for order in orders]
        order_no = [order.order_id for order in orders]
        #paid_status = [order.paid_status for order in orders]
        paid_status = ["Paid" if order.paid_status == True else "Not paid" for order in orders ]
        totalAmount = [order.total_amount for order in orders]

        data = list(zip(customer_names, date,order_no, paid_status, totalAmount))

        return render_template("view_order.html", data=data)
    return render_template("login.html",form=g.login_form)


#TODO FIX THIS..
@app.route("/get_order_item", methods=["POST"])
def get_order_item():
    #global items
    items = None
    if request.method == "POST":
        order_id = request.json["order_id"]
        items = OrderItem.query.filter_by(order_id=order_id.strip()).all()
        #check if items is list is empty
        if not items:
            return jsonify({"items": ""})

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
    print (items)
    return render_template("order_details.html", items=items)



@app.route("/get_order_numbers", methods=["POST"])
def get_order_numbers():
    # get customers who have placed orders..
    name = request.form["customer_name"]
    #grab orders customer has placed..
    order_ids, total_amount = getOrderData(name, filter=False)
    return jsonify({"order_ids":order_ids, "total_amount":total_amount})


@app.route("/add_payment", methods=["POST", "GET"])
def add_payment():
    if g.user:
        #get customer names who have placed order.
        customer_names = customerNamesforOrders(filter=True)
        if request.method == "POST":
            customer_name = request.form["customerName"]

            order_no = request.form["no_order"]
            bank_name = request.form["bank_name"]
            date = request.form["date"]
            amount_paid = request.form["amount_paid"]

            total_amount = request.form["total_amount"]

            # convert to date object.
            date = datetime.strptime(date, '%m/%d/%Y')
            order = Orders.query.filter_by(order_id=order_no).first()

            #get from Payment data base info.
            payment = Payment.query.filter_by(order_id=order_no).all()
            if payment:
                amount_paidsoFar = sum([p.amount_paid for p in payment])
                if (float(amount_paid)+ float(amount_paidsoFar)) > float(total_amount):
                    flash(" Try Again! Amount paid is greater than amount customer owes", "danger")
                    return redirect(url_for("add_payment"))
                elif (float(amount_paid)+ float(amount_paidsoFar)) == float(total_amount):
                    order.paid_status = True
                    order.save_to_db()
                else:
                    pass
            else:
                #check if amount paid is greater than total_amount
                if (float(amount_paid) > float(total_amount)):
                    flash(" Try Again! Amount paid is greater than amount customer owes", "danger")
                    return redirect(url_for("add_payment"))
                elif (float(amount_paid) == float(total_amount)):
                    order.paid_status = True
                    order.save_to_db()
                else:
                    pass



            payment = Payment(date, bank_name, amount_paid)
            #retrieve customer..
            customer = Customer.query.filter_by(name=customer_name).first()
            #retrieve order..
            payment.customer = customer
            payment.order = order
            payment.save_to_db()

            flash("Successfully added payment", "success")

        return render_template("add_payment.html", customers=customer_names)
    return render_template("login.html",form=g.login_form)




@app.route("/edit_payment_status", methods=["POST", "GET"])
def edit_paymentStatus():
    if g.user:
        if request.method == "POST":
            payment_status = request.form["payment_status"]
            order_code = request.form["order_code"]

            #remove preeciding spaces
            order_code = order_code.strip()

            #change paid status
            order = Orders.query.filter_by(order_id=order_code).first()
            order.paid_status = payment_status
            order.save_to_db()
        return redirect(url_for("view_order"))
    return render_template("login.html",form=g.login_form)



@app.route("/pending_payments", methods=["POST", "GET"])
def pending_payments():
    if g.user:
        #GRAB customers who have placed order but not finished paying.
        customer_names = customerNamesforOrders(filter=True)
        if request.method == "POST":
            name = request.form["customer_name"]
            # grab orders that customer has not paid complete..
            order_no, total_amount = getOrderData(name, filter=True)
            return jsonify({"order_ids": order_no, "total_amount": total_amount})

        return render_template("pending_payments.html", customers=customer_names)
    return render_template("login.html",form=g.login_form)



@app.route("/customer_paymentStatus", methods=["GET", "POST"])
def customer_paymentStatus():
    if g.user:
        amountLeftoPay = 0
        amountPaid = 0

        if request.method == "POST":

            try:
                order_no = request.form["no_order"]
                customer = request.form["customerName"]
                # get total amount from order database.
                order = Orders.query.filter_by(order_id=order_no).first()
                totalAmount = order.total_amount

                #get customer from database.
                customer = Customer.query.filter_by(name=customer).first()

                payment = Payment.query.filter_by(order_id=order_no).first()
                #check if payment has order info in it.
                #first time customer has generated the order and no payment has been made to the payment database..
                if payment is None:
                    amountLeftoPay = totalAmount
                else:

                    p = Payment.query.filter_by(customer_id=customer.id).filter_by(order_id= order.order_id).all()
                    amountPaid = sum([i.amount_paid for i in p])
                    amountLeftoPay = totalAmount - amountPaid





            except Exception as e:
                print (e)
                flash ("Order number not selected", "danger")
                return redirect(url_for("pending_payments"))
        return render_template("customer_paymentStatus.html", amountLeftoPay=amountLeftoPay, amountPaid=amountPaid, totalAmount=totalAmount)
    return render_template("login.html",form=g.login_form)


@app.route("/view_history", methods=["GET", "POST"])
def history():
    if g.user:
        #view all customers who have placed order regarless of payment status with Filter = False flag
        customer_names = customerNamesforOrders(filter=False)
        if request.method == "POST":
            name = request.form["customer_name"]
            # grab orders that customer has not paid complete..
            order_no, total_amount = getOrderData(name, filter=False)
            return jsonify({"order_ids": order_no, "total_amount": total_amount})
        return render_template("account_history.html", customers=customer_names)
    return render_template("login.html",form=g.login_form)



@app.route("/viewHistory_Info", methods=["GET", "POST"])
def viewHistory_Info():
    if g.user:
        if request.method == "POST":
            name = request.form["customerName"]
            order_no = request.form["no_order"]

            #get order
            order = Orders.query.filter_by(order_id=order_no).first()
            #get customer.
            customer = Customer.query.filter_by(name=name).first()
            payment = Payment.query.filter_by(customer_id=customer.id).filter_by(order_id=order_no).all()

            date = [pay.date.strftime("%d/%m/%Y") for pay in payment]
            bank_name = [pay.bank_name for pay in payment ]
            amount_paid = [pay.amount_paid for pay in payment]
            data = list(zip(date, bank_name, amount_paid))
            print (data)

        return render_template("account_historyInfo.html", data=data, order_cost="₦" + str(order.total_amount))
    return render_template("login.html",form=g.login_form)


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


    return ""

@app.route("/view_customer", methods=["GET", "POST"])
def manage_customer():
    #get all customers..
    if g.user:
        customers = Customer.query.all()
        return render_template("view_customer.html", customers=customers)
    return render_template("login.html",form=g.login_form)









