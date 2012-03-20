from flask.ext.security import UserNotFoundError, user_datastore
from flask.ext.wtf import (Form, TextField, PasswordField, Required, Optional,
                           Email, Length, Regexp, ValidationError, SubmitField,
                           EqualTo) 

class UniqueUser(object):
    def __init__(self, message="User exists"):
        self.message = message
        
    def __call__(self, form, field):
        try:
            user_datastore.find_user(field.data)
            raise ValidationError(self.message)
        except UserNotFoundError:
            pass

validators = {
    'username': [
        Optional(),
        Length(min=3, max=20), 
        UniqueUser(message='Username is already taken')
    ],
    'email': [
        Required(), 
        Email(), 
        UniqueUser(message='Email address is associated with '
                           'an existing account')
    ],
    'password': [
        Required(), 
        Length(min=6, max=50), 
        EqualTo('confirm', message='Passwords must match'),
        Regexp(r'[A-Za-z0-9@#$%^&+=]', 
               message='Password contains invalid characters')
    ],
    'name': [
        Required(), 
        Length(min=2, max=100)
    ]
}

class RegisterForm(Form):
    username = TextField('Username', validators['username'])
    email = TextField('Email', validators['email'])
    password = PasswordField('Password', validators['password'], )
    confirm = PasswordField('Confirm Password')
    submit = SubmitField("Register")