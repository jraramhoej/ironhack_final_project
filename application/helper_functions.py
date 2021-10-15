import slack
from flask import Response
import pandas as pd
import numpy as np
from numpy import nan
import re
import os
import networkx as nx
from pyvis.network import Network
from dotenv import load_dotenv, dotenv_values
from statsmodels.tsa.arima.model import ARIMA

# load environment variables
# config = dotenv_values(".env")
load_dotenv()
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

# define slack client
client = slack.WebClient(token=SLACK_TOKEN)

# function to retrieve the display name of the user based on user id
def get_name(user_id):
    try:
        out = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    except:
        out = None
    return out

# function to get the channels that a user is active in
def get_user_channels(user_id):
    return client.users_conversations(user=user_id)["channels"]


# send response message to user
def send_response_message(user_id):
    # define message to be posted
    message = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                ":sparkles: Hey, check out our latest analysis of your team here: <https://network-analysis.azurewebsites.net|LINK> :sparkles:"
            )
        }
    }

    client.chat_postMessage(channel=user_id, blocks=[message])


# function used to retrieve network analysis data for a specific channel
def get_slack_data(user_id, text):

    # define channel id
    try:
        channel_id = [channel["id"] for channel in get_user_channels(user_id) if channel["name"] == text][0]
    except:
        channel_id = "C01T6GGTBQD"

    # get channel history
    result = client.conversations_history(channel=channel_id, limit=1000)

    # retrieve messages
    conversation_history = result["messages"]

    # create DataFrame
    messages = pd.DataFrame(conversation_history)

    # add channel id to df
    messages["user_id"] = str(user_id)

    # convert timestamp to datetime object
    messages['date'] = pd.to_datetime(messages['ts'], unit="s").dt.date

    messages['ts'] = pd.to_datetime(messages['ts'], unit="s")

    # clean text column from quotation marks
    messages["text"] = messages["text"].apply(lambda x: re.sub(r"\"", "", x))

    # replace user ids with names of users
    # messages["reply_users"] = messages["reply_users"].apply(get_name)
    # messages["user"] = messages["user"].apply(get_name)

    # select columns to save
    messages = messages[["client_msg_id", "user_id", "reply_users", "user", "text", "date"]]

    # def find_reaction_users(col):
    #     try:
    #         return col[0]["users"]
    #     except:
    #         return np.nan

    # find user ids in the reactions column
    #messages["reactions"] = messages["reactions"].apply(find_reaction_users)

    # explode the reply_users column to get senders of replies
    # messages = messages.explode("reply_users")

    # explode the reactions column to get senders of reactions
    #messages = messages.explode("reactions")

    messages.dropna(inplace=True)

    # convert reply users to string for database
    messages["reply_users"] = messages["reply_users"].astype(str)


    return messages


def time_series_analysis(df):

    # df = df[df["reply_users"] != "nan"]

    df['reply_users'] = pd.eval(df['reply_users'])

    df = df.explode("reply_users")

    df['week'] = pd.to_datetime(df['ts']).dt.to_period('W')

    df = df.groupby(["week"]).size().reset_index().rename(columns={0: 'count'})

    df.set_index("week", inplace=True)

    df.index = df.index.to_timestamp()

    df.sort_index(inplace=True)

    df = df.resample('W').first()

    df.fillna(0, inplace=True)
    
    # # messages per day
    # df = df.groupby(["ts"]).size().reset_index().rename(columns={0: 'count'})

    # # convert column to datetime
    # df['ts'] = pd.to_datetime(df['ts'])

    # # make ts column into index
    # df.index = pd.DatetimeIndex(df['ts'], freq='infer')

    # # make sure we count per day and fill empty days
    # df = df.asfreq('D')

    # # remove ts column
    # df.drop(["ts"], axis=1, inplace=True)

    # # fill NaN values with 0
    # df.fillna(0, inplace=True)

    # fit model
    model = ARIMA(df["count"], order=(5,1,0))
    model_fit = model.fit()

    #make prediction
    predictions = model_fit.predict(start=len(df)-1, end=len(df)+3)

    return {"data": df, "predictions": predictions}
    


def network_analysis(messages):

    #messages = messages[messages["reply_users"] != "nan"]
    
    messages['reply_users'] = pd.eval(messages['reply_users'])

    messages = messages.explode("reply_users")

    # get number of messages per user
    df = messages.groupby(["reply_users", "user"]).size().reset_index().rename(columns={0: 'count'})

    # rename columns
    df.rename({"reply_users": "source", "user": "target"}, inplace=True, axis=1)

    # create graph
    Q = nx.from_pandas_edgelist(df, source="source", target="target", edge_attr="count")

    # create vis network
    net = Network(height='750px', width='100%', bgcolor='white', font_color='black')

    net.barnes_hut()

    sources = df['source']
    targets = df['target']
    weights = df['count']

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]

        net.add_node(src, src, title=src)
        net.add_node(dst, dst, title=dst)
        net.add_edge(src, dst, value=w)

    net.show('application/templates/graph_data.html')

    # get the degree of centrality for the graph object
    degree_centrality = nx.degree_centrality(Q)

    # get the closeness of centrality for the graph object
    closeness_centrality = nx.closeness_centrality(Q)

    # get the betweenness of centrality for the graph object
    betweenness_centrality = nx.betweenness_centrality(Q)

    # the density of the network
    # density = nx.density(Q)

    # make network analysis result to dataframe
    # network_res = pd.DataFrame({"degree_centrality": degree_centrality, "closeness_centrality": closeness_centrality, "betweenness_centrality": betweenness_centrality}).reset_index()

    # number of messages sent
    messages_sent = messages.groupby(["reply_users"]).size().reset_index().rename(columns={0: 'count_sent'})

    # number of messages received
    messages_received = messages.groupby(["user"]).size().reset_index().rename(columns={0: 'count_received'})

    # rename index
    messages_received.rename({"user": "reply_users"}, inplace=True, axis=1)
    # network_res.rename({"index": "reply_users"}, inplace=True, axis=1)

    # res = messages_sent[["reply_users", "count_sent"]].merge(network_res, left_on="reply_users", right_on="reply_users")

    res = messages_sent[["reply_users", "count_sent"]].merge(messages_received, left_on="reply_users", right_on="reply_users")

    return res.values.tolist()


def graph_data():

    # load csv
    df = pd.read_csv("message_data.csv")

    # messages per day
    df = df.groupby(["date"]).size().reset_index().rename(columns={0: 'count'})

    df['date'] = pd.to_datetime(df['date'])

    df.index = pd.DatetimeIndex(df['date'], freq='infer')

    df["date"] = df["date"].astype(str)

    records = df.to_records(index=False)

    return list(records)
