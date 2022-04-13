#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import datetime 
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, flash, session, abort
from passlib.hash import sha256_crypt
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import SQLAlchemyError

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
CORS(app)
socketio = SocketIO(app)

@socketio.on('disconnect')
def disconnect_user():
    print("here")
    session.clear()

# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "mm5588"
DB_PASSWORD = "tigman99"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
        
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  if not session.get('logged_in'):
      return render_template('login.html')
  else:  
      # DEBUG: this is debugging code to see what request looks like
      print(request.args)

      #
      # Flask uses Jinja templates, which is an extension to HTML where you can
      # pass data to a template and dynamically generate HTML based on the data
      # (you can think of it as simple PHP)
      # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
      #
      # You can see an example template in templates/index.html
      #
      # context are the variables that are passed to the template.
      # for example, "data" key in the context variable defined below will be 
      # accessible as a variable in index.html:
      #
      #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
      #     <div>{{data}}</div>
      #     
      #     # creates a <div> tag for each element in data
      #     # will print: 
      #     #
      #     #   <div>grace hopper</div>
      #     #   <div>alan turing</div>
      #     #   <div>ada lovelace</div>
      #     #
      #     {% for n in data %}
      #     <div>{{n}}</div>
      #     {% endfor %}
      #

      #
      # render_template looks in the templates/ folder for files.
      # for example, the below file reads template/index.html
      #
      return redirect('/map')

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#

@app.route('/upvote', methods=["POST"])
def upvote():
  data = request.get_json()
  print(data)
  print(type(data))
  cursor = g.conn.execute("""UPDATE selfreporteddata 
  SET numvotes = numvotes + 1 
  WHERE record_num = %s""", data)
  return {"message": "ok"}

@app.route('/map')
def map():
  return render_template("map.html")

START_DATE = datetime.date(2012, 1, 1)
END_DATE = datetime.date(2020, 1, 1)

@app.route('/setDates', methods=["POST"])
def setDates():
  data =  request.form
  start_date_split = data['startdate'].split('-')
  global START_DATE
  global END_DATE
  START_DATE = datetime.date(int(start_date_split[0]), int(start_date_split[1]), int(start_date_split[2]))
  end_date_split = data['enddate'].split('-')
  END_DATE = datetime.date(int(end_date_split[0]), int(end_date_split[1]), int(end_date_split[2]))
  return redirect('/map')

@app.route('/selfreporteddata', methods=["GET"])
def selfreportedData():
  print(START_DATE, END_DATE)
  cursor = g.conn.execute("""SELECT record_num, date, numvotes, abrv, description, lat, lng 
  FROM selfreporteddata 
  WHERE date >= %s AND date <= %s
  ORDER BY numvotes DESC 
  LIMIT 10""", START_DATE, END_DATE)
  points = {}
  for result in cursor:
    points["result" + str(result['record_num'])] =  [result['description'], [result['lat'], result['lng']],
                                    result['date'], result['numvotes'], result['abrv'], result['record_num']]
  cursor.close()
  return points

@app.route('/naturaldisasters', methods=["GET"])
def naturaldisastersData():
  print(START_DATE, END_DATE)
  g.conn.execute("""CREATE OR REPLACE VIEW nd_counts as
SELECT naturaldisasters.abrv, COUNT(*) as count
FROM naturaldisasters 
WHERE date >= %s AND date <= %s
GROUP BY naturaldisasters.abrv;
CREATE OR REPLACE VIEW percentiles as
SELECT k, percentile_cont(k) within group (order by nd_counts.count)
FROM nd_counts, generate_series(0.00, 1, 0.05) as k
GROUP BY k;""", START_DATE, END_DATE)
  nd_perc = g.conn.execute("""SELECT * 
FROM nd_counts t, percentiles p
WHERE ABS(t.count - p.percentile_cont) = 
(SELECT MIN(ABS(t.count - percentile_cont)) FROM temp_changes t1, percentiles p2 WHERE t.abrv = t1.abrv)
""")
  states = {}
  for result in nd_perc:
    states[result["abrv"]] =  int(result["k"]*100)
  nd_perc.close()
  return states


@app.route('/temperature', methods=["GET"])
def temperatureData():
  startdate = datetime.date(int(START_DATE.year), 1, 1)
  enddate = datetime.date(int(END_DATE.year), 1, 1)
  print(startdate, enddate)
  g.conn.execute("""CREATE OR REPLACE VIEW temp_changes as 
SELECT t1.abrv, t2.temp - t1.temp as Temp_Change
FROM Temperature t1 INNER JOIN Temperature t2 on t1.abrv = t2.abrv
WHERE t1.date = %s and t2.date = %s
ORDER BY Temp_Change;

CREATE OR REPLACE VIEW percentiles as
SELECT k, PERCENTILE_CONT(k) within group (order by Temp_Change)
FROM temp_changes, generate_series(0.00, 1, 0.05) as k
GROUP BY k;""", startdate, enddate)
  temp_perc = g.conn.execute("""SELECT * 
FROM temp_changes t, percentiles p
WHERE ABS(t.Temp_Change - percentile_cont) = 
(SELECT MIN(ABS(t.Temp_Change - percentile_cont)) FROM temp_changes t1, percentiles p2 WHERE t.abrv = t1.abrv)
""")
  states = {}
  for result in temp_perc:
    states[result["abrv"]] =  int(result["k"]*100)
  temp_perc.close()
  return states

