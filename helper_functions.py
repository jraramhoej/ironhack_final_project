import slack
import database
from flask import request, Response
import os
import pandas as pd
import re
from datetime import datetime
import numpy as np
#from language_assessment import get_characteristics
import networkx as nx
from pyvis.network import Network
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')

# define slack client
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# function to retrieve the display name of the user based on user id
def get_name(user_id):
    try:
        out = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    except:
        out = "NO_REPLIES"
    return out

# function to get the channels that a user is active in
def get_user_channels(user_id):
    return client.users_conversations(user=user_id)["channels"]

# function used to retrieve network analysis data for a specific channel
def network_analysis():

    # retrieve data from endpoint
    data = request.form

    # define user
    user = data.get('user_id')

    # define user input text from slash command
    text = data.get("text")

    # define slack client
    client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    # define message to be posted
    message = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                "Hey, check out our latest analysis of your team here:"
            )
        }
    }

    client.chat_postMessage(channel=user, blocks=[message])

    try:
        channel_id = [channel["id"] for channel in get_user_channels(user) if channel["name"] == text][0]
    except:
        channel_id = "C01T6GGTBQD"

    # get channel history
    result = client.conversations_history(channel=channel_id, limit=1000)

    # retrieve messages
    conversation_history = result["messages"]

    # create DataFrame
    messages = pd.DataFrame(conversation_history)

    # save df as csv
    messages.to_csv("message_data.csv", index=False)

    # fill reply column with NO_REPLIES for cases where no one replied to the message
    messages["reply_users"] = messages["reply_users"].fillna(value="NO_REPLIES")

    # convert timestamp to datetime object
    messages['ts'] = pd.to_datetime(messages['ts'], unit="s").dt.date

    # clean text column from quotation marks
    messages["text"] = messages["text"].apply(lambda x: re.sub(r"\"", "", x))

    # replace user ids with names of users
    messages["reply_users"] = messages["reply_users"].apply(get_name)
    messages["user"] = messages["user"].apply(get_name)

    # select columns to save
    messages = messages[["client_msg_id", "type", "reply_users", "user", "text", "ts"]]

    # create database
    database.sql_action(database.create_database)

    # create tables
    database.sql_action(database.create_table)

    # populate table
    database.populate_table(messages)

    # explode the reply_users column to get senders of replies
    messages = messages.explode("reply_users")

    # get number of messages per user
    df = messages.groupby(["reply_users", "user"]).size().reset_index().rename(columns={0: 'count'})

    # get all rows of original
    df = messages.merge(df, how="left", left_on=["reply_users", "user"], right_on=["reply_users", "user"])

    # rename columns
    df.rename({"reply_users": "source", "user": "target"}, inplace=True, axis=1)

    df = df[["source", "target", "text", "ts", "count"]]

    df.reset_index(drop=True, inplace=True)

    # data frame for graph without messages with no replies
    graph_df = df[df.source != "NO_REPLIES"]







    # create graph
    Q = nx.from_pandas_edgelist(graph_df, source="source", target="target", edge_attr="count")

    # create vis network
    net = Network(height='750px', width='100%', bgcolor='white', font_color='black')

    net.barnes_hut()

    sources = graph_df['source']
    targets = graph_df['target']
    weights = graph_df['count']

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]

        net.add_node(src, src, title=src)
        net.add_node(dst, dst, title=dst)
        net.add_edge(src, dst, value=w)

    net.show('graph.html')

    # get the degree of centrality for the graph object
    degree_centrality = nx.degree_centrality(Q)

    # get the closeness of centrality for the graph object
    closeness_centrality = nx.closeness_centrality(Q)

    # get the betweenness of centrality for the graph object
    betweenness_centrality = nx.betweenness_centrality(Q)

    # the density of the network
    density = nx.density(Q)

    print({"degree_centrality": degree_centrality, "closeness_centrality": closeness_centrality, "betweenness_centrality": betweenness_centrality, "density": density})


