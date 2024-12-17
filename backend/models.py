
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    flag = db.Column(db.Boolean, default=False, nullable=False)  # Default value is False
    approve = db.Column(db.Boolean, default=False, nullable=False)  # Default value is False
    last_visited = db.Column(db.DateTime)
    gmail = db.Column(db.String(100))

    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    influencer_signups = db.relationship('InfluencerSignup', backref='user', lazy=True)
    sponsor_signups = db.relationship('SponsorSignup', backref='user', lazy=True)
    Request_for_sponsor = db.relationship('request_for_sponsor', backref='user', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # Values could be 'public' or 'private'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class InfluencerSignup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class SponsorSignup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(250), nullable=False)
    industry = db.Column(db.String(250), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class request_for_sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    #this  user_id means the influensor details who have requsted 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    status = db.Column(db.String(20), nullable=False, default='Pending')
    #this is a user_id of the campain who have created
    camp_user_id = db.Column(db.Integer)



class AdRequest(db.Model):

    __tablename__ = 'adrequest'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer,  nullable=False)
    # this  stores the id of that sponsor who that created that campaign
    the_user_who_have_created_campaign = db.Column(db.Integer,  nullable=False)
    influencer_id = db.Column(db.Integer,  nullable=False)
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=False)
    request_date =db.Column(db.DateTime, default=datetime.utcnow) 
    status = db.Column(db.String(20), nullable=False, default="pending")
    # make a status  here if request get comform by sponsor 
    # then status is  conform if request is pending then status is pending else 
    # rejactged then initally status is pending 


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campain_id = db.Column(db.Integer, nullable=False)
    #the person who have created campaign
    sender_id = db.Column(db.Integer, nullable=False)
    # the imflencer who have been requested
    receiver_id = db.Column(db.Integer, nullable=False)
    sender_role = db.Column(db.String(50), nullable=False)  # "sponsor" or "influencer"
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="pending")


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campain_id = db.Column(db.Integer, nullable=False)
    # the imfluecer who have been requested
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    # receiver_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    request_date =db.Column(db.DateTime, default=datetime.utcnow) 





    