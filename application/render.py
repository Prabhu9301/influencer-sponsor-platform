from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from main import app
from application.models import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Incorrect Username or Password')
            return redirect(url_for('login'))
        
        user = Users.query.filter_by(username=username).first()
        print(user, username, password)
        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        if password != user.password:
            flash('Incorrect Password')
            return redirect(url_for('login'))
        
        session['user'] = user.username
        session['usertype'] = user.usertype

        flash('Login Successful')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('usertype', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('auth/register.html')

registration = Blueprint('registration', __name__, url_prefix='/register')

@registration.route('/influencer', methods=['GET','POST'])
def register_influencer():
    if request.method == 'GET':
        return render_template('auth/register_influencer.html')
    
    if request.method == 'POST':
        # print("Influencer registration POST request received")
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        category = request.form['category']
        niche = request.form['niche']

        if not username or not password:
            flash('Please enter username and password')
            return redirect(url_for('registration.register_influencer'))
        
        # if len(password) < 8:
        #     flash('Password must be at least 8 characters')
        #     return redirect(url_for('registration.register_influencer'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('registration.register_influencer'))
        
        user = Users.query.filter_by(username=username).first()
        if user:
            flash('User already exists')
            return redirect(url_for('registration.register_influencer'))
        
        new_user = Users(username=username, password=password, usertype='influencer')
        db.session.add(new_user)
        db.session.commit()
        new_influencer = Influencers(user_id=new_user.user_id, name=name, category=category, niche=niche)
        db.session.add(new_influencer)
        db.session.commit()
        flash('Registered Succesfully. You can now login.')
        return redirect(url_for('login'))
        
@registration.route('/sponsor', methods=['GET','POST'])
def register_sponsor():
    if request.method == 'GET':
        return render_template('auth/register_sponsor.html')
    
    if request.method == 'POST':
        # print("Sponsor registration POST request received")
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        brand_name = request.form['brand_name']
        industry = request.form['industry']
        budget = request.form['budget']

        if not username or not password:
            flash('Please enter username and password')
            return redirect(url_for('registration.register_sponsor'))
        
        # if len(password) < 8:
        #     flash('Password must be at least 8 characters')
        #     return redirect(url_for('registration.register_sponsor'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('registration.register_sponsor'))

        user = Users.query.filter_by(username=username).first()
        if user:
            flash('User already exists')
            return redirect(url_for('registration.register_sponsor'))
        
        new_user = Users(username=username, password=password, usertype='sponsor')
        db.session.add(new_user)
        db.session.commit()
        new_sponsor = Sponsors(user_id=new_user.user_id, name=name, brand_name=brand_name, industry=industry, budget=budget)
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Registered Succesfully. You can now login.')
        return redirect(url_for('login'))
        
app.register_blueprint(registration)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/campaigns')
def campaigns():
    return render_template('campaigns.html')

@app.route('/add_campaign')
def add_campaign():
    return render_template('add_campaign.html')