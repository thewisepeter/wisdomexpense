from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, ExpenseForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '4fae35a28915d9bc651e0bc712350e5d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
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
                           default='default_receipt.jpg')
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


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'

    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/addexpense", methods=['GET', 'POST'])
def addexpense():
        form = ExpenseForm()
        if form.validate_on_submit():
            flash(f'Expense added!', 'success')
            return redirect(url_for('home'))
        return render_template('addExpense.html',title='Add Expense', form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
