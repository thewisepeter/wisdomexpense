import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from expense_app import app, db, bcrypt
from expense_app.models import User, Expenses, Income, SpendingLimit, PlannerItem
from expense_app.forms import RegistrationForm, UpdateAccountForm, LoginForm
from expense_app.forms import  ExpenseForm, IncomeForm, SpendingLimitForm, PlannerItemForm
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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # resizing the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


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
        
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        else:
            picture_file = 'default.jpg'

        user = User(username=form.username.data, email=form.email.data, password=hashed_password, image_file=picture_file)
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


def save_receipt_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/receipt_pics', picture_fn)
    
    # resizing the image
    output_size = (600, 600)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return 'receipt_pics/' + picture_fn

#Handles addition of expenses
@app.route("/expense/new", methods=['GET', 'POST'])
@login_required
def new_expense():
        form = ExpenseForm()
        if form.validate_on_submit():

            # Calculate today's spending
            today = datetime.utcnow().date()
            total_spent_today = sum(
                expense.amount for expense in Expenses.query.filter_by(
                    user_id=current_user.id,
                    date_of_purchase=today
                )
            )

            # Get the current spending limit
            current_limit = SpendingLimit.query.filter(
                SpendingLimit.user_id == current_user.id,
                SpendingLimit.start_date <= today,
                SpendingLimit.end_date >= today
            ).first()

            if current_limit and (total_spent_today + form.amount.data > current_limit.daily_limit):
                flash('Warning: This expense exceeds your daily limit!', 'warning')
            
            if form.picture.data:
                picture_file = save_receipt_picture(form.picture.data)
                # current_user.image_file = picture_file
            else:
                picture_file = 'receipt_pics/default_receipt.png'
            
            expense=Expenses(
                title=form.title.data,
                amount=form.amount.data,
                category=form.category.data,
                date_of_purchase=form.date_of_purchase.data,
                description=form.description.data,
                receipt_image=picture_file,
                user_id=current_user.id
            )
            db.session.add(expense)
            db.session.commit()
            flash(f'Expense added!', 'success')
            return redirect(url_for('home'))
        return render_template('create_expense.html',title='Add Expense', form=form, legend="New Expense")

@app.route("/expenses")
@login_required  # Ensures only logged-in users can access this route
def view_expenses():
    user_expenses = Expenses.query.filter_by(user_id=current_user.id).all()
    return render_template('all_expenses.html', title='All Expenses', expenses=user_expenses)

@app.route("/expenses/<int:expense_id>")
@login_required  # Ensures only logged-in users can access this route
def expenses(expense_id):
    expense = Expenses.query.get_or_404(expense_id)
    if expense.author != current_user:
        abort(403)
    return render_template('expense.html', title=expense.title, expense=expense)


