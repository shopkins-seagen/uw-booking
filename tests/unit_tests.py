import unittest
import app
from peewee import SqliteDatabase
from datetime import datetime,timedelta
from model import Customer,Order,get_customers



class TestCase(unittest.TestCase):
    def setUp(self):
        # Don't use a real database, instead, let's use an in-memory version that gets thrown away once tests are done
        self.database = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
        # Bind our tables to this one instead of our people.db file
        self.database.bind([Customer, Order])
        # Connect and create tables
        self.database.connect()
        self.database.create_tables([Customer, Order])
        seed()
    def tearDown(self):
        self.database.drop_tables([Customer, Order])
        self.database.close()

    def test_get_customers(self):
        customers=app.get_customers()
        self.assertEqual(len(customers), 2)
    def test_get_customer(self):
        customer=app.get_customer(1)
        self.assertEqual(customer.first_name,"Shawn")
    def test_get_orders(self):
        orders=app.get_orders(1)
        self.assertEqual(orders[0].deliver_by, datetime.now().date() + timedelta(days=5))
    def test_update_customer(self):
        customer=app.get_customer(2)
        is_updated = app.try_update_customer({
                "id":customer.id,
                "first_name":"John",
                "last_name":customer.last_name,
                "email":customer.email})
        self.assertTrue(is_updated)
        self.assertEqual(app.get_customer(2).first_name,"John")

    def test_validate_dimensions(self):
        self.assertTrue(Order.validate_dimensions(124.9,9.9)[0])
        response = Order.validate_dimensions(125,10)
        self.assertFalse(response[0])
        self.assertRegex(response[1],'exceeds')
        self.assertTrue(Order.validate_dimensions(200,9.9)[0])
        response = Order.validate_dimensions(0,50)
        self.assertFalse(response[0])
        self.assertRegex(response[1],'zero')

    def test_is_urgent(self):
        today = datetime.now()
        self.assertTrue(Order.is_urgent( today + timedelta(days=3)))
        self.assertFalse(Order.is_urgent(today + timedelta(days=4)))

    def test_shipping_options_1(self):
        today = datetime.now()

        order = create_order(True,True,today.strftime('%Y-%m-%d'))
        options = Order.get_shipping_options(order,order['is_urgent'])

        self.assertEqual(options['plane'],0)
        self.assertEqual(options['truck'],None)
        self.assertEqual(options['ship'],30)

    def test_shipping_options_2(self):
        today = datetime.now()

        order = create_order(False,False,today.strftime('%Y-%m-%d'))
        options = Order.get_shipping_options(order,order['is_urgent'])

        self.assertEqual(options['plane'],float(100))
        self.assertEqual(options['truck'],float(45))
        self.assertEqual(options['ship'],None)

    def test_shipping_options_3(self):
        today = datetime.now() + timedelta(days=5)

        order = create_order(False, True, today.strftime('%Y-%m-%d'),weight=20)
        options = Order.get_shipping_options(order, order['is_urgent'])

        self.assertEqual(options['plane'], float(200))
        self.assertEqual(options['truck'], None)
        self.assertEqual(options['ship'], 30)





def seed():
    for c in ["Shawn Hopkins","Tim Smith"]:
        c=Customer.create(first_name=c.split()[0],last_name=c.split()[1],email="shawn.hopkins1@gmail.com")
        c.save()
        order = Order().create(customer_id=c.id,description=c.first_name,is_hazard=True,is_international=False,
                               weight=5.2,volume=3.3,deliver_by=datetime.now() + timedelta(days=5),order_placed=datetime.now(),
                               price=10.2,deliver_method="plane",comment="this is only a test")
        order.save()

def create_order(is_hazardous,is_international,deliver_by,weight=5,volume=5):
    order = {
        'description': "description",
        'is_hazardous': is_hazardous,
        'is_international': is_international,
        'weight': float(weight),
        'volume': float(volume),
        'is_urgent': Order.is_urgent(datetime.strptime(deliver_by, '%Y-%m-%d')),
        'deliver_by': datetime.strptime(deliver_by, '%Y-%m-%d')
    }
    return order

if __name__ == '__main__':
    unittest.main()
