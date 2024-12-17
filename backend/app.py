from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
from datetime import timedelta
from models import db, AdRequest, SponsorSignup, Users, Campaign, InfluencerSignup,Message,  Status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import logging
from sqlalchemy.orm import aliased


app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YOUR_JWT_SECRET_KEY'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=10)

# Initialize extensions

CORS(app)
jwt = JWTManager(app)

db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Function to create tables if they don't exist

def create_tables():
    with app.app_context():
        db.create_all()
        existing_user = Users.query.filter_by(username='owner').first()
        if not existing_user:
            # Create the admin user
            hashed_password = generate_password_hash('123', method='pbkdf2:sha256', salt_length=16)
            admin_user = Users(username='owner', password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()


create_tables()  # Create tables when the application starts

#--------------code for download file ----------------------------------------------------------------------\
import os
import csv
import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from celery import Celery
from models import Campaign, Users  # Make sure to import all the relevant models



# Celery and Flask Configuration
app.config.update(
    broker_url="redis://localhost:6379/0",  # Updated key
    result_backend="redis://localhost:6379/0",  # Updated key
    SECRET_KEY="your_secret_key",
)

# Initialize JWT
jwt = JWTManager(app)

# Initialize Celery
celery = Celery(
    app.import_name,
    broker=app.config["broker_url"],
    backend=app.config["result_backend"],
)
celery.conf.update(app.config)

# Logger
logger = logging.getLogger(__name__)

export_dir = 'static/exports'


# Celery Task to Generate CSV
import os
import csv
import logging
from flask import Flask, jsonify
from celery import Celery


# Configure logging
logger = logging.getLogger(__name__)

# Make sure to adjust these paths for your application
 # Make sure this directory exists and is accessible

@celery.task(bind=True)
def generate_campaign_csv(self, sponsor_id):
    try:
        # Query campaigns based on sponsor_id (assuming 'sponsor_id' is passed correctly)
        campaigns = Campaign.query.filter_by(user_id=sponsor_id).all()  # Make sure user_id matches your database field
        if not campaigns:
            raise ValueError(f"No campaigns found for sponsor_id {sponsor_id}")

        # Create CSV data (ensure it's properly formatted)
        csv_data = []
        for campaign in campaigns:
            # Log the campaign info to check its content
            logger.info(f"Campaign Data: {campaign.id}, {campaign.title}, {campaign.description}")
            csv_data.append([
                campaign.id,
                campaign.title,
                campaign.description,
                campaign.niche,
                campaign.start_date.strftime('%Y-%m-%d'),  # Format dates if needed
                campaign.end_date.strftime('%Y-%m-%d'),
                campaign.budget,
                campaign.visibility
            ])

        # Check if the data exists
        if not csv_data:
            raise ValueError(f"No valid campaign data found for sponsor_id {sponsor_id}")

        # Save the CSV file
        csv_file_path = os.path.join(export_dir, f"sponsor_{sponsor_id}_campaigns.csv")
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)  # Ensure directory exists
        
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row
            writer.writerow(["ID", "Title", "Description", "Niche", "Start Date", "End Date", "Budget", "Visibility"])
            # Write data rows
            writer.writerows(csv_data)
        
        logger.info(f"CSV generated successfully for sponsor_id {sponsor_id}, saved to {csv_file_path}")
        return {"file_path": csv_file_path}
    
    except Exception as e:
        # Log and raise any exception
        logger.error(f"Error generating CSV for sponsor_id {sponsor_id}: {str(e)}")
        raise e


# Flask Routes
@app.route("/trigger-export", methods=["POST"])
@jwt_required()
def trigger_export():
    try:
        print("Received export request.")
        
        # Get sponsor ID from the JWT token
        sponsor_id = get_jwt_identity().get("user_id")
        print(f"Sponsor ID from token: {sponsor_id}")

        # Start the Celery task
        task = generate_campaign_csv.delay(sponsor_id)

        print(f"Started Celery task with task ID: {task.id}")

        return jsonify({"status": "success", "task_id": task.id}), 202
    
    except Exception as e:
        print(f"Error triggering export: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/check-task-status/<task_id>", methods=["GET"])
