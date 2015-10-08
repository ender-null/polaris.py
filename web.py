from __main__ import *
from flask import Flask
from flask import render_template
application = Flask(__name__)

@application.route('/')
@application.route('/home')
def home():
	return render_template('home.html')

if __name__ == "__main__":
	application.run(host='0.0.0.0')