import pymysql
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from platform_take_out import view, config

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(view.the_user.user)
app.register_blueprint(view.the_merchant.merchant)
db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
