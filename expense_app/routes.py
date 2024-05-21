import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request
from expense_app import app, db, bcrypt
from expense_app.models import User, Expenses, Income, SpendingLimit, PlannerItem
from expense_app.forms import RegistrationForm, UpdateAccountForm, LoginForm, ExpenseForm
from flask_login import login_user, current_user, logout_user, login_required

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
    '''
        This redirects me home
    '''
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    '''
        This is the landing/ about page
    '''
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    '''
        This is where users register and get an account
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
        Handles logging in of registered users
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/addexpense", methods=['GET', 'POST'])
def addexpense():
        '''
            Handles addition of expenses
        '''
        form = ExpenseForm()
        if form.validate_on_submit():
            flash(f'Expense added!', 'success')
            return redirect(url_for('home'))
        return render_template('add_expense.html',title='Add Expense', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # resizing the image
    output_size = (125, 125)
    i = Image.open()
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/logout")
def logout():
    '''
        Closes a user session
    '''
    logout_user()
    return redirect(url_for('about'))


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
