from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    mobile = db.Column(db.BigInteger, primary_key=True, unique=True)  # Ensure primary_key and unique constraint
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    address = db.Column(db.Text)

    def __repr__(self):
        return f'<User {self.name}>'
    
class Billing(db.Model):
    __tablename__ = 'billing'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile = db.Column(db.BigInteger, db.ForeignKey('users.mobile'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    method_of_payment = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.String(512), nullable=True)
    active = db.Column(db.Boolean, default=True)
    items = db.relationship('BillingItem', backref='billing', lazy=True)

class BillingItem(db.Model):
    __tablename__ = 'billing_item'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    billing_id = db.Column(UUID(as_uuid=True), db.ForeignKey('billing.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item_price = db.Column(db.Float, nullable=False)
