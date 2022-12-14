from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired(),Length(max=280)])

class DirectMessageForm(FlaskForm):
    """Form for direct messages."""
    message_text = TextAreaField('Text', validators=[DataRequired(),Length(max=280)])

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
    

class AdminUserUpdateForm(FlaskForm):
    """Form for Admin editing user profiles."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Write a good bio to describe yourself', validators=[Length(max=300)])
    is_private = BooleanField('Make account private') 
    is_admin = BooleanField('Make account admin')
    is_verified = BooleanField('Verify user')

class UpdatePasswordForm(FlaskForm):
    """Update PW form"""
    password = PasswordField('Password', validators=[Length(min=6, max=15)])
    new_password = PasswordField('New Password', validators=[Length(min=6, max=15), EqualTo("confirm", message='Passwords must match!')])
    confirm = PasswordField('Repeat Password', validators=[Length(min=6, max=15)])

class PrivacySettingsForm(FlaskForm):
    """Privacy picker - radiobutton"""
    is_private = BooleanField('Make my account private')    