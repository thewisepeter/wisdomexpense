from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import IntegerField, TextAreaField, SelectField, DateField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from expense_app.models import User, SpendingLimit
from sqlalchemy import and_, or_

# This a form that handles User SignUp
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confrim Password',
                                     validators=[DataRequired(), EqualTo('password')])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
            this method checks if the username has already been taken 
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
        
    def validate_email(self, email):
        """
            this method checks if the email has already been taken
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


# This form updates the account details
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


# This a form that handles User Login
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# This captures expenses
class ExpenseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Miscellaneous', 'Miscellaneous'),
        ('Food', 'Food'),
        ('Transportation', 'Transportation'),
        ('Groceries', 'Groceries'),
        ('Clothing', 'Clothing'),
        ('Household', 'Household'),
        ('Rent', 'Rent'),
        ('Bills and Taxes', 'Bills and Taxes'),
        ('Vacations', 'Vacations')
    ], validators=[DataRequired()])
    date_of_purchase = DateField('Date of Purchase', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description')
    picture = FileField('Receipt Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Add Expense')


# This form captures Income
class IncomeForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired(), Length(max=100)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Salary', 'Salary'),
        ('Investment', 'Investment'),
        ('Gift', 'Gift'),
        ('Others', 'Others')
    ], validators=[DataRequired()])
    date_received = DateField('Date Received', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description')
    picture = FileField('Receipt Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Add Income')

class SpendingLimitForm(FlaskForm):
    daily_limit = IntegerField('Daily Limit', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Set Limit')

    def validate_start_date(self, start_date):
        if self.end_date.data < start_date.data:
            raise ValidationError("End date must be after the start date.")

        overlapping_limits = SpendingLimit.query.filter(
            SpendingLimit.user_id == current_user.id,
            or_(
                and_(SpendingLimit.start_date <= start_date.data, SpendingLimit.end_date >= start_date.data),
                and_(SpendingLimit.start_date <= self.end_date.data, SpendingLimit.end_date >= self.end_date.data),
                and_(SpendingLimit.start_date >= start_date.data, SpendingLimit.end_date <= self.end_date.data),
                and_(SpendingLimit.start_date <= start_date.data, SpendingLimit.end_date >= self.end_date.data),
            )
        ).all()

        if overlapping_limits:
            raise ValidationError("This period overlaps with an existing spending limit.")


class PlannerItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    planned_date = DateField('Planned Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Item')
