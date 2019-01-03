from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length 
from models import User,CatalogCategory
from app import session
from securityManager import SecurityManager


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = session.query(User).filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered')

class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class MyAccountForm(FlaskForm):
    email = StringField('Email / Username',
                        validators=[DataRequired(), Email()])
    name = StringField('Name',validators=[DataRequired()])
    picture = FileField('Profil Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update My Account')

    def validate_email(self, email):
        if email.data != SecurityManager().getAuthenticatedUser().email:
            user = session.query(User).filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email / username is already registered')

class CatalogItemForm(FlaskForm):
    #name =Column(String(80), nullable = False)
    #description = Column(String(250))
    categories = session.query(CatalogCategory).all()
    name = StringField('Name',validators=([DataRequired(),Length(0,80)]))
    description = TextAreaField('Description',validators=([Length(0,1000)]))
    category_id = SelectField('Category',coerce=int,choices=[(c.id, c.name) for c in categories])
    submit = SubmitField('save')
