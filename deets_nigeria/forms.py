from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FloatField
from wtforms.validators import DataRequired, ValidationError, InputRequired
from wtforms.fields.html5 import DateField
from deets_nigeria.models import Product, Customer



def check_product(form, field):
    product = Product.query.filter_by(product_name=form.name_of_product.data).first()
    if product:
        raise ValidationError("{} product already registered!".format(form.name_of_product.data))

def customer_exist(form, field):
    customer_name = Customer.query.filter_by(name=form.name.data.lower()).first()
    if customer_name:
        raise ValidationError("{} already registered".format(form.name.data))


class WarehouseForm(FlaskForm):
    name_of_product = StringField('Name of Product', validators=[DataRequired(), check_product])
    price = FloatField("Price per bag (Naira)", validators=[DataRequired()])
    #kg = FloatField("kg per bag", validators=[DataRequired()])


class CustomerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), customer_exist])
    address = StringField("Address", validators=[DataRequired()])
    phone_number = StringField("Phone number", validators=[DataRequired()])

class UpdateProductForm(FlaskForm):
    date = DateField("Date",format="%Y-%m-%d", validators=[DataRequired()])
    product_quantity = IntegerField("Product Quantity", validators=[DataRequired()])



