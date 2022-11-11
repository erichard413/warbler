from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired(),Length(max=280)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserUpdateForm(FlaskForm):
    """Form for editing user profiles."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Write a good bio to describe yourself', validators=[Length(max=300)])
    password = PasswordField('Password', validators=[Length(min=6, max=15)])

class UpdatePasswordForm(FlaskForm):
    """Update PW form"""
    password = PasswordField('Password', validators=[Length(min=6, max=15)])
    new_password = PasswordField('New Password', validators=[Length(min=6, max=15), EqualTo("confirm", message='Passwords must match!')])
    confirm = PasswordField('Repeat Password', validators=[Length(min=6, max=15)])
    