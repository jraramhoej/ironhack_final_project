from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


# from flask import Flask, render_template, request, Response
# import helper_functions
# import json
# import pandas as pd
# import plotly
# import plotly.express as px

# # initiate application
# app = Flask(__name__)

# @app.route('/network_analysis', methods=["POST", "GET"])
# def main_analysis():
#     helper_functions.retrieve_data()
#     helper_functions.network_analysis()

#     return Response(), 200

# @app.route("/home")
# def home():
    
#     data = helper_functions.graph_data()

#     labels = []
#     values = []
#     for row in data:
#         labels.append(row[0])
#         values.append(row[1])

#     return render_template('main.html', labels=labels, values=values)

# if __name__ == "__main__":
#     app.run(debug=True)