def check_task_status(task_id):
    try:
        print(f"Checking status for task ID: {task_id}")
        
        # Check the status of the task
        task = celery.AsyncResult(task_id)
        print(f"Task state: {task.state}")

        if task.state == "SUCCESS":
            print(f"Task completed successfully. File path: {task.result['file_path']}")
            return jsonify({"status": "completed", "file_path": task.result["file_path"]})
        elif task.state == "FAILURE":
            # Improved error handling to print the full error
            print(f"Task failed. Error message: {task.info}")
            return jsonify({"status": "error", "message": str(task.info)}), 500
        else:
            print(f"Task is still pending. Current state: {task.state}")
            return jsonify({"status": "pending"}), 202
    
    except Exception as e:
        print(f"Error checking task status for task_id {task_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500




#--------------------------------------------------------------------------------------------------------------------------

@app.route('/trigger-reminder', methods=['POST'])
def trigger_reminder():
    try:
        # Trigger the Celery task
        send_reminders_task.delay()

        return jsonify({"message": "Reminder task triggered successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --------------------------------------------------------------------------------------


# Initialize Flask app
from celery import Celery
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import db, celery  # Assuming celery and db are already initialized


# Initialize Flask app
app.config.update(
    broker_connection_retry_on_startup=True  ,# Set this to True
    SQLALCHEMY_DATABASE_URI='sqlite:///your_db_path.db',  # Example database URI
    SECRET_KEY='your_secret_key',  # Ensure this is set for security
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)

# Initialize SQLAlchemy


# Initialize Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)


    # Custom task base to use Flask app context with Celery
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# Function to get influencers with pending ad requests or inactivity
def get_influencers_to_notify():
    print("[DEBUG] Querying influencers to notify...")
    try:
        # Assuming the 'Users' model has a relationship to 'Status' for the ad request status
        influencers = db.session.query(Users).join(Status).filter(
            Status.status == 'pending'  # Filter for pending ad requests
        ).all()
        print(f"[DEBUG] Found {len(influencers)} influencers to notify.")
        return influencers
    except Exception as e:
        print(f"[ERROR] Error querying influencers: {e}")
        return []



def get_pending_request_count(influencer_id):
    try:
        count = (
            db.session.query(Status)
            .filter(Status.receiver_id == influencer_id, Status.status == 'pending')
            .count()
        )
        return count
    except Exception as e:
        print(f"[ERROR] Error fetching pending requests count: {e}")
        return 0



# Function to send email reminders
def send_reminder_email(influencer, pending_count):
    print(influencer)
    print(f"[DEBUG] Preparing email for {influencer.username} ({influencer.gmail})...")

    sender_email = "22f2000226@ds.study.iitm.ac.in"
    receiver_email = influencer.gmail

    # Use the 16-character app password generated from Google
    password = "lprp pdix jnqc naop" 

    subject = "Reminder: Pending Ad Requests or Inactivity"
    body = (
        f"Hello {influencer.username},\n\n"
        f"You have {pending_count} pending ad requests. Please log in to review them.\n\n"
        "Best regards,\nYour App Team"
    )

    

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f"[DEBUG] Email sent to {influencer.username} at {influencer.gmail}")
    except Exception as e:
        print(f"[ERROR] Error sending email to {influencer.username}: {e}")



# Celery task to send reminders
@celery.task
def send_reminders_task():
    print("[DEBUG] Task send_reminders_task started.")
    influencers_to_notify = get_influencers_to_notify()

    if not influencers_to_notify:
        print("[DEBUG] No influencers to notify.")
        return  # Exit early if no influencers to notify

    for influencer in influencers_to_notify:
        pending_count = get_pending_request_count(influencer.id)
        send_reminder_email(influencer, pending_count)


    print("[DEBUG] Task send_reminders_task completed.")

# Celery Beat Configuration for periodic task scheduling
from celery.schedules import crontab

celery.conf.beat_schedule = {
    # Daily reminder at 6:00 PM IST
    'send-daily-evening-reminders': {
        'task': 'send_reminders_task',
        'schedule': crontab(hour=18, minute=0),  # IST Time
    },
}
celery.conf.timezone = 'Asia/Kolkata'  # Set timezone to IST

from app import send_reminders_task



#-----------------------------------------------------------------------------------




def get_sponsor_campaign_report():
    """Fetch campaigns and their request statuses for each sponsor."""
    try:
        # Fetch all sponsors
        sponsors = Users.query.filter_by(role="sponsor").all()
        report_data = []

        for sponsor in sponsors:
            campaigns = Campaign.query.filter_by(user_id=sponsor.id).all()
            campaign_details = []

            for campaign in campaigns:
                # Fetch total and accepted requests
                total_requests = Status.query.filter_by(campain_id=campaign.id).count()
                accepted_requests = Status.query.filter_by(
                    campain_id=campaign.id, status="accepted"
                ).count()

                campaign_details.append({
                    "title": campaign.title,
                    "total_requests": total_requests,
                    "accepted_requests": accepted_requests
                })

            report_data.append({
                "sponsor_name": sponsor.username,
                "email": sponsor.gmail,  # Assuming 'gmail' holds the email address
                "campaigns": campaign_details
            })

        return report_data
    except Exception as e:
        print(f"[ERROR] Error generating report data: {e}")
        return []


def send_email(to_email, subject, body, from_email, from_password, smtp_server, smtp_port):
    """Function to send email using smtplib."""
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())

        print(f"Email sent to {to_email} successfully.")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


@celery.task
def send_sponsor_reports():
    """Generate and send monthly reports to sponsors."""
    print("[DEBUG] Task send_sponsor_reports started.")
    sponsors_data = get_sponsor_campaign_report()

    if not sponsors_data:
        print("[DEBUG] No sponsors to notify.")
        return

    # Email configuration (update these values)
    from_email ="22f2000226@ds.study.iitm.ac.in" # Sender email
    from_password = "lprp pdix jnqc naop"  # Sender email password or app password
    smtp_server = "smtp.gmail.com"  # SMTP server (for Gmail)
    smtp_port = 587  # SMTP port (for Gmail)

    for sponsor in sponsors_data:
        try:
            # Render email content
            html_content = render_template(
                'sponsor_report_email.html',
                sponsor_name=sponsor["sponsor_name"],
                campaigns=sponsor["campaigns"]
            )

            # Send email using the send_email function
            send_email(
                to_email=sponsor["email"],
                subject="Monthly Campaign Report",
                body=html_content,
                from_email=from_email,
                from_password=from_password,
                smtp_server=smtp_server,
                smtp_port=smtp_port
            )   

            print(f"[DEBUG] Report sent to {sponsor['sponsor_name']} at {sponsor['email']}")

        except Exception as e:
            print(f"[ERROR] Error sending email to {sponsor['sponsor_name']}: {e}")

    print("[DEBUG] Task send_sponsor_reports completed.")


celery.conf.beat_schedule.update({
    'send-monthly-sponsor-reports': {
        'task': 'send_sponsor_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # First day of every month at 9:00 AM
    },
})




from app import send_sponsor_reports


@app.route('/send-monthly-report', methods=['POST'])
def trigger_monthly_report():
    """Trigger the send_sponsor_reports task."""
    try:
        send_sponsor_reports.delay()  # Asynchronous task execution
        return jsonify({"message": "Monthly report generation task has been started."}), 200
    except Exception as e:
        print(f"[ERROR] Failed to start monthly report task: {e}")
        return jsonify({"error": "Failed to start monthly report task."}), 500



#---------------------------------------------------------------------------------------------

@app.route('/userss', methods=['GET'])
def get_users():
    users = Users.query.filter(Users.role != 'admin').all()
    users_list = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "flag": user.flag
        }
        for user in users
    ]
    return jsonify(users_list), 200



