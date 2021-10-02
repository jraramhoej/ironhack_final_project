from flask import Flask, render_template, request, Response
import helper_functions

# initiate application
app = Flask(__name__)

@app.route("/")
def home():
    data = [('01-01-2020', 1597), ('02-01-2020', 597), ('03-01-2020', 1675), ('04-01-2020', 1298), ('05-01-2020', 900)]

    labels = []
    values = []
    for row in data:
        labels.append(row[0])
        values.append(row[1])

    return render_template('main.html', labels=labels, values=values)

@app.route("/graph")
def show_graph():
    return render_template('graph.html')

@app.route('/network_analysis', methods=["POST"])
def main_analysis():
    helper_functions.network_analysis()
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)
