from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, User, Billing, BillingItem
from datetime import datetime
import config
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    mobile = request.args.get('mobile', '')
    if request.method == 'POST':
        mobile = request.form['mobile']
        name = request.form['name']
        email = request.form.get('email', '')
        address = request.form.get('address', '')

        user = User(mobile=mobile, name=name, email=email, address=address)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_user.html', mobile=mobile)

@app.route('/get_users')
def get_users_page():
    users = User.query.all()
    user_list = [{"mobile": user.mobile, "name": user.name, "email": user.email, "address": user.address} for user in users]
    return render_template('get_users.html', users=user_list)

@app.route('/get_user', methods=['GET'])
def get_user():
    mobile = request.args.get('mobile')
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        return render_template('user_profile.html', user=user)
    else:
        return redirect(url_for('add_user', mobile=mobile))

@app.route('/enter_mobile', methods=['GET', 'POST'])
def enter_mobile():
    # if request.method == 'POST':
    mobile = request.form.get('mobile')
    if not mobile:
        error = "Please provide a mobile number."
        return render_template('enter_mobile.html', error=error)

    # Redirect back to billing session after entering mobile number
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        billing = Billing(mobile=mobile, amount_paid=0, total_amount=0,  method_of_payment='', date=datetime.now().date(), active=True)
        db.session.add(billing)
        db.session.commit()
        return redirect(url_for('billing_session', billing_id=str(billing.id)))

    # billing_id = request.args.get('billing_id')
    # return render_template('enter_mobile.html', billing_id=billing_id)


@app.route('/start_billing_session', methods=['POST','GET'])
def start_billing_session():
    
    mobile = request.form.get('mobile', None)
    
    if mobile:
        user = User.query.filter_by(mobile=mobile).first()
        if user:
            print("here")
            billing = Billing(mobile=mobile, amount_paid=0, total_amount=0,  method_of_payment='', date=datetime.now().date(), active=True)
            print("here 2", billing)
            db.session.add(billing)
            db.session.commit()
            return redirect(url_for('billing_session', billing_id=str(billing.id)))
        return "User not found"
    else:
        return redirect(url_for('enter_mobile'))

@app.route('/billing_session/<uuid:billing_id>', methods=['GET', 'POST'])
def billing_session(billing_id):
    billing = Billing.query.get_or_404(billing_id)
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_price = float(request.form['item_price'])
        quantity = int(request.form.get('quantity'))
        total_amount = item_price * quantity
        item = BillingItem(billing_id=billing_id, item_name=item_name, item_price=total_amount, quantity=quantity)
        db.session.add(item)
        db.session.commit()

    items = BillingItem.query.filter_by(billing_id=billing_id).all()
    total_cost = sum(item.item_price for item in items)
    return render_template('billing_session.html', billing=billing, items=items, total_cost=total_cost)

@app.route('/active_sessions')
def active_sessions():
    active_billings = Billing.query.filter_by(active=True).all()
    return render_template('active_session.html', billings=active_billings)

@app.route('/end_billing_session/<uuid:billing_id>', methods=['POST'])
def end_billing_session(billing_id):

    amount_paid = request.form['amount_paid']
    method_of_payment = request.form['method_of_payment']
    remarks = request.form['remarks']
    billing_items = BillingItem.query.filter_by(billing_id=billing_id).all()
    total_cost = sum(item.item_price for item in billing_items)

    billing = Billing.query.get_or_404(billing_id)
    billing.active = False
    billing.amount_paid = float(amount_paid)
    billing.method_of_payment = method_of_payment
    billing.payment_date = datetime.now().date()
    billing.remarks = remarks
    billing.total_amount = total_cost
    db.session.commit()
    return redirect(url_for('active_sessions'))

@app.route('/delete_item/<uuid:billing_id>/<uuid:item_id>', methods=['DELETE'])
def delete_item(billing_id, item_id):
    # item = BillingItem.query.get_or_404(item_id)
    item_detail = BillingItem.query.filter_by(id=item_id)
    item_detail.delete()
    db.session.commit()
    items = BillingItem.query.filter_by(billing_id=billing_id).all()

    return render_template('billing_session.html', billing=billing_id, items=items)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
