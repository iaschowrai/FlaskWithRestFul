from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user,UserMixin

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,SelectField,SubmitField, DecimalField, TextAreaField,EmailField
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mscs3150'
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')])
    user_type = SelectField('User Type', choices=[('Employer', 'Employer'), ('JobSeeker', 'JobSeeker')])
    submit = SubmitField('Register')

class JobForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    salary = StringField('Salary')
    company = StringField('Company', validators=[validators.DataRequired()])
    category = SelectField('Category', choices=[('FullTime', 'FullTime'), ('PartTime', 'PartTime'),('Contract', 'Contract')])
    description = TextAreaField('Description', validators=[validators.DataRequired()])
    email = EmailField('Email', validators=[validators.DataRequired()])
    submit = SubmitField('AddPost')

@app.route('/jobs', methods=['GET', 'POST'])
def addpost():
    form = JobForm()
    if form.validate_on_submit():
        title = form.title.data
        salary = form.salary.data
        company = form.company.data
        category = form.category.data
        description = form.description.data
        email= form.email.data
        response = requests.post('http://localhost:5001/api/jobs', json={'title' :title, 'salary':  salary, 'company': company, 'category': category, 'description': description, 'email': email})
        if response.status_code == 201:
            flash('Job Posted!')
            return redirect('/aboutme')
        else:
            flash('Job Not Posted Something wrong!')
    return render_template('create.html', form=form)

@app.route('/jobs/<int:job_id>', methods=['GET','PUT', 'DELETE'])
def view(job_id):
    if request.method == 'GET':
        response = requests.post('http://localhost:5001/api/jobs/'+ f'/{job_id}', json={'filled': True })
    return render_template('view.html', title= 'view', form=response)
                             

@app.route('/', methods=['GET', 'POST'])
def index():
    response = requests.get('http://localhost:5001/api/jobs')
    jobs = response.json()
    print(jobs) # print the jobs variable to console

    return render_template('index.html', title='title', form = jobs) 

# @app.route('/aboutme', method=['GET', 'POST'])
# def aboutme():
#     return render_template('aboutme.html', title='aboutme')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        response = requests.post('http://localhost:5001/api/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            flash('Login successful!')
            return redirect('/')
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_type= form.user_type.data
        response = requests.post('http://localhost:5001/api/register', json={'username': username, 'password': password, 'user_type': user_type})
        if response.status_code == 201:
            flash('Registration successful! Please log in.')
            return redirect('/login')
        else:
            flash('Username already taken.')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))



# # # Define the user loader function for Flask-Login
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', title='profile')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
