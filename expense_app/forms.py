from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import FileField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed
from datetime import datetime

# This a form that handles User SignUp
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confrim Password',
                                     validators=[DataRequired(), EqualTo('password')])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')


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
    date_of_purchase = StringField('Date of Purchase', validators=[DataRequired()])
    description = TextAreaField('Description')
    receipt_image = FileField('Receipt Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Add Expense')

    def validate_date_of_purchase(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, please use YYYY-MM-DD")
