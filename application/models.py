from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    usertype = db.Column(db.Enum('admin','influencer','sponsor'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)

class Influencers(db.Model):
    __tablename__ = 'influencers'
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.String)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String)
    
    ad_requests = db.relationship('adRequests', backref='influencers')

class Sponsors(db.Model):
    __tablename__ = 'sponsors'
    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    brand_name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Numeric, nullable=False)

    campaigns = db.relationship('Campaigns', backref='sponsors')

class Campaigns(db.Model):
    __tablename__ = 'campaigns'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.sponsor_id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    budget = db.Column(db.Numeric)
    category = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    visibility = db.Column(db.Enum('public','private'))
    is_flagged = db.Column(db.Boolean, default=False)

    ad_requests = db.relationship('adRequests', backref='campaigns')

class adRequests(db.Model):
    __tablename__ = 'ad_requests'
    ad_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.campaign_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.influencer_id'))
    messages = db.Column(db.String)
    requirements = db.Column(db.String)
    payment_amount = db.Column(db.Numeric)
    status = db.Column(db.Enum('pending','accepted','rejected'), default='pending')

    contracts = db.relationship('Contracts', backref='ad_requests')

class Contracts(db.Model):
    __tablename__ = 'contracts'
    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_requests.ad_request_id'))
    agreement_terms = db.Column(db.String)
    status = db.Column(db.Enum('pending','active','completed','cancelled'))

class Payments(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.contract_id'))
    amount = db.Column(db.Numeric)
    payment_date = db.Column(db.Date)

class Flags(db.Model):
    __tablename__ = 'flags'
    flag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flagged_entity = db.Column(db.Integer, db.ForeignKey('users.user_id'), db.ForeignKey('campaigns.campaign_id'), nullable=False)
    entity_type = db.Column(db.Enum('user','campaign'))
    reason = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum('pending','resolved'))