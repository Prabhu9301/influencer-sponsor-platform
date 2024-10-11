from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from main import app
from application.models import *
from functools import wraps
from datetime import datetime

def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapper

# Landing Page
@app.route('/')
def index():
    if 'user' in session:
        if session['usertype'] == 'admin':
            return redirect(url_for('info'))
        elif session['usertype'] == 'sponsor':
            return redirect(url_for('home'))
        else:
            return redirect(url_for('profile'))
    return render_template('index.html')

# Authentication
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

        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        if password != user.password:
            flash('Incorrect Password')
            return redirect(url_for('login'))

        if user.is_flagged:
           flash('Your account has been flagged. Please contact admin')
           return redirect(url_for('index'))
        
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
        flash('Registered Succesfully. Login to continue')
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
        flash('Registered Succesfully. Login to continue')
        return redirect(url_for('login'))
        
app.register_blueprint(registration)

# Admin Routes
@app.route('/info')
@auth_required
def info():
    flags=Flags.query.all()

    return render_template('info.html', campaigns=Campaigns.query.filter_by(is_flagged=False).all(), flags=flags)

@app.route('/flag_campaign', methods=['POST'])
@auth_required
def flagCampaign():
    campaign_id = request.form.get('campaign_id')
    campaign = Campaigns.query.filter_by(campaign_id=campaign_id).first()

    flag = Flags(flagged_entity=campaign_id, name=campaign.title, entity_type='campaign', status='pending')
    db.session.add(flag)

    campaign = Campaigns.query.filter_by(campaign_id=campaign_id).first()
    if campaign:
        campaign.is_flagged = True

    db.session.commit()
    flash('Campaign flagged')
    return redirect(url_for('info'))

@app.route('/flag_user', methods=['POST'])
@auth_required
def flagUser():
    influencer_id = request.form.get('influencer_id')
    influencer = Influencers.query.filter_by(influencer_id=influencer_id).first()

    flag = Flags(flagged_entity=influencer.user_id, name=influencer.name, entity_type='influencer', status='pending')
    db.session.add(flag)
    
    user = Users.query.filter_by(user_id=influencer.user_id).first()
    if user:
        user.is_flagged = True
    influencer = Influencers.query.filter_by(influencer_id=influencer_id).first()
    if influencer:
        influencer.is_flagged = True

    db.session.commit()
    flash('User flagged')
    return redirect(url_for('info'))        

@app.route('/statistics')
@auth_required
def stats():
    # Active and flagged users
    active_users = Users.query.filter_by(is_flagged=False).count()
    flagged_users = Users.query.filter_by(is_flagged=True).count()
    
    # Active and flagged influencers
    active_influencers = Influencers.query.filter_by(is_flagged=False).count()
    flagged_influencers = Influencers.query.filter_by(is_flagged=True).count()
    
    # Sponsors
    total_sponsors = Sponsors.query.count()
    
    # Public and private campaigns
    public_campaigns = Campaigns.query.filter_by(visibility='public').count()
    private_campaigns = Campaigns.query.filter_by(visibility='private').count()
    flagged_campaigns = Campaigns.query.filter_by(is_flagged=True).count()
    
    # Ad requests by status
    ad_requests_status = {
        'pending': adRequests.query.filter_by(status='pending').count(),
        'accepted': adRequests.query.filter_by(status='accepted').count(),
        'rejected': adRequests.query.filter_by(status='rejected').count(),
    }

    return render_template('stats.html', 
                           active_users=active_users, 
                           flagged_users=flagged_users,
                           active_influencers=active_influencers,
                           flagged_influencers=flagged_influencers,
                           total_sponsors=total_sponsors,
                           public_campaigns=public_campaigns, 
                           private_campaigns=private_campaigns, 
                           flagged_campaigns=flagged_campaigns, 
                           ad_requests_status=ad_requests_status)

# Sponsor Routes
@app.route('/home', methods=['GET','POST'])
@auth_required
def home():
    user_id = Users.query.filter_by(username=session['user']).first().user_id
    sponsor = Sponsors.query.filter_by(user_id=user_id).first()
    
    campaigns = Campaigns.query.filter_by(sponsor_id=Sponsors.query.filter_by(user_id=user_id).first().sponsor_id,is_flagged=False).all()

    results = db.session.query(Campaigns, adRequests).join(adRequests, Campaigns.campaign_id == adRequests.campaign_id).filter(Campaigns.sponsor_id == sponsor.sponsor_id,Campaigns.is_flagged==False).all()
    
    responses = [{'campaign': campaign, 'request': request, 'influencer': Influencers.query.filter_by(influencer_id=request.influencer_id,is_flagged=False).first().name} for campaign, request in results]

    if request.method == 'GET':
        return render_template('home.html', campaigns=campaigns, responses=responses, username=sponsor.name)

