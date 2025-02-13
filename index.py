from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from dotenv import load_dotenv # type: ignore
import os
from functions import create_user, login_user, get_user, create_campaign, get_user_campaigns, delete_campaign, create_lead, get_all_users, total_leads, delete_leads, change_payment_status, create_business
from emailer import send_email
app = Flask(__name__)
CORS(app)

load_dotenv()

SENDER_EMAIL = "kobbyenos.770@gmail.com"
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAILS = [
    os.getenv('ADMIN_EMAIL'),
    os.getenv('SOCIAL_HAWK')
    
]

@app.route("/api/test", methods=["GET"])
def handle_test():

    return jsonify({"message": "API works"})

@app.route('/api/create-business', methods=['POST'])
def handle_create_business():

    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    businessName = data.get('businessName')
    businessLocation = data.get('businessLocation')
    services = data.get('services')
    shipping = data.get('shipping')
    fastest_reach = data.get('fastest_reach')


    business = create_business(name, email, phone, businessName, businessLocation, services, shipping, fastest_reach)

    contact = ""
    if fastest_reach == 'text':
        contact = phone
    else:
        contact = email

    SUBJECT = "🗂️ A USER SUBMITTED BUSINESS INFO"
    BODY = f"A user named {name} submitted their business info. They want leads sent to {contact}. "

    for item in RECIPIENT_EMAILS:
        send_email(SENDER_EMAIL, SENDER_PASSWORD, item, SUBJECT, BODY)

    return jsonify(business)


@app.route('/api/register', methods=['POST'])
def handle_register():

    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    
    user = create_user(name, email, password)
        #save data to DB
        
    return jsonify(user)
    
@app.route('/api/login', methods=['POST'])
def handle_login():

    data = request.json
    email = data.get("email")
    password = data.get("password")

    #handle login

    user = login_user(email, password)
    #print(user) 
    return jsonify(user)

@app.route('/api/user', methods=['GET'])
def handle_get_user():

    name = request.args.get('name')
    email = request.args.get('email')
    #handle login
    user = get_user(email)
    #print(user) 
    return jsonify(user)

@app.route('/api/create-campaign', methods=['POST'])
def handle_create_campaign():

    data = request.json
    campaign_name = data.get("campaign_name")
    campaign_location = data.get("campaign_location")
    campaign_desc = data.get("campaign_desc")
    campaign_service = data.get("campaign_service")

    user_id = data.get("user_id")

    campaign = create_campaign(user_id, campaign_name, campaign_location, campaign_desc,campaign_service)

    SUBJECT = f"📖 {user_id} CAMPAIGN CREATED"
    BODY = f"User {user_id} created a campaign called {campaign_name}. Looking for {campaign_service} in {campaign_location}.\n \n Their description is {campaign_desc}"

    for item in RECIPIENT_EMAILS:
        send_email(SENDER_EMAIL, SENDER_PASSWORD, item, SUBJECT, BODY)


    return jsonify(campaign)

#get user campaigns for a user
@app.route('/api/get-user-campaigns', methods=['GET'])
def handle_get_user_campaign():


    email = request.args.get('email')
    
    campaigns = get_user_campaigns(email)



    return jsonify(campaigns)

#delete campaign
@app.route('/api/delete-campaign', methods=['GET'])
def handle_delete_campaign():


    campaign_id = request.args.get('campaign_id')
    
    campaigns = delete_campaign(campaign_id)
    delete_leads(campaign_id)

    SUBJECT = f"📖⛔️ CAMPAIGN DELETED"
    BODY = f"Campaign {campaign_id} deleted"

    for item in RECIPIENT_EMAILS:
        send_email(SENDER_EMAIL, SENDER_PASSWORD, item, SUBJECT, BODY)


    

    return jsonify(campaigns)

#create and insert lead into db
@app.route('/api/create-lead', methods=['POST'])
def handle_create_lead():


    data = request.json
    user_email = data.get("user_email")
    campaign_name = data.get("campaign_name")
    lead_name = data.get("lead_name")
    lead_location = data.get("lead_location")
    lead_source = data.get("lead_source")
    lead_post = data.get("lead_post")
    lead_contact = data.get("lead_contact")



    lead = create_lead(user_email, campaign_name, lead_name, lead_location, lead_source, lead_post, lead_contact)
    return jsonify(lead)


#get all users
@app.route('/api/get-all-users', methods=['GET'])
def handle_all_users():
    return jsonify(get_all_users())


#get user campaigns
@app.route('/api/campaigns/<string:email>', methods=['GET'])
def handle_user_campaigns(email):
    return jsonify(get_user_campaigns(email))

#get total leads
@app.route('/api/get-total-leads', methods=['GET'])
def handle_get_total_leads():
    email = request.args.get('email')
    return jsonify(total_leads(email))


@app.route('/api/change-payment-status', methods=['GET'])
def handle_change_payment_status():
    email = request.args.get('email')
    subscription = request.args.get('subscription')

    SUBJECT = f"🤑 {email} PAID JUST PAID"
    BODY = f"The user {email} just paid to start"

    for item in RECIPIENT_EMAILS:
        send_email(SENDER_EMAIL, SENDER_PASSWORD, item, SUBJECT, BODY)

    return jsonify(change_payment_status(email, subscription))

@app.route('/api/send-email', methods=['POST'])
def handle_send_email():

    
    data = request.json
    body = data.get('body')
    subject = data.get('subject')

    for item in RECIPIENT_EMAILS:
        send_email(SENDER_EMAIL, SENDER_PASSWORD, item, subject, body)

    return jsonify({"message": "email sent succesfully"})











if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    print("up on 5000")
