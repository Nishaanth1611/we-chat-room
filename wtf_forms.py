from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length ,EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from models import *


def invalid_credentials(form, field):
    """ Username and password checker """

    username_entered = form.username.data
    password_entered = field.data

    # Check username is invalid
    user_data = User.query.filter_by(username=username_entered).first()
    if user_data is None:
        raise ValidationError("Username or password is incorrect")

    elif not pbkdf2_sha256.verify(password_entered, user_data.password):
        raise ValidationError("Username or password is incorrect")

class RegistrationForm(FlaskForm):

    
    username = StringField("username_label",validators=[InputRequired(message="Username required"),Length(min=4,max=24,message="Username must between 6 to 24 characters")])
    password = PasswordField("password_label",validators=[InputRequired(message="Password required"),Length(min=4,max=24,message="Password must between 8 to 24 characters")])
    confirm_pass = PasswordField("confirm_pass_label",validators=[InputRequired(message="Password required"),EqualTo("password",message ="Password must match")])
    submit_button = SubmitField("Create")

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")

class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), invalid_credentials])

     