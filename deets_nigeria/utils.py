from deets_nigeria.models import Customer,Orders
from datetime import timedelta, date

def getOrderData(customer_name, filter=False):
    """

    :param customer_name:
    :return: order_number for customer and the total amount for the order.
    """

    customer = Customer.query.filter_by(name=customer_name).first()
    if filter:
        order_numbers = [order.order_id for order in customer.orders if order.paid_status==False]
    else:
        order_numbers = [order.order_id for order in customer.orders]

    total_amount = [order.total_amount for order in customer.orders]
    return order_numbers, total_amount

def customerNamesforOrders(filter=False):
    """

    :return: all customer names who have placed order..
    """
    orders = Orders.query.all()


    if filter:
        customers = set([order.customer_id for order in orders if order.paid_status== False ])
    else:
        customers = set([order.customer_id for order in orders])


    # get customer names...
    customer_names = set([Customer.query.filter_by(id=customer).first().name for customer in customers])

    return customer_names


def daterange(date1, date2):
    for n in range(int((date2-date1).days)+1):
        yield date1 + timedelta(n)