@app.route("/expense/<int:expense_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expenses.query.get_or_404(expense_id)
    if expense.author != current_user:
        abort(403)

    form = ExpenseForm()
    if form.validate_on_submit():
        # Calculate today's spending excluding the current expense
        today = datetime.utcnow().date()
        total_spent_today_excluding_current = sum(
            expense.amount for expense in Expenses.query.filter(
                Expenses.user_id == current_user.id,
                Expenses.date_of_purchase == today,
                Expenses.id != expense_id
            )
        )

        # Get the current spending limit
        current_limit = SpendingLimit.query.filter(
            SpendingLimit.user_id == current_user.id,
            SpendingLimit.start_date <= today,
            SpendingLimit.end_date >= today
        ).first()

        if current_limit and (total_spent_today_excluding_current + form.amount.data > current_limit.daily_limit):
            flash('Warning: Updating this expense exceeds your daily limit!', 'warning')
        

        if form.picture.data:
            picture_file = save_receipt_picture(form.picture.data)
            expense.receipt_image = picture_file

        expense.title = form.title.data
        expense.amount = form.amount.data
        expense.category = form.category.data
        expense.date_of_purchase = form.date_of_purchase.data
        expense.description = form.description.data
        
        db.session.commit()
        flash('Your expense has been updated!', 'success')
        return redirect(url_for('expenses', expense_id=expense.id))
    elif request.method == 'GET':
        form.title.data = expense.title
        form.amount.data = expense.amount
        form.category.data = expense.category
        form.date_of_purchase.data = expense.date_of_purchase
        form.description.data = expense.description

    return render_template('create_expense.html', title='Edit Expense', form=form, legend='Edit Expense')


@app.route("/expense/<int:expense_id>/delete", methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expenses.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        abort(403)
    db.session.delete(expense)
    db.session.commit()
    flash('Your expense has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/income/new", methods=['GET', 'POST'])
@login_required
def new_income():
    form = IncomeForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_receipt_picture(form.picture.data)
        else:
            picture_file = 'receipt_pics/default_receipt.png'
        
        income = Income(
            source=form.source.data,
            amount=form.amount.data,
            category = form.category.data,
            date_received=form.date_received.data,
            description=form.description.data,
            receipt_image = picture_file,
            user_id=current_user.id
        )
        
        db.session.add(income)
        db.session.commit()
        flash('Your income has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('create_income.html', title='New Income', form=form, legend='Update Income')


@app.route("/income")
@login_required  # Ensures only logged-in users can access this route
def all_income():
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    return render_template('all_income.html', title='All Income', incomes=incomes)

@app.route("/income/<int:income_id>")
@login_required  # Ensures only logged-in users can access this route
def view_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.author != current_user:
        abort(403)
    return render_template('income.html', title=income.source, income=income)


@app.route("/income/<int:income_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.author != current_user:
        abort(403)
    
    form = IncomeForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_receipt_picture(form.picture.data)
            income.receipt_image = picture_file
        
        income.source = form.source.data
        income.amount = form.amount.data
        income.category = form.category.data
        income.date_received = form.date_received.data
        income.description = form.description.data
        
        db.session.commit()
        flash('Your income has been updated!', 'success')
        return redirect(url_for('view_income', income_id=income.id))
    elif request.method == 'GET':
        form.source.data = income.source
        form.amount.data = income.amount
        form.category.data = income.category
        form.date_received.data = income.date_received
        form.description.data = income.description
    
    return render_template('create_income.html', title='Edit Income', form=form, legend="Edit Income")


@app.route("/income/<int:income_id>/delete", methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.author != current_user:
        abort(403)
    db.session.delete(income)
    db.session.commit()
    flash('Your income entry has been deleted!', 'success')
    return redirect(url_for('all_income'))


@app.route("/spending_limit/new", methods=['GET', 'POST'])
@login_required
def new_spending_limit():
    form = SpendingLimitForm()
    if form.validate_on_submit():
        spending_limit = SpendingLimit(
            daily_limit=form.daily_limit.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(spending_limit)
        db.session.commit()
        flash('Your spending limit has been set!', 'success')
        return redirect(url_for('view_spending_limits'))
    return render_template('create_spending_limit.html', title='New Spending Limit', form=form, legend='New Spending Limit')

@app.route("/spending_limits")
@login_required
def view_spending_limits():
    limits = SpendingLimit.query.filter_by(user_id=current_user.id).all()
    return render_template('spending_limits.html', title='Spending Limits', limits=limits)

@app.route("/spending_limit/<int:limit_id>", methods=['GET'])
@login_required
def view_spending_limit(limit_id):
    limit = SpendingLimit.query.get_or_404(limit_id)
    if limit.user_id != current_user.id:
        abort(403)

    return render_template('view_spending_limit.html', title='Spending Limit', limit=limit)

@app.route("/spending_limit/<int:limit_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_spending_limit(limit_id):
    limit = SpendingLimit.query.get_or_404(limit_id)
    if limit.user_id != current_user.id:
        abort(403)

    form = SpendingLimitForm()
    if form.validate_on_submit():
        limit.daily_limit = form.daily_limit.data
        limit.start_date = form.start_date.data
        limit.end_date = form.end_date.data

        db.session.commit()
        flash('Spending limit updated successfully!', 'success')
        return redirect(url_for('view_spending_limits'))
    
    elif request.method == 'GET':
        form.daily_limit.data = limit.daily_limit
        form.start_date.data = limit.start_date
        form.end_date.data = limit.end_date

    return render_template('create_spending_limit.html', title='Edit Spending Limit', form=form, limit=limit, legend='Edit Limit')


@app.route("/spending_limit/<int:limit_id>/delete", methods=['POST'])
@login_required
def delete_spending_limit(limit_id):
    limit = SpendingLimit.query.get_or_404(limit_id)
    if limit.user_id != current_user.id:
        abort(403)

    db.session.delete(limit)
    db.session.commit()
    flash('Spending limit deleted successfully!', 'success')
    return redirect(url_for('view_spending_limits'))


@app.route("/planner_item/new", methods=['GET', 'POST'])
@login_required
def new_planner_item():
    form = PlannerItemForm()
    if form.validate_on_submit():
        planner_item = PlannerItem(
            title=form.title.data,
            description=form.description.data,
            planned_date=form.planned_date.data,
            user_id=current_user.id
        )
        db.session.add(planner_item)
        db.session.commit()
        flash('Your planner item has been added!', 'success')
        return redirect(url_for('view_planner_items'))
    return render_template('create_planner_item.html', title='New Planner Item', form=form, legend='New Planner Item')

@app.route("/planner_items")
@login_required
def view_planner_items():
    items = PlannerItem.query.filter_by(user_id=current_user.id).all()
    return render_template('planner_items.html', title='Planner Items', items=items)

@app.route("/planner_item/<int:planner_item_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_planner_item(planner_item_id):
    planner_item = PlannerItem.query.get_or_404(planner_item_id)
    if planner_item.user_id != current_user.id:
        abort(403)

    form = PlannerItemForm()
    if form.validate_on_submit():
        planner_item.title = form.title.data
        planner_item.description = form.description.data
        planner_item.planned_date = form.planned_date.data
        db.session.commit()
        flash('Your planner item has been updated!', 'success')
        return redirect(url_for('view_planner_items'))
    elif request.method == 'GET':
        form.title.data = planner_item.title
        form.description.data = planner_item.description
        form.planned_date.data = planner_item.planned_date

    return render_template('create_planner_item.html', title='Edit Planner Item', form=form, legend='Edit Planner Item')


@app.route("/planner_item/<int:planner_item_id>/delete", methods=['POST'])
@login_required
def delete_planner_item(planner_item_id):
    planner_item = PlannerItem.query.get_or_404(planner_item_id)
    if planner_item.user_id != current_user.id:
        abort(403)

    db.session.delete(planner_item)
    db.session.commit()
    flash('Your planner item has been deleted!', 'success')
    return redirect(url_for('view_planner_items'))
