from wtforms import Form, StringField, TextAreaField, PasswordField, validators

class RegisterForm(Form):
    name= StringField('Name', [validators.Length(min=2,max=45)])
    email= StringField('E-Mail', [validators.length(min=6,max=45)])
    password=PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm',message="Passwords don't match")
    ])
    confirm= PasswordField('Confirm Password')

class BookAdd(Form):
    title= StringField('Title', [validators.Length(min=5)])
    author= StringField('Author', [validators.length(min=6,max=45)])
    ISBN = StringField('ISBN')
    ratings=StringField('Ratings',[validators.length(min=12,max=16)])

class UserSearch(Form):
    email=StringField('E-Mail',[validators.Length(min=6)])
class VerifyOTP(Form):
    otp=StringField('OTP')

class CommentForm(Form):
    comment=StringField('COMMENT',[validators.Length(min=0)])
