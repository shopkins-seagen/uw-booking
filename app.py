from flask import Flask, redirect, url_for, render_template, session, request, jsonify, flash, send_from_directory
from model import (get_customers, get_customer,Customer, Order, try_add_customer,
                   try_add_order,get_orders,try_delete_customer,try_update_customer)
from datetime import datetime, timedelta
from flask_restful import Api,Resource
from babel.numbers import format_currency
import os

app = Flask(__name__,
            template_folder='templates',
            static_url_path='',
            static_folder='static')
app.config["SECRET_KEY"] = 'key'
app.config['DATABASE_URL']='postgres://u75t8s1co5mrjh:pa5cd7c2cc8cde578f5cb9f8cde67a1a676f9a0f78bb01e437678b90b89264d12@c9mq4861d16jlm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d7r3qdc24d5ai8'
api=Api(app)

@app.template_filter()
def dollar(value):
   return format_currency(value, 'USD', locale='en_US')

app.jinja_env.filters['dollar'] = dollar

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pass
    return render_template('index.html', customers=get_customers())

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        customer = {

            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']
        }
        isadded = try_add_customer(customer)
        if isadded[0]:
            return redirect(url_for('index'))
        else:
            flash(f"Error attempting to save customer: {isadded[1]}")
    return render_template('customer.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        customer = {
            'id':id,
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']
        }
        isupdated = try_update_customer(customer)
        if isupdated[0]:
            return redirect(url_for('index'))
        else:
            flash(f"Error attempting to save customer: {isupdated[1]}")
    return render_template('edit.html',customer=get_customer(id),orders=get_orders(id))

@app.route('/order/<int:id>', methods=['GET', 'POST'])
def order(id):
    if request.method == 'POST':
        order = {
            'customer_id': id,
            'description': request.form['description'],
            'is_hazardous': True if request.form.get('is_hazardous') == 'on' else False,
            'is_international': True if request.form.get('is_international') else False,
            'weight': float(request.form['weight']),
            'volume': float(request.form['volume']),
            'is_urgent': Order.is_urgent(datetime.strptime(request.form['deliver_by'], '%Y-%m-%d')),
            'deliver_by': datetime.strptime(request.form['deliver_by'], '%Y-%m-%d')
        }


        check_size = Order.validate_dimensions(order['volume'], order['weight'])
        if not check_size[0]:
            flash(check_size[1])
        else:
            options = Order.get_shipping_options(order, Order.is_urgent(order["deliver_by"]))
            opts = []
            for k, v in list(options.items()):
                if v is None:
                    del options[k]
                else:
                    deliver_by = " "
                    if k == 'plane':
                        deliver_by = f" arriving by {order['deliver_by'].strftime('%d-%b-%Y')} "
                    entry = (k, v, f"By {k}{deliver_by}for {'${:,.2f}'.format(v)}")
                    opts.append(entry)
            session['quote_data'] = (opts, order)
            return redirect(url_for('quote'))


    return render_template('order.html', customer=get_customer(id)
                           , date=datetime.date(datetime.now())
                           , default=datetime.date(datetime.now()) + timedelta(days=4))


@app.route('/quotes', methods=['GET','POST'])
def quote():
    if request.method == 'POST':
        selected=request.values.get("quotes")
        session['selected_data']=selected
        response = try_add_order(session.get('quote_data'),selected)
        if not response[0]:
            flash(response[1])
        else:
            return redirect(url_for('confirm'))
    return render_template('quotes.html', options=session.get('quote_data')[0], order=session.get('quote_data')[1])

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    response = try_delete_customer(id)
    return redirect(url_for('index'))
@app.route('/confirmation', methods=['GET'])
def confirm():
    options= session.get('quote_data')[0]
    orders= session.get('quote_data')[1]
    selected=session.get('selected_data')
    method=next(x for x in options if x[0]==selected)
    return render_template('confirmation.html',order=orders,method=method)

class ApiOrders(Resource):
    def get(self,id):
        return jsonify([to_dict(x) for x in get_orders(id)])
api.add_resource(ApiOrders, '/api/orders/<int:id>')

def to_dict(e):
    d = {
        "id":e.id,
        "description" : e.description,
        "order_placed":e.order_placed,
        "deliver_method":e.deliver_method,
        "comment":e.comment}
    return d

if __name__ == '__main__':
    # app.run()
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