@app.route('/air', methods=["GET"])
def airData():
  startdate = datetime.date(int(START_DATE.year), 1, 1)
  enddate = datetime.date(int(END_DATE.year), 1, 1)
  print(startdate, enddate)
  g.conn.execute("""CREATE OR REPLACE VIEW air_changes as 
SELECT a1.abrv, a2.aqi - a1.aqi Air_Change
FROM AirQuality a1 INNER JOIN AirQuality a2 on a1.abrv = a2.abrv
WHERE a1.date = %s and a2.date = %s
ORDER BY Air_Change;

CREATE OR REPLACE VIEW percentiles as
SELECT k, PERCENTILE_CONT(k) within group (order by Air_Change)
FROM Air_changes, generate_series(0.00, 1, 0.05) as k
GROUP BY k;""", startdate, enddate)
  air_perc = g.conn.execute("""SELECT * 
FROM air_changes t, percentiles p
WHERE ABS(t.Air_Change - percentile_cont) = 
(SELECT MIN(ABS(t.Air_Change - percentile_cont)) FROM air_changes t1, percentiles p2 WHERE t.abrv = t1.abrv)
""")
  states = {}
  for result in air_perc:
    states[result["abrv"]] =  int(result["k"]*100)
  air_perc.close()
  return states

@app.route('/water', methods=["GET"])
def waterData():
  startdate = datetime.date(int(START_DATE.year), 1, 1)
  enddate = datetime.date(int(END_DATE.year), 1, 1)
  print(startdate, enddate)
  g.conn.execute("""CREATE OR REPLACE VIEW water_changes as 
SELECT w1.abrv, w2.concentration - w1.concentration as Water_Change
FROM waterquality w1 INNER JOIN waterquality w2 on w1.abrv = w2.abrv
WHERE w1.date = %s and w2.date = %s
ORDER BY Water_Change;

CREATE OR REPLACE VIEW percentiles as
SELECT k, PERCENTILE_CONT(k) within group (order by Water_Change)
FROM Water_changes, generate_series(0.00, 1, 0.05) as k
GROUP BY k;""",startdate, enddate)
  water_perc = g.conn.execute("""SELECT * 
FROM water_changes t, percentiles p
WHERE ABS(t.Water_Change - percentile_cont) = 
(SELECT MIN(ABS(t.Water_Change - percentile_cont)) FROM water_changes t1, percentiles p2 WHERE t.abrv = t1.abrv)
""")
  states = {}
  for result in water_perc:
    states[result["abrv"]] =  int(result["k"]*100)
  water_perc.close()
  return states

#source: https://www.section.io/engineering-education/user-login-web-system/

#load new user form
@app.route('/newuser')
def newuser():
    return render_template("newuser.html")

@app.route('/newuser/add', methods=['POST'])
def add_newuser():
    user =  request.form
    username_new = user['username']
    password_new = user['password']
    email_new = user['email']
    first_name_new = user['first_name']
    last_name_new = user['last_name']

    try: 
        g.conn.execute('INSERT INTO Users (username, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)', (username_new, first_name_new, last_name_new, email_new, password_new))
    except SQLAlchemyError as e:
        print("database entry failed")
        error = str(e.__dict__['orig'])
        flash(error)
        return redirect('/newuser')
    print("account created!")
    return redirect('/')

#logging in
@app.route('/login', methods=['POST'])
def login():
    login = request.form
    account = False

    username = login['username']
    password = login['password']

    cmd = 'SELECT password FROM Users WHERE username = (:username1)'
    try:
      g.conn.execute(text(cmd), username1 = username).fetchone()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
      
    try:
      data = g.conn.execute(text(cmd), username1 = username).fetchone()[0]
    except:
      flash('No Account Found')
      return redirect('/')

    print("PASSWORD")
    print(password)
    print("DATA")
    print(data)
    if password == data:
        account = True

    if account:
        session.permanent = False
        session['username'] = username
        session['logged_in'] = True
    else:
      flash('Wrong Password')
      return redirect('/')

    return redirect('/')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')

@app.route('/dataentry')
def dataentry():
  return render_template("dataentry.html")

@app.route('/enterdata', methods=['POST'])
def enterdata():
    data =  request.form
    try:
      date_split = data['date'].split('-')
      date = datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
      lat = float(data['latitude'])
      lon = float(data['longitude'])
      description = data['description']
      state = data['DropDownList']
      numvotes = 0
      contents = [description, date, numvotes, lat, lon, state, session['username'],]
    except:
      flash('Missing Fields or Invalid Input')
      return redirect('/dataentry')

    try: 
        g.conn.execute('INSERT INTO SelfReportedData (description, date, numvotes, lat, lng, abrv, username) VALUES (%s, %s, %s, %s, %s, %s, %s)', contents)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash(error)
        return redirect('/dataentry')

    return redirect('/')

if __name__ == "__main__":
  import click
  app.secret_key = 'super secret key'

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