@app.route('/api/users/<int:user_id>', methods=['PUT'])
def toggle_user_flag(user_id):
    user = Users.query.get_or_404(user_id)
    data = request.json

    if 'flag' not in data:
        return jsonify({"error": "Missing 'flag' field in request body"}), 400

    user.flag = data['flag']
    db.session.commit()

    return jsonify({"message": f"User flag status updated to {user.flag}"}), 200



@app.route('/sponsors', methods=['GET'])
def get_sponsors():
    sponsors = Users.query.filter_by(role='sponsor').all()  # Assuming "sponsor" is the role name
    sponsors_list = [
        {
            "id": sponsor.id,
            "username": sponsor.username,
            "role": sponsor.role,
            "company_name": sponsor.sponsor_signups[0].company_name if sponsor.sponsor_signups else "",
            "industry": sponsor.sponsor_signups[0].industry if sponsor.sponsor_signups else "",
            "budget": sponsor.sponsor_signups[0].budget if sponsor.sponsor_signups else 0,
            "approve": sponsor.approve,
        }
        for sponsor in sponsors
    ]
    return jsonify(sponsors_list), 200


# Route to toggle approval status
@app.route('/api/sponsors/<int:sponsor_id>', methods=['PUT'])
def update_sponsor_approval(sponsor_id):
    sponsor = Users.query.get_or_404(sponsor_id)
    data = request.json

    if 'approve' not in data:
        return jsonify({"error": "Missing 'approve' field in request body"}), 400

    sponsor.approve = data['approve']
    db.session.commit()

    return jsonify({"message": "Sponsor approval status updated", "approve": sponsor.approve}), 200



@app.route('/', methods=['POST'])
def login():
    print("Login accessed")
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400

    username = data.get('username')
    password = data.get('password')

    # Validate input data
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Query user by username
    user = Users.query.filter_by(username=username).first()

    # Check if the user exists
    if not user:
        return jsonify({"message": "Account not found. Please sign up."}), 404

    # Check if the password is correct
    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Check if the user's account is flagged
    if user.flag:
        return jsonify({"message": "User is flagged by admin, access restricted."}), 403

    # Check if the user is a sponsor and approval status
    if user.role == 'sponsor' and not user.approve:
        return jsonify({"message": "Your account is under verification. Please contact support for more information."}), 403

    # Generate an access token for the user
    access_token = create_access_token(identity={'user_id': user.id, 'username': user.username, 'role': user.role})
    print(user.role)
    return jsonify({"message": "Login successful", "access_token": access_token, "role": user.role}), 200



from flask_caching import Cache

# Initialize cache with a default timeout of 1 minute
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 60})


@app.route('/api/user-stats', methods=['GET'])
@cache.cached(timeout=60) 
def user_stats():
    influencer_count = Users.query.filter_by(role='influencer').count()
    sponsor_count = Users.query.filter_by(role='sponsor').count()
    
    # Count of public and private campaigns
    public_campaign_count = Campaign.query.filter_by(visibility='public').count()
    private_campaign_count = Campaign.query.filter_by(visibility='private').count()

    influencers_accepted_adreqeust = Status.query.filter_by(status='accepted').count()
    influencers_rejected_adreqeust = Status.query.filter_by(status='rejected').count()
    influencers_pending_adreqeust = Status.query.filter_by(status='pending').count()

    sponsor_accepted_adreqeust = AdRequest.query.filter_by(status='Accepted').count()
    sponsor_rejected_adreqeust = AdRequest.query.filter_by(status='Rejected').count()

    return jsonify({
        'influencers': influencer_count,
        'sponsors': sponsor_count,
        'public_campaigns': public_campaign_count,
        'private_campaigns': private_campaign_count,
        'influencers_accepted_adreqeust':influencers_accepted_adreqeust,
        'influencers_rejected_adreqeust':influencers_rejected_adreqeust,
        'sponsor_accepted_adreqeust':sponsor_accepted_adreqeust,
        'sponsor_rejected_adreqeust':sponsor_rejected_adreqeust,



    })



@app.route('/update-influencer-profile', methods=['PUT'])
@jwt_required()
def update_influencer_profile():
    try:
        user_id = get_jwt_identity().get('user_id')
        data = request.get_json()

        # Extract updated fields
        username = data.get('username')
        category = data.get('category')
        niche = data.get('niche')
        reach = data.get('reach')

        # Update user table
        user = Users.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        user.username = username

        # Update influencer profile
        influencer = InfluencerSignup.query.filter_by(user_id=user_id).first()
        if not influencer:
            return jsonify({"message": "Influencer profile not found"}), 404
        influencer.category = category
        influencer.niche = niche
        influencer.reach = reach

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"message": "Failed to update profile"}), 500



