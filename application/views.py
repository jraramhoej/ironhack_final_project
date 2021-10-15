from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from .models import Slack
from . import db
import json
import pandas as pd
from application.helper_functions import send_response_message, get_slack_data, time_series_analysis, network_analysis


views = Blueprint('views', __name__)

# home page with links to other pages
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    # define slack user id for current user
    slack_user_id = current_user.slack_user_id

    # load data from database
    query = "SELECT * FROM slack WHERE user_id = \"" + slack_user_id + "\";"
    
    # execute query on database from pandas
    df = pd.read_sql(query, db.session.bind)
    
    # analyse data
    users = network_analysis(df)
   
    return render_template(
        "home.html", 
        user=current_user,
        users=users,
        )

# endpoint for retrieving slack data
@views.route("/slack", methods=["POST"])
def slack():

    if request.method == "POST":
        
        # retrieve data from endpoint
        data = request.form

        # define user
        user_id = data.get('user_id')

        # define user input text from slash command
        text = data.get("text")

        # send response message to slack user
        send_response_message(user_id)

        # save slack data to database
        for row in list(get_slack_data(user_id, text).to_records(index=False)):
            client_msg_id = Slack.query.filter_by(client_msg_id=row[0]).first()
            if client_msg_id is None:
                db.session.add(Slack(client_msg_id=row[0], user_id=row[1], reply_users=row[2], user=row[3], text=row[4], ts=row[5]))
                db.session.commit()
            else:
                pass

        return Response(), 200

# page for displaying time series data
@views.route('/time_series', methods=['GET', 'POST'])
@login_required
def message_count():

    # define slack user id for current user
    slack_user_id = current_user.slack_user_id

    # load data from database
    query = "SELECT * FROM slack WHERE user_id = \"" + slack_user_id + "\";"
    
    # execute query on database from pandas
    df = pd.read_sql(query, db.session.bind)

    # modify data for total number of messages time series
    time_series = time_series_analysis(df)
    
    # time series data
    date_labels = list(time_series["data"].index.strftime("%m-%d-%y"))
    over_time_messages = list(time_series["data"]["count"])

    # time series prediction
    date_labels_pred = list(time_series["predictions"].index.strftime("%m-%d-%y"))
    over_time_messages_pred = list(time_series["predictions"])
    
    return render_template(
        "message_count.html", 
        user=current_user, 
        over_time_messages=json.dumps(over_time_messages),
        date_labels =json.dumps(date_labels),
        over_time_messages_pred=json.dumps(over_time_messages_pred),
        date_labels_pred =json.dumps(date_labels_pred)
        )

@views.route('/graph', methods=['GET', 'POST'])
@login_required
def graph():

    # define slack user id for current user
    slack_user_id = current_user.slack_user_id
    
    # load data from database
    query = "SELECT * FROM slack WHERE user_id = \"" + slack_user_id + "\";"
    
    # execute query on database from pandas
    df = pd.read_sql(query, db.session.bind)

    network_analysis(df)

    return render_template("graph.html", user=current_user)
