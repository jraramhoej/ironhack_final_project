import slack
import database
from flask import request, Response
import pandas as pd
import numpy as np
import re
import networkx as nx
from pyvis.network import Network
from dotenv import dotenv_values

# load environment variables
config = dotenv_values(".env")

# define slack client
client = slack.WebClient(token=config['SLACK_TOKEN'])

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
                "Hey, check out our latest analysis of your team here:"
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

    # fill reply column with NO_REPLIES for cases where no one replied to the message
    #messages["reply_users"] = messages["reply_users"].fillna(value="NO_REPLIES")

    # convert timestamp to datetime object
    messages['date'] = pd.to_datetime(messages['ts'], unit="s").dt.date

    messages['ts'] = pd.to_datetime(messages['ts'], unit="s")

    # clean text column from quotation marks
    messages["text"] = messages["text"].apply(lambda x: re.sub(r"\"", "", x))

    #messages["ts"] = messages["ts"].astype(str)

    # replace user ids with names of users
    # messages["reply_users"] = messages["reply_users"].apply(get_name)
    # messages["user"] = messages["user"].apply(get_name)

    # select columns to save
    messages = messages[["reply_users", "user", "text", "date"]]

    # def find_reaction_users(col):
    #     try:
    #         return col[0]["users"]
    #     except:
    #         return np.nan

    # find user ids in the reactions column
    #messages["reactions"] = messages["reactions"].apply(find_reaction_users)

    # explode the reply_users column to get senders of replies
    messages = messages.explode("reply_users")

    # explode the reactions column to get senders of reactions
    #messages = messages.explode("reactions")

    # replace NaN with None
    messages = messages.replace(np.nan, "no_replies")

    return messages

    # create database
    #database.sql_action(database.create_database)

    # create tables
    #database.sql_action(database.create_table)

    # populate table
    #database.populate_table(messages)




def network_analysis(data):

    # # retrieve data from database
    # results = database.sql_retrieve(database.retrieval)

    # results_data = results["results"]
    # description = results["description"]

    # # create pandas dataframe
    # data = pd.DataFrame(results_data, columns = [header[0] for header in description])

    # save df as csv
    data.to_csv("message_data.csv", index=False)
    
    # get number of messages per user
    df = data.groupby(["reply_users", "user"]).size().reset_index().rename(columns={0: 'count'})

    # get all rows of original
    df = data.merge(df, how="left", left_on=["reply_users", "user"], right_on=["reply_users", "user"])

    # rename columns
    df.rename({"reply_users": "source", "user": "target"}, inplace=True, axis=1)

    df = df[["source", "target", "text", "date", "count"]]

    df.reset_index(drop=True, inplace=True)

    # data frame for graph without messages with no replies
    graph_df = df[df.source != "no_replies"]

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

    net.show('templates/graph.html')

    # get the degree of centrality for the graph object
    degree_centrality = nx.degree_centrality(Q)

    # get the closeness of centrality for the graph object
    closeness_centrality = nx.closeness_centrality(Q)

    # get the betweenness of centrality for the graph object
    betweenness_centrality = nx.betweenness_centrality(Q)

    # the density of the network
    density = nx.density(Q)

    print({"degree_centrality": degree_centrality, "closeness_centrality": closeness_centrality, "betweenness_centrality": betweenness_centrality, "density": density})


def graph_data():

    # load csv
    df = pd.read_csv("message_data.csv")

    # messages per day
    df = df.groupby(["date"]).size().reset_index().rename(columns={0: 'count'})

    df['date'] = pd.to_datetime(df['date'])

    df.index = pd.DatetimeIndex(df['date'], freq='infer')

    df["date"] = df["date"].astype(str)

    #df.drop(["date"], axis=1, inplace=True)

    records = df.to_records(index=False)

    return list(records)
