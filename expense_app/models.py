from datetime import datetime
from expense_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    """
        this returns a user from an ID
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='profile_pics/default.jpg')
    password = db.Column(db.String(60), nullable=False)
    expenses = db.relationship('Expenses', backref='author', lazy=True)
    income = db.relationship('Income', backref='author', lazy=True)
    spending_limits = db.relationship('SpendingLimit', backref='author',
                                      lazy=True)
    planner_items = db.relationship('PlannerItem', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_of_purchase = db.Column(db.DateTime, nullable=False,
                                 default=datetime.utcnow)
    description = db.Column(db.Text)
    receipt_image = db.Column(db.String(20), nullable=False,
                           default='receipt_pics/default_receipt.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (f"Expense('{self.title}', '{self.amount}', "
                f"'{self.date_of_purchase}, {self.category}')")


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date_received = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (f"Income('{self.source}', '{self.amount}', "
                f"'{self.date_received}')")


class SpendingLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_limit = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (f"SpendingLimit('{self.daily_limit}', '{self.start_date}', "
                f"'{self.end_date}')")


class PlannerItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    planned_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"PlannerItem('{self.title}', '{self.planned_date}')"
