from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


def run_web_ui():
    app.run("0.0.0.0", 80)
