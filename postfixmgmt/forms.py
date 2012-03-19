from wtforms import Form, validators
from flaskext.wtf import Form, TextField, BooleanField, PasswordField, FileField, TextAreaField, HiddenField, SelectField
from wtforms.validators import ValidationError, StopValidation
from postfixmgmt.auth import check_user_password, check_password
from postfixmgmt.models import Admin, Domain, Address
from postfixmgmt.regex import DOMAIN_REGEX, EMAIL_USERNAME_REGEX, EMAIL_ADDRESS_REGEX


def validate_login_user(form, field):
    if not Admin.query.filter_by(email=field.data).first():
        raise ValidationError("Invalid login")
    u = Admin.query.filter_by(email=form.data['email']).first()
    if not check_user_password(u, form.data['password']):
        raise ValidationError("Invalid login")
    return True

def validate_active_user(form, field):
    if not Admin.query.filter_by(email=field.data, active=True).first():
        raise ValidationError("Account is not active")

def validate_domain_doesnt_exist(form, field):
    if Domain.query.filter_by(name=field.data).first():
        raise ValidationError("Domain already exists")

def validate_domain_name(form, field):
    if not DOMAIN_REGEX.match(field.data):
        raise ValidationError("Invalid domain name format")

def validate_email_username(form, field):
    if not EMAIL_USERNAME_REGEX.match(field.data):
        raise ValidationError("Invalid username format")

def validate_combined_email_address(form, field):
    if not EMAIL_ADDRESS_REGEX.match("%s@%s" % (form.data['username'], form.data['domain'])):
        raise ValidationError("Invalid email address format")
    
def validate_email_address(form, field):
    if not EMAIL_ADDRESS_REGEX.match(field.data):
        raise ValidationError("Invalid email address format")

def validate_combined_email_address_doesnt_exist(form, field):
    if Address.query.filter_by(username=form.data['username'], 
                               domain=Domain.query.filter_by(name=form.data['domain']).first()
                               ).first():
        raise ValidationError("Account already exists")
    
def validate_admin_doesnt_exist(form, field):
    if Admin.query.filter_by(email=field.data).first():
        raise ValidationError("Account already exists")

class LoginForm(Form):
    email = TextField('Email', [validators.Required(message="Please enter your email address"), validate_login_user, validate_active_user])
    password = PasswordField('Password', [validators.Required(message="Please enter your password")])


class DomainAddForm(Form):
    name = TextField('Name', [validators.Required(message="You need to provide a domain name"), validate_domain_doesnt_exist, validate_domain_name])
    description = TextAreaField('Description')


class DomainEditForm(Form):
    id = HiddenField()
    name = TextField("Name", [validators.Required(message="You need to provide a domain name"), validate_domain_doesnt_exist, validate_domain_name])
    description = TextAreaField('Description')


class AddressAddForm(Form):
    username = TextField('Username', [validators.Required(message="You need to provide a username"), 
                                      validators.Length(min=1, max=128), validate_email_username, validate_combined_email_address,
                                      validate_combined_email_address_doesnt_exist])
    domain = SelectField('Domain', [validators.Required("You need to select a domain"), validate_domain_name], choices=[])
    password = PasswordField('Password', [validators.Required(message="You need to provide a password"), validators.Length(min=6)])
    active = BooleanField('Active')


class AddressEditForm(Form):
    id = HiddenField()
    username = TextField('Username', [validators.Required(message="You need to provide a username"), 
                                      validators.Length(min=1, max=128), validate_email_username, validate_combined_email_address])
    domain = SelectField('Domain', [validators.Required("You need to select a domain"), ], choices=[])
    active = BooleanField('Active')


class AddressPasswordEditForm(Form):
    id = HiddenField()
    password = PasswordField('Password', [validators.Required("You need to provide a password"), validators.Length(min=6)])


class AliasAddForm(Form):
    username = TextField("Username", [validators.Required(message="You need to provide a username"), 
                                      validators.Length(min=1, max=128), validate_email_username, validate_email_address,
                                      validate_combined_email_address_doesnt_exist])
    domain = SelectField('Domain', [validators.Required("You need to select a domain"), validate_domain_name], choices=[])
    goto = TextField("Goto", [validators.Required(message="You need to provide a goto address"), validate_email_address])


class AliasEditForm(Form):
    id = HiddenField()
    username = TextField("Username", [validators.Required(message="You need to provide a username"), 
                                      validators.Length(min=1, max=128), validate_email_username, validate_email_address,
                                      validate_combined_email_address_doesnt_exist])
    domain = SelectField('Domain', [validators.Required("You need to select a domain")], choices=[])
    goto = TextField("Goto", [validators.Required(message="You need to provide a goto address"), validate_email_address])

class AdminAddForm(Form):
    email = TextField("Email", [validators.Required(message="You need to provide an email address"), validate_email_address,
                                validate_admin_doesnt_exist])
    password = PasswordField("Password", [validators.Required(message="You need to provide a password"), validators.Length(min=6)])
    active = BooleanField("Active")


class AdminEditForm(Form):
    id = HiddenField()
    email = TextField("Email", [validators.Required(message="You need to provide an email address"), validate_email_address,
                                validate_admin_doesnt_exist])
    active = BooleanField("Active")


class AdminEditPassword(Form):
    id = HiddenField()
    password = PasswordField("Password", [validators.Required(message="You need to provide a password"), validators.Length(min=6)])
