from flask import render_template, flash, redirect, url_for, request
from expense_app import app
from expense_app.models import User, Expenses, Income, SpendingLimit, PlannerItem
from expense_app.forms import RegistrationForm, LoginForm, ExpenseForm

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

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/addexpense", methods=['GET', 'POST'])
def addexpense():
        form = ExpenseForm()
        if form.validate_on_submit():
            flash(f'Expense added!', 'success')
            return redirect(url_for('home'))
        return render_template('add_expense.html',title='Add Expense', form=form)


# @app.route("/expense/<int:expense_id>/edit", methods=['GET', 'POST'])
# def edit_expense(expense_id):
#     expense = Expenses.query.get_or_404(expense_id)
#     form = ExpenseForm()

#     if form.validate_on_submit():
#         expense.title = form.title.data
#         expense.category = form.category.data
#         expense.amount = form.amount.data
#         expense.date_of_purchase = datetime.strptime(form.date_of_purchase.data, '%Y-%m-%d')
#         expense.description = form.description.data

#         if form.receipt_image.data:
#             receipt_image_file = save_receipt_image(form.receipt_image.data)
#             expense.receipt_image = receipt_image_file

#         db.session.commit()
#         flash('Your expense has been updated!', 'success')
#         return redirect(url_for('home'))

#     elif request.method == 'GET':
#         form.title.data = expense.title
#         form.category.data = expense.category
#         form.amount.data = expense.amount
#         form.date_of_purchase.data = expense.date_of_purchase.strftime('%Y-%m-%d')
#         form.description.data = expense.description

#     return render_template('edit_expense.html', title='Edit Expense', form=form)