@app.route('/create_status', methods=['POST'])
@jwt_required()
def create_status():
    try:
        # Get the JSON payload from the frontend
        data = request.get_json()
        campaign_id = data.get('campaign_id')
        receiver_id = data.get('receiver_id')

        # Validate input
        if not campaign_id or not receiver_id:
            return jsonify({'error': 'Campaign ID and Receiver ID are required.'}), 400

        # Check if the entry already exists
        existing_status = Status.query.filter_by(campain_id=campaign_id, receiver_id=receiver_id).first()
        if existing_status:
            return jsonify({'message': 'Status already exists for this campaign and influencer.', 'status': existing_status.status}), 200

        # Create a new status entry
        new_status = Status(
            campain_id=campaign_id,
            receiver_id=receiver_id,
            status="pending"
        )
        db.session.add(new_status)
        db.session.commit()

        return jsonify({'message': 'Status created successfully.', 'status_id': new_status.id}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred.', 'details': str(e)}), 500

    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500







@app.route('/update_request_status', methods=['POST'])
@jwt_required()  # Protect the route with JWT authentication
def update_request_status():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity().get('user_id')

        if not user_id:
            return jsonify({'error': 'Unauthorized access. Invalid user.'}), 401

        # Parse the JSON payload from the request
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid request payload. JSON data required.'}), 400

        # Extract necessary fields
        campaign_id = data.get('campaign_id')
        influencer_id = user_id  # The current user is the influencer
        status = data.get('status')  # Expected values: "accepted" or "rejected"

        # Validate input
        if not campaign_id or not influencer_id or status not in ['accepted', 'rejected']:
            return jsonify({'error': 'Invalid data provided. Check campaign ID, influencer ID, and status.'}), 400

        # Create or update the status record
        existing_status = Status.query.filter_by(campain_id=campaign_id, receiver_id=influencer_id).first()

        if existing_status:
            existing_status.status = status  # Update the existing record
        else:
            new_status = Status(campain_id=campaign_id, receiver_id=influencer_id, status=status)
            db.session.add(new_status)  # Add new record if not exists

        db.session.commit()  # Commit the changes to the database

        # Return a response with the updated campaign and status
        return jsonify({
            'message': f'Status for campaign {campaign_id} has been updated to {status} successfully.',
            'updated_campaign_id': campaign_id,
            'updated_status': status
        }), 200

    except SQLAlchemyError as e:  # Handle database-related errors
        db.session.rollback()  # Roll back any changes on error
        print(str(e))
        return jsonify({'error': 'Database error occurred.', 'details': str(e)}), 500

    except Exception as e:  # Catch all other exceptions
        print({'error': 'An unexpected error occurred.', 'details': str(e)})
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500



@app.route('/messages/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_messages_other(campaign_id):
    try:
        print('get_messages_other')
        current_user = get_jwt_identity()
        influencer_id = current_user.get('user_id')

        messages = Message.query.filter_by(
            receiver_id=influencer_id,
            campain_id=campaign_id
        ).order_by(Message.timestamp).all()

        messages_data = [
            {
                "id": msg.id,
                "campaign_id": msg.campain_id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "sender_role": msg.sender_role,
                "text": msg.text,
                "timestamp": msg.timestamp.isoformat(),
                "status": msg.status
            }
            for msg in messages
        ]

        return jsonify(messages_data), 200
    except Exception as e:
        print({"error": str(e)})
        return jsonify({"error": str(e)}), 500


@app.route('/messages_send', methods=['POST'])
@jwt_required()
def send_message_others():
    try:
        print("message send")
        current_user = get_jwt_identity()
        receiver_id = current_user.get('user_id')

        data = request.json
        campaign_id = data.get('campaign_id')
        text = data.get('text')

        # Fetch the campaign to find the sender_id
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"error": "Campaign not found"}), 404

        sender_id = campaign.user_id

        # Create the new message
        new_message = Message(
            campain_id=campaign_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            sender_role="influencer",  # Adjust sender role dynamically if needed
            text=text,
            timestamp=datetime.utcnow(),
            status="pending"
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        print(({"error": str(e)}))
        return jsonify({"error": str(e)}), 500



@app.route('/influencer/campaigns', methods=['GET'])
@jwt_required()
def get_influencer_campaigns():
    try:
        print("Starting to fetch campaigns for the influencer.")
        influencer_id = get_jwt_identity().get('user_id')
        print(f"Influencer ID: {influencer_id}")

        if not influencer_id:
            raise ValueError("Invalid or missing influencer ID in the token.")

        # Query campaigns by status
        pending_campaigns = (
            db.session.query(Campaign)
            .join(Status, Status.campain_id == Campaign.id)
            .filter(
                Status.receiver_id == influencer_id,
                Status.status == 'pending',
                Campaign.visibility == 'public'
            )
            .all()
        )

        accepted_campaigns = (
            db.session.query(Campaign)
            .join(Status, Status.campain_id == Campaign.id)
            .filter(
                Status.receiver_id == influencer_id,
                Status.status == 'accepted',
                Campaign.visibility == 'public'
            )
            .all()
        )

        rejected_campaigns = (
            db.session.query(Campaign)
            .join(Status, Status.campain_id == Campaign.id)
            .filter(
                Status.receiver_id == influencer_id,
                Status.status == 'rejected',
                Campaign.visibility == 'public'
            )
            .all()
        )

        print(f"Pending: {len(pending_campaigns)}, Accepted: {len(accepted_campaigns)}, Rejected: {len(rejected_campaigns)}")

        return jsonify({
            'pending': [{
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'niche': campaign.niche,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': campaign.budget,
                'visibility': campaign.visibility
            } for campaign in pending_campaigns],
            'accepted': [{
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'niche': campaign.niche,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': campaign.budget,
                'visibility': campaign.visibility
            } for campaign in accepted_campaigns],
            'rejected': [{
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'niche': campaign.niche,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': campaign.budget,
                'visibility': campaign.visibility
            } for campaign in rejected_campaigns]
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while fetching campaigns', 'details': str(e)}), 500





# add request handling route 



@app.route('/adrequest', methods=['POST'])
@jwt_required()
def create_ad_request():
    print("accessed")
    try:
        # Extract data from request
        data = request.get_json()
        print(data)
        campaign_id = data.get('campaign_id')
        amount = data.get('amount')
        message = data.get('message')

        # Get influencer ID from JWT identity
        jwt_identity = get_jwt_identity()
        current_user_id = jwt_identity.get('user_id')  # Get user_id from JWT identity payload

        # Fetch the campaign by campaign_id
        campaign = Campaign.query.filter_by(id=campaign_id).first()
        if not campaign:
            return jsonify({"error": "Campaign not found"}), 404


    
        # Create a new AdRequest entry
        print([current_user_id,campaign_id,campaign.user_id, amount , message])

        ad_request = AdRequest(
            campaign_id=campaign_id,
            the_user_who_have_created_campaign=campaign.user_id,  # The ID of the campaign's creator
            influencer_id=current_user_id,  # The influencer's ID from the InfluencerSignup table
            amount=amount,
            message=message
        )
  
        # Add to the database and commit
        db.session.add(ad_request)
        db.session.commit()

        return jsonify({"message": "Request sent successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching all campaigns: {str(e)}")
        return jsonify({"error": "Failed to fetch campaigns", "message": str(e)}), 500




@app.route('/accept-request/<int:campaign_id>', methods=['POST'])
@jwt_required()
def accept_request(campaign_id):
    try:
        print("Attempting to accept request for campaign ID:", campaign_id)
        
        # Find the AdRequest by campaign_id (use filter_by instead of get)
        ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, status='pending').first()

        if not ad_request:
            print(f"AdRequest with campaign_id {campaign_id} not found or already processed")
            return jsonify({"error": "Campaign request not found or already processed"}), 404
        
        # Update the status to 'Accepted'
        ad_request.status = 'Accepted'
        val = ad_request.amount
        
        # Find the related campaign
        campaign = Campaign.query.filter_by(id=campaign_id).first()
        
        if not campaign:
            print(f"Campaign with ID {campaign_id} not found")
            return jsonify({"error": "Campaign not found"}), 404
        
        # Deduct the amount from the campaign's budget
        print(f"Current campaign budget: {campaign.budget}, deducting {val}")
        campaign.budget -= val
        db.session.commit()
        
        print(f"Request accepted successfully. New campaign budget: {campaign.budget}")
        return jsonify({"message": "Request accepted successfully!"}), 200
    except Exception as e:
        # Log detailed error information
        print(f"Error occurred while accepting the request: {str(e)}")
        print("Traceback:", traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "An error occurred while accepting the request"}), 500



@app.route('/reject-request/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def reject_requesttt(campaign_id):
    try:
        print("Attempting to reject request for campaign ID:", campaign_id)
        
        # Find the AdRequest by campaign_id (use filter_by instead of get)
        ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, status='pending').first()

        if not ad_request:
            print(f"AdRequest with campaign_id {campaign_id} not found or already processed")
            return jsonify({"error": "Campaign request not found or already processed"}), 404
        
        # Update the status to 'Rejected'
        ad_request.status = 'Rejected'
        db.session.commit()
        
        print(f"Request for campaign ID {campaign_id} has been rejected successfully")
        return jsonify({"message": "Request rejected successfully!"}), 200
    except Exception as e:
        # Log detailed error information
        print(f"Error occurred while rejecting the request: {str(e)}")
        print("Traceback:", traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "An error occurred while rejecting the request"}), 500



@app.route('/get_messages/<int:influencer_id>', methods=['GET'])
@jwt_required()  # Protect the route with JWT authentication
def get_messages(influencer_id):
    print("Accessed get_message")

    # Get the current user's ID from the JWT token
    user_id = get_jwt_identity().get('user_id')

    # Get the campaign ID from the query parameters
    campaign_id = request.args.get('campaign_id', type=int)
    
    if not campaign_id:
        return jsonify({"error": "Campaign ID is required"}), 400

    # Query messages where the campaign ID matches, and the sender or receiver is the influencer
    messages = Message.query.filter(
        ((Message.receiver_id == influencer_id) | (Message.sender_id == influencer_id)) &
        (Message.campain_id == campaign_id)
    ).order_by(Message.timestamp.asc()).all()

    # Format messages into a list of dictionaries
    messages_data = []
    for message in messages:
        messages_data.append({
            'sender': message.sender_role,  # 'sponsor' or 'influencer'
            'text': message.text,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Format timestamp as string
        })

    return jsonify(messages_data)  # Return the messages as a JSON response


@app.route('/send_message', methods=['POST'])
@jwt_required()
def send_message():
    print("send message")
    data = request.json
    influencer_id = data.get('influencerId')
    message_text = data.get('message')['text']
    campain_id = data.get('ampain_id')

    # Get the current user's ID from the JWT token 
    #it will be the sponsor who have created this campain 
    user_id = get_jwt_identity().get('user_id') 

    sender_role = 'sponsor'

    new_message = Message(
        #sender id mins the name of imfluenver who 
        #who have created this  campign
        sender_id=user_id,
        receiver_id=influencer_id,
        sender_role=sender_role,
        text=message_text,
        timestamp=datetime.utcnow(),
        campain_id = campain_id
    )

    db.session.add(new_message)
    db.session.commit()


    return jsonify({"status": "success", "message": "Message sent successfully"})





@app.route('/search_influencers', methods=['GET'])
def search_influencers():
    query = request.args.get('query', '').lower()
    category = request.args.get('category')
    followers = request.args.get('followers')
    campain_id = request.args.get('campain_id')

    base_query = (
        Users.query
        .join(InfluencerSignup)  # Join with the InfluencerSignup table
        .outerjoin(Status, (Users.id == Status.receiver_id) & (Status.campain_id == campain_id))  # Outer join with Status table
        .filter(Users.role == 'influencer')  # Only influencers
    )

 

    # If a query parameter for username exists, filter by it
    if query:
        base_query = base_query.filter(Users.username.ilike(f"%{query}%"))

    # If category is specified, filter by it
    if category:
        base_query = base_query.filter(InfluencerSignup.category == category)

    # Handle follower range filtering
    if followers:
        if followers == '1k-10k':
            base_query = base_query.filter(InfluencerSignup.reach.between(0, 10000))
        elif followers == '10k-100k':
            base_query = base_query.filter(InfluencerSignup.reach.between(10000, 100000))
        elif followers == '100k-500k':
            base_query = base_query.filter(InfluencerSignup.reach.between(100000, 500000))
        elif followers == '500k+':
            base_query = base_query.filter(InfluencerSignup.reach >= 500000)

    # Fetching all the filtered users
    influencers_pending = []
    influencers_accepted = []
    influencers_rejected = []
    print(base_query.all())
    for user in base_query.all():
        print(user)
        if user.influencer_signups:
            influencer = user.influencer_signups[0]  # Access the first (and presumably only) influencer signup for the user
            
            # Check the status of each influencer's request and categorize accordingly
            status = Status.query.filter_by(receiver_id=user.id, campain_id=campain_id).first()
            
            if status:
                if status.status == 'pending':
                    influencers_pending.append({
                        'id': user.id,
                        'username': user.username,
                        'category': influencer.category,
                        'niche': influencer.niche,
                        'reach': influencer.reach,
                        'role': user.role,
                        'status': status.status
                    })
                elif status.status == 'accepted':
                    influencers_accepted.append({
                        'id': user.id,
                        'username': user.username,
                        'category': influencer.category,
                        'niche': influencer.niche,
                        'reach': influencer.reach,
                        'role': user.role,
                        'status': status.status
                    })
                elif status.status == 'rejected':
                    influencers_rejected.append({
                        'id': user.id,
                        'username': user.username,
                        'category': influencer.category,
                        'niche': influencer.niche,
                        'reach': influencer.reach,
                        'role': user.role,
                        'status': status.status
                    })
            else:
                # If no status exists, treat the influencer as pending by default
                influencers_pending.append({
                    'id': user.id,
                    'username': user.username,
                    'category': influencer.category,
                    'niche': influencer.niche,
                    'reach': influencer.reach,
                    'role': user.role,
                    'status': 'pending'
                })

    print({
        'pending': influencers_pending,
        'accepted': influencers_accepted,
        'rejected': influencers_rejected
    })
    return jsonify({
        'pending': influencers_pending,
        'accepted': influencers_accepted,
        'rejected': influencers_rejected
    })


#----------------------------------------------------------------------------------------------

@app.route('/update-status/<int:campaign_id>', methods=['POST'])
def update_campaign_status(campaign_id):
    # Get the status directly from the JSON body in the request
    status = request.json.get('status')  # Extract status from the JSON body

    if not status:
        return jsonify({"error": "Status is required"}), 400

    # Query the database to find the ad request with the given campaign_id
    ad_request = AdRequest.query.filter_by(campaign_id=campaign_id).first()

    if not ad_request:
        return jsonify({"error": "Campaign not found"}), 404

    # Update the status of the ad request
    ad_request.status = status
    db.session.commit()  # Save changes to the database

    return jsonify({"message": "Status updated successfully"}), 200








@app.route('/reject-request/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def reject_request(campaign_id):
    try:
        # Find the AdRequest by ID
        print("Attempting to reject request for campaign ID:", campaign_id)
        ad_request = AdRequest.query.get(campaign_id)
        
        if not ad_request:
            print(f"AdRequest with campaign_id {campaign_id} not found")
            return jsonify({"error": "Campaign request not found"}), 404
        
        # Update the status to 'Rejected'
        ad_request.status = 'Rejected'
        db.session.commit()
        
        print(f"Request for campaign ID {campaign_id} has been rejected successfully")
        return jsonify({"message": "Request rejected successfully!"}), 200
    except Exception as e:
        # Log detailed error information
        print(f"Error occurred while rejecting the request: {str(e)}")
        print("Traceback:", traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "An error occurred while rejecting the request"}), 500


#------------------------------------------------------------------------------------------------------------


# this route will giev the campain to sponsor taht have 
#requestd by infleuncer 
@app.route('/all-requested-campaigns', methods=['GET'])
@jwt_required()
def get_all_requested_campaigns():
    print("Accessed get all requested campaigns")

    user_id = get_jwt_identity().get('user_id')  # Get sponsor ID from the JWT token

    try:
        # Query the Campaign, AdRequest, and Influencer tables
        ad_requests = (
            db.session.query(Campaign, AdRequest, Users)
            .join(AdRequest, Campaign.id == AdRequest.campaign_id)
            .join(Users, Users.id == AdRequest.influencer_id)
            .filter(Campaign.user_id == user_id)  # Filter by sponsor (user) ID
            .all()
        )   

        # Convert ad requests to JSON format
        campaigns_data = [
            {
                "id": campaign.id,
                "title": campaign.title,
                "description": campaign.description,
                "niche": campaign.niche,
                "start_date": campaign.start_date.strftime("%Y-%m-%d"),
                "end_date": campaign.end_date.strftime("%Y-%m-%d"),
                "budget": campaign.budget,
                "visibility": campaign.visibility,
                "influencer_name": user.username,       # Assuming `name` field exists in `Influencer` table
                "requested_amount": ad_request.amount,    # Budget requested by influencer from AdRequest
                "message": ad_request.message ,            # Message from influencer from AdRequest
                'status': ad_request.status
            }

            for campaign, ad_request, user in ad_requests
        ]

        return jsonify(campaigns=campaigns_data), 200

    except Exception as e:

        db.session.rollback()
        print(f"Error fetching all campaigns: {str(e)}")
        return jsonify({"error": "Failed to fetch campaigns", "message": str(e)}), 500


@app.route('/all-campaigns', methods=['GET'])
@jwt_required()
def get_all_campaigns():

    print("accessed get all campaign")

    try:
        # Get all campaigns from the database
 
        campaigns = Campaign.query.filter(Campaign.visibility != 'private').all()

        # Convert campaigns to JSON format
        campaigns_data = [
            {
                "id": campaign.id,
                "title": campaign.title,
                "description": campaign.description,
                "niche": campaign.niche,
                "start_date": campaign.start_date.strftime("%Y-%m-%d"),
                "end_date": campaign.end_date.strftime("%Y-%m-%d"),
                "budget": campaign.budget,
                "visibility": campaign.visibility
            }
            for campaign in campaigns
        ]
        return jsonify(campaigns=campaigns_data), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching requested campaigns: {str(e)}")
        return jsonify({"error": "Failed to fetch campaigns", "message": str(e)}), 500



@app.route('/search-campaigns', methods=['GET'])
@jwt_required()
def search_campaigns():
    try:
        # Get search parameters from query string
        title_query = request.args.get('title', '').lower()
        niche_query = request.args.get('niche', '').lower()

        # Search campaigns with filters
        campaigns = Campaign.query.filter(
            Campaign.title.ilike(f"%{title_query}%") 
        ).all()

        # Serialize data
        campaigns_data = [
            {
                "id": campaign.id,
                "title": campaign.title,
                "description": campaign.description,
                "niche": campaign.niche,
                "start_date": campaign.start_date.strftime("%Y-%m-%d"),
                "end_date": campaign.end_date.strftime("%Y-%m-%d"),
                "budget": campaign.budget,
                "visibility": campaign.visibility,
                "user_id": campaign.user_id,
            }
            for campaign in campaigns
        ]

        return jsonify(campaigns=campaigns_data), 200
    except Exception as e:
        print(f"Error during campaign search: {str(e)}")
        return jsonify({"error": "Failed to fetch campaigns"}), 500


@app.route('/campaigns/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    user_id = get_jwt_identity().get('user_id')
    campaign = Campaign.query.filter_by(id=campaign_id, user_id=user_id).first()
    
    if not campaign:
        return jsonify({"error": "Campaign not found or unauthorized access"}), 404

    return jsonify({
        "id": campaign.id,
        "title": campaign.title,
        "description": campaign.description,
        "niche": campaign.niche,
        "start_date": campaign.start_date.strftime("%Y-%m-%d") if campaign.start_date else None,
        "end_date": campaign.end_date.strftime("%Y-%m-%d") if campaign.end_date else None,
        "budget": campaign.budget,
        "visibility": campaign.visibility
    }), 200


# PUT request to update campaign details

@app.route('/campaigns/<int:campaign_id>/update', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    # Extract user_id from JWT claims
    user_id = get_jwt_identity().get('user_id')
    
    # Fetch the campaign based on campaign_id and user_id to ensure ownership
    campaign = Campaign.query.filter_by(id=campaign_id, user_id=user_id).first()

    if not campaign:
        return jsonify({"error": "Campaign not found or unauthorized access"}), 404

    # Extract data from the request body
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    niche = data.get('niche')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    budget = data.get('budget')
    visibility = data.get('visibility')

    # Check if all required fields are present
    if not all([title, description, niche, start_date_str, end_date_str, budget, visibility]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        # Update campaign fields
        campaign.title = title
        campaign.description = description
        campaign.niche = niche
        campaign.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        campaign.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        campaign.budget = budget
        campaign.visibility = visibility
        
        # Commit changes to the database
        db.session.commit()
        return jsonify({"message": "Campaign updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# this is influencer profile route 

@app.route('/influencer-profile', methods=['GET'])
@jwt_required()  # Ensures only authenticated requests are allowed
def influencer_profile():
    # Get the user identity from the JWT
    print("route accessed")
    identity = get_jwt_identity()
    user_id =  get_jwt_identity().get('user_id')
    username = get_jwt_identity().get('username')
    print(user_id)
    # Fetch user and influencer profile from the database
    user = Users.query.filter_by(id=user_id).first()
    influencer_profile = InfluencerSignup.query.filter_by(user_id=user_id).first()

    # Check if the user and profile exist
    if not user or not influencer_profile:
        return jsonify({"message": "Influencer profile not found"}), 404

    # Prepare profile data for the response
    profile_data = {
        "username": user.username,
        "profile": {
            "role": user.role,
            "reach": influencer_profile.reach,
            "category": influencer_profile.category,
            "niche": influencer_profile.niche
        }
    }


    # Return user profile data in JSON format
    print(profile_data)
    return jsonify(profile_data), 200







# this is sponsor signup


@app.route('/sponsorsignup', methods=['POST'])
def sponsor_signup():

    data = request.get_json()

    username = data.get('username')
    gmail = data.get('gmail')
    password = data.get('password')
    role = data.get('role', 'sponsor')
    company_name = data.get('companyName')
    industry = data.get('industry')
    budget = data.get('budget')

    if not all([username, password, company_name, industry, budget]):
        return jsonify({"message": "All fields are required."}), 400

    existing_user = Users.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists."}), 409

    hashed_password = generate_password_hash(password)
    new_user = Users(username=username, gmail = gmail ,password=hashed_password, role=role)

    try:
        db.session.add(new_user)
        db.session.commit()

        new_sponsor = SponsorSignup(
            username=username,
            password=hashed_password,
            role=role,
            company_name=company_name,
            industry=industry,
            budget=budget,
            user_id=new_user.id,
        )
        db.session.add(new_sponsor)
        db.session.commit()

        return jsonify({"message": "Sponsor registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed, please try again.", "error": str(e)}), 500


@app.route('/register', methods=['POST'])
def register():
    print("Register endpoint accessed.")
    data = request.get_json()
    username = data.get('username')
    gmail = data.get('gmail')
    password = data.get('password')
    role = data.get('role', 'influencer')
    category = data.get('category')
    niche = data.get('niche')
    reach = data.get('reach')
    print("Received data:", data)

    # Validate required fields
    if not all([username, password, category, niche, reach]):
        return jsonify({"message": "All fields are required."}), 400

    # Check if the username already exists
    if Users.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists."}), 409

    # Hash the password and create a new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Fixed hash method
    new_user = Users(username=username, gmail = gmail , password=hashed_password, role=role)

    try:
        # Add and commit the new user to get its ID
        db.session.add(new_user)
        db.session.commit()

        # Use new_user.id as the foreign key for InfluencerSignup
        influencer_info = InfluencerSignup(
            category=category,
            niche=niche,
            reach=reach,
            role=role,
            user_id=new_user.id
        )
        db.session.add(influencer_info)
        db.session.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        print("Error:", e)  # Detailed error message for debugging
        return jsonify({"message": "Registration failed, please try again.", "error": str(e)}), 500




@app.route('/campaign', methods=['POST'])
@jwt_required()
def add_campaign():
    data = request.json
    identity = get_jwt_identity()

    # Retrieve user ID from the JWT token identity
    user_id = identity.get('user_id') if identity else None
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 400
    
    print(data)
    # Retrieve data from request
    title = data.get('title')
    description = data.get('description')
    niche = data.get('niche')
    start_date_str = data.get('start_date')  # "YYYY-MM-DD" format
    end_date_str = data.get('end_date')      # "YYYY-MM-DD" format
    budget = data.get('budget')
    visibility = data.get('visibility')

    # Validate required fields
    if not all([title, description, niche, start_date_str, end_date_str, budget, visibility, user_id]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        # Convert date strings to date objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Validate budget as integer
        try:
            budget = int(budget)
            if budget <= 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Budget must be a positive integer."}), 400

        # Check visibility
        if visibility not in ['public', 'private']:
            return jsonify({"error": "Visibility must be 'public' or 'private'."}), 400

        # Check if the user exists and has a sponsor role
        sponsor = Users.query.get(user_id)
        if not sponsor or sponsor.role != 'sponsor':
            return jsonify({"error": "Invalid sponsor user ID."}), 400

        # Create and add the campaign
        new_campaign = Campaign(
            title=title,
            description=description,
            niche=niche,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            user_id=user_id
        )
        db.session.add(new_campaign)
        db.session.commit()

        return jsonify({"message": "Campaign added successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route('/sponsor-home', methods=['GET'])
@jwt_required()  # Ensures that the request has a valid JWT token
def sponsor_home():
    # Extract JWT claims
    claims = get_jwt_identity()

    # Ensure the user has the correct role (sponsor)
    if claims.get('role') != 'sponsor':
        return jsonify({"error": "Unauthorized"}), 403

    # Extract user_id from JWT claims
    user_id = claims.get('user_id')

    # Fetch campaigns created by the sponsor (filter by user_id)
    campaigns = Campaign.query.filter_by(user_id=user_id).all()

    # Serialize campaign data to send as JSON response
    campaign_list = [{
        #this is the id of the perticular campian 
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'niche': c.niche,
        'start_date': c.start_date.isoformat(),  # Convert start_date to string format
        'end_date': c.end_date.isoformat(),      # Convert end_date to string format
        'budget': c.budget,
        'visibility': c.visibility
    } for c in campaigns]

    # Send the user's name (extracted from claims) and their campaigns
    return jsonify({
        'user_name': claims.get('username'),  # Assuming username is part of the JWT claims
        'campaigns': campaign_list
    })




@app.route('/dcampaign/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(id):
    claims = get_jwt_identity()
    user_id = claims.get('user_id')

    # Perform deletion logic here, ensuring the user has permission
    campaign = Campaign.query.filter_by(id=id, user_id=user_id).first()
    if not campaign:
        return jsonify({"error": "Campaign not found or unauthorized"}), 404
    
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted successfully"}), 200





if __name__ == '__main__':
    app.run(debug=True)
    send_reminders_task.apply_async()  
