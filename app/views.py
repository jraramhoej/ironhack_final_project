from flask import Blueprint, render_template, request, flash, jsonify, Response
from flask_login import login_required, current_user
from .models import Note, Slack
from . import db
import json
import pandas as pd
from app.helper_functions import send_response_message, get_slack_data, time_series_analysis, network_analysis


views = Blueprint('views', __name__)

# home page with links to other pages
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

# endpoint for retrieving slack data
@views.route("/slack", methods=["GET", "POST"])
def slack():

    #if request.method == "POST":
        
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
        ts = Slack.query.filter_by(ts=row[3]).first()
        if not ts:
            db.session.add(Slack(reply_users=row[0], user=row[1], text=row[2], ts=row[3]))
            db.session.commit()
        else:
            pass

    # load data from database
    query = "SELECT * FROM slack;"
    
    # execute query on database from pandas
    df = pd.read_sql(query, db.session.bind)


    return Response(), 200

# page for displaying time series data
@views.route('/message_count', methods=['GET', 'POST'])
@login_required
def message_count():

    # load data from database
    query = "SELECT * FROM slack;"
    
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

    # total messages per person
   

    #print(time_series["predictions"])


    # get the total amount of messages per team member
    total_messages_sent = db.session.query(db.func.count(Slack.text), Slack.reply_users).group_by(Slack.reply_users).all()
    
    total_messages = []
    total_members = []
    for val, name in total_messages_sent:
        total_messages.append(val)
        total_members.append(name)

    # get the messages sent over time
    # dates = db.session.query(db.func.count(Slack.text), Slack.ts).group_by(Slack.ts).order_by(Slack.ts).all()

    # over_time_messages = []
    # dates_label = []
    # for amount, date in dates:
    #     dates_label.append(date.strftime("%m-%d-%y"))
    #     over_time_messages.append(amount)

    return render_template(
        "message_count.html", 
        user=current_user, 
        total_messages=json.dumps(total_messages),
        total_members=json.dumps(total_members),
        over_time_messages=json.dumps(over_time_messages),
        date_labels =json.dumps(date_labels),
        over_time_messages_pred=json.dumps(over_time_messages_pred),
        date_labels_pred =json.dumps(date_labels_pred)
        )

@views.route('/graph', methods=['GET', 'POST'])
@login_required
def graph():

    # load data from database
    query = "SELECT * FROM slack;"
    
    # execute query on database from pandas
    df = pd.read_sql(query, db.session.bind)

    network_analysis(df)

    return render_template("graph.html", user=current_user)
