import datetime
import os
from peewee import Model, CharField, IntegerField, ForeignKeyField, DateField, JOIN, fn, AutoField, BooleanField, FloatField
from playhouse.db_url import connect

# db = connect(os.environ.get('DATABASE_URL', 'sqlite:///booking.db'))
db = connect('postgres://u75t8s1co5mrjh:pa5cd7c2cc8cde578f5cb9f8cde67a1a676f9a0f78bb01e437678b90b89264d12@c9mq4861d16jlm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d7r3qdc24d5ai8')

class Customer(Model):
    # id = IntegerField(primary_key=True)
    id=AutoField(primary_key=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField()

    def to_string(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        database = db
        db_table = 'Employee'

class Order(Model):
    id = AutoField(primary_key=True)
    description = CharField()
    is_hazard=BooleanField(default=False)
    is_international=BooleanField(default=False)
    weight=FloatField()
    volume=FloatField()
    deliver_by = DateField()
    price = FloatField()
    order_placed = DateField()
    deliver_method=CharField()
    comment=CharField()
    customer_id=ForeignKeyField(Customer,backref='Order')

    def to_string(self):
        return (f"'{self.description}' booked on {self.order_placed} for delivery by {self.deliver_by} by {self.deliver_method} "
                f"for {'${:,.2f}'.format(self.price)}")

    @staticmethod
    def get_shipping_options(order,urgent):
        options = {"plane":None,
                   "truck":None,
                   "ship":None}
        if order["is_hazardous"] and urgent:
            return options
        if not order["is_hazardous"]:
            options['plane']=max(order['volume']*20,order['weight']*10)
        if not order['is_international']:
            options['truck']=45 if urgent else 25
        if order['is_international']:
            options['ship']=30
        return options

    @staticmethod
    def validate_dimensions(v,w):
        if v*w==0:
            return False,"Volume and Weight cannot be zero"
        if (v >= 125 and  w >= 10):
            return False,"Item exceeds capacity. Weight must be under 10kg or Volume must be 125m^3 or less"
        return True, None

    @staticmethod
    def is_urgent(deliver_by):
        return True if (deliver_by.date() - datetime.datetime.now().date()).days <=3 else False

    class Meta:
        database = db
        db_table = 'Order'

def get_customers():
    return Customer.select().order_by(Customer.first_name)
def get_customer(cust_id):
    c = Customer.get(Customer.id == cust_id)
    return c

def try_add_customer(c):
    try:
        customer = Customer.create(first_name=c["first_name"],last_name=c["last_name"],email=c["email"])
        customer.save()
        return True,customer
    except Exception as ex:
        return False,ex

def try_add_order(order,selected):
    try:
        o=order[1]
        m=[x for x in order[0] if x[0]==selected][0]

        r = Order.create(description=o["description"],is_hazard=o["is_hazardous"],is_international=o["is_international"],
                         weight=o["weight"],volume=o["volume"],deliver_by=o["deliver_by"],customer_id=o["customer_id"],
                         price=m[1],deliver_method=m[0],order_placed=datetime.datetime.now(),comment=m[2])
        r.save()
        return True,r
    except Exception as ex:
        return False,ex

def get_orders(id):
    return (Order().select().where(Order.customer_id==id).order_by(Order.deliver_by.desc()))

def init():
    db.connect()
    db.drop_tables([Customer,Order])
    db.create_tables([Customer,Order])

    for c in ["Shawn Hopkins","Tim Smith"]:
        c=Customer.create(first_name=c.split()[0],last_name=c.split()[1],email="shawn.hopkins1@gmail.com")
        c.save()

def try_update_customer(c):
    try:
        customer = Customer.get_by_id(c["id"])
        customer.first_name=c["first_name"]
        customer.last_name=c["last_name"]
        customer.email=c["email"]
        customer.save()
        return True,customer
    except Exception as ex:
        return False,ex

def try_delete_customer(id):
    try:
        c = Customer.get_by_id(id)
        c.delete_instance()
        return True
    except Exception as ex:
        return False,ex


# init()