@app.route('/campaigns', methods=['GET','POST'])
@auth_required
def campaigns():
    if request.method == 'GET':
        campaigns = Campaigns.query.filter_by(sponsor_id=Sponsors.query.filter_by(user_id=Users.query.filter_by(username=session['user']).first().user_id).first().sponsor_id,is_flagged=False).all()
        return render_template('campaigns.html', campaigns=campaigns)
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        goals = request.form['goals']
        budget = request.form['budget']
        category = request.form['category']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        visibility = request.form.get('visibility', 'public')

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if visibility not in ['public', 'private']:
            visibility = 'public'
        
        user_id = Users.query.filter_by(username=session['user']).first().user_id
        sponsor_id = Sponsors.query.filter_by(user_id=user_id).first().sponsor_id

        new_campaign = Campaigns(sponsor_id=sponsor_id, title=title, description=description, 
                                 goals=goals, budget=budget, category=category, 
                                 start_date=start_date, end_date=end_date, visibility=visibility
                                )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully')
        return redirect(url_for('campaigns'))
    return render_template('campaigns.html', campaigns=campaigns)

@app.route('/delete_campaign', methods=['POST'])
def delete_campaign():
    campaign_id = request.form.get('campaign_id')
    campaign = Campaigns.query.get(campaign_id)
    if not campaign:
        flash('Campaign not found')
        return redirect(url_for('campaigns'))
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully')
    return redirect(url_for('campaigns'))

@app.route('/campaigns/<int:campaign_id>/edit', methods=['GET','POST'])
@auth_required
def edit_campaign(campaign_id):
    if request.method == 'GET':
        return render_template('edit.html', campaign=Campaigns.query.get(campaign_id))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        goals = request.form['goals']
        budget = request.form['budget']
        category = request.form['category']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        visibility = request.form.get('visibility')

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        campaign = Campaigns.query.get(campaign_id)
        if not campaign:
            flash('Campaign not found')
            return redirect(url_for('campaigns'))
        campaign.title = title
        campaign.description = description
        campaign.goals = goals
        campaign.budget = budget
        campaign.category = category
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.visibility = visibility
        db.session.commit()
        flash('Campaign updated successfully')
    
    return redirect(url_for('campaigns'))

@app.route('/send_request', methods=['POST'])
@auth_required
def send_request():

    influencer_id = request.form.get('influencer_id')
    campaign_id = request.form.get('campaign_id')
    message = request.form.get('message')
    new_request = adRequests(influencer_id=influencer_id, campaign_id=campaign_id, message=message)
    db.session.add(new_request)
    db.session.commit()
    flash('Request sent successfully')
    return redirect(url_for('home'))

# Influencer Routes
@app.route('/profile', methods=['GET','POST'])
@auth_required
def profile():
    user_id = Users.query.filter_by(username=session['user']).first().user_id
    influencer_id = Influencers.query.filter_by(user_id=user_id).first().influencer_id
    profile = Influencers.query.filter_by(influencer_id=influencer_id).first()
    
    results = db.session.query(Campaigns, adRequests).join(adRequests, Campaigns.campaign_id == adRequests.campaign_id).filter(adRequests.influencer_id == influencer_id).all()
    
    campaigns = [{'campaign': campaign, 'request': request} for campaign, request in results]
    
    if request.method == 'GET':
        return render_template('profile.html', campaigns=campaigns, profile=profile)

    if request.method == 'POST':        
        status = request.form.get('action')
        campaign_id = request.form.get('campaign_id')

        campaign = adRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()

        if campaign:
            if status == 'accept':
                campaign.status = 'accepted'
            elif status == 'reject':
                campaign.status = 'rejected'
            db.session.commit()
    
    return redirect(url_for('profile'))

@app.route('/notifications')
@auth_required
def notifications():
    user_id = Users.query.filter_by(username=session['user']).first().user_id
    influencer_id = Influencers.query.filter_by(user_id=user_id).first().influencer_id
    
    results = db.session.query(Campaigns, adRequests).join(adRequests, Campaigns.campaign_id == adRequests.campaign_id).filter(adRequests.influencer_id == influencer_id,Campaigns.is_flagged==False).all()
    
    campaigns = [{'campaign': campaign, 'request': request, 'name': Influencers.query.filter_by(influencer_id=request.influencer_id).first().name} for campaign, request in results]
    
    return render_template('notifications.html', campaigns=campaigns)

# Common Explore Route
@app.route('/explore')
@auth_required
def explore():

    campaigns=Campaigns.query.filter_by(is_flagged=False).all()
    influencers=Influencers.query.filter_by(is_flagged=False).all()

    if session['usertype'] == 'admin':
        return render_template('explore.html', campaigns=campaigns, influencers=influencers)

    if session['usertype'] == 'sponsor':
        user_id = Users.query.filter_by(username=session['user']).first().user_id
        sponsor_id = Sponsors.query.filter_by(user_id=user_id).first().sponsor_id

        sponsor_campaign = Campaigns.query.filter_by(sponsor_id=sponsor_id, is_flagged=False).all()
        print(sponsor_campaign)
        return render_template('explore.html', influencers=influencers, sponsor_campaign=sponsor_campaign)
    
    if session['usertype'] == 'influencer':
        public=Campaigns.query.filter_by(visibility='public', is_flagged=False).all()

        return render_template('explore.html', public=public)