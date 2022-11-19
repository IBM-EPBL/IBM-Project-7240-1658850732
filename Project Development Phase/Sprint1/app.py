# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 10:25:58 2022

@author: LENOVO
"""

import os
import sqlite3 as sql
import bcrypt
import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for
from markupsafe import escape

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=rqh47791;PWD=8cqzyDyV5CrIMNp9",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)


app = Flask(__name__)
app.secret_key ='\x80\xaf\xb5W\xa5\xed\xf4l`\xad\xc4g'

import sendgrid
#from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from sendgrid.helpers.mail import Mail


def send_conformation_mail(mail):
  #load_dotenv()  
  SENDGRID_API_KEY = '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'  
  #sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API'))
  sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
  from_email = Email("aseera1105@gmail.com")
  to_email = To(mail)
  subject = "Welcome to containment alert"
  content = Content("text/plain", "welcome to our page containment alert.you can use our website to know about the covid zones.Enable location to get notified about the covid containment zone.Stay Alert!!")
  mail = Mail(from_email, to_email, subject, content)
  # mail_json=mail.get()
  response = sg.client.mail.send.post(request_body=mail.get())
  print(response.status_code)
  print(response.body)
  print(response.headers)

def send_alert(mail):
  #load_dotenv() 
  SENDGRID_API_KEY = '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'  
  sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)   
  #sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API'))
  from_email = Email("aseera1105@gmail.com")
  to_email = To(mail)
  subject = "Alert!!"
  content = Content("text/plain", "Be Safe!! You are now at the covid containment zone.Please leave the area as soon as posiible.")
  mail = Mail(from_email, to_email, subject, content)
  # mail_json=mail.get()
  response = sg.client.mail.send.post(request_body=mail.get())
  print(response.status_code)
  print(response.body)
  print(response.headers)  


session={}


@app.route("/",methods=['GET'])
def index():
    # if 'email' not in session:
    #   return redirect(url_for('login'))
    return render_template('index.html',name='Home')

@app.route("/home",methods=['GET'])
def home():
  if request.method == 'GET':
      name1=session['username']
      email=session['useremail']
      return render_template('home.html', name=name1,email=email)   
  return render_template('home.html')    
    

@app.route("/register",methods=['GET','POST'])
def register():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    cpassword = request.form['cpassword']

    if not email or not name or not password or not cpassword:
      return render_template('register.html',error='Please fill all fields')
    if password != cpassword:
        return render_template('register.html',error='The password is not same')
    else:
        hash=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

    query = "SELECT * FROM LOGINAUTHENTICATION WHERE useremail=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    
    if not isUser:
      insert_sql = "INSERT INTO LOGINAUTHENTICATION(USERNAME, USEREMAIL, PASSWORD) VALUES (?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, hash)
      ibm_db.execute(prep_stmt)
      send_conformation_mail(email)
      return render_template('login.html',success="You can login")
      
    else:
      return render_template('register.html',error='Invalid Credentials')

  return render_template('register.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']

      if not email or not password:
        return render_template('login.html',error='Please fill all fields')
      query = "SELECT * FROM LOGINAUTHENTICATION WHERE useremail=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,email)
      ibm_db.execute(stmt)
      isUser = ibm_db.fetch_assoc(stmt)
      print(isUser,password)

      if not isUser:
        return render_template('login.html',error='Invalid Credentials')
             
      #return render_template('login.html',error=isUser['PASSWORD'])

      isPasswordMatch = bcrypt.checkpw(password.encode('utf-8'),isUser['PASSWORD'].encode('utf-8'))

      if not isPasswordMatch:
        return render_template('login.html',error='Invalid Credentials')

      # session['email'] = isUser['USEREMAIL']
      # session['id'] = isUser['ID']
      session['username'] = isUser['USERNAME']
      session['useremail'] = email
      return redirect(url_for('home'))

    return render_template('login.html',name='Home')

@app.route('/user_map')
def user_map():
   return render_template('user_map.html',name='Map')

@app.route('/about')
def about():
   return render_template('about.html',name='Map')

@app.route('/success')
def success():
  inf_location = []
  sql = "SELECT * FROM INF_LOCATION"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    # print ("The Name is : ",  dictionary)
    inf_location.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)
  if inf_location:
    return render_template("success.html", inf_location = inf_location)  
  
  return render_template('success.html')  


@app.route('/addzone',methods=['GET','POST'])
def addzone():
        if request.method == 'GET':
            return render_template('addzone.html')
        if request.method == "POST":
            # get data
            lat = request.form["lat"]
            lon = request.form["lon"]
            if lat == "" or lon == "":
                return render_template('addzone.html')
            sql = "INSERT INTO inf_location ( locate_lat, locate_lang, visited) VALUES ('" + lat + "', '" + lon + "', 0)"
            ibm_db.exec_immediate(conn, sql)
            return render_template('addzone.html',msg="Added Successfully")
        return render_template('addzone.html', success=0)

@app.route('/delete/<lat>')
def delete(lat):
  sql = f"SELECT * FROM INF_LOCATION WHERE LOCATE_LAT='{escape(lat)}'"
  # print(sql)
  stmt = ibm_db.exec_immediate(conn, sql)
  student = ibm_db.fetch_row(stmt)
  # print ("The Name is : ",  student)
  if student:
    sql = f"DELETE FROM INF_LOCATION WHERE LOCATE_LAT='{escape(lat)}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)

    location = []
    sql = "SELECT * FROM INF_LOCATION"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      location.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    if location:
      return render_template("table.html", location=location, msg="Delete successfully")
  return render_template("table.html")



@app.route('/table')
def table():
  inf_location = []
  sql = "SELECT * FROM INF_LOCATION"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    inf_location.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)
  if inf_location:
    return render_template("table.html", inf_location = inf_location)  
  return render_template("table.html")    
  

@app.route('/data')
def data():
  inf_location = []
  sql = "SELECT * FROM INF_LOCATION"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    inf_location.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)
  if inf_location:
    return render_template("data.html", inf_location = inf_location) 
  return render_template("data.html")  
@app.route('/check',methods=['GET','POST'])
def check():
    
    if request.method == 'POST':
      lat = request.form['lat']
      lon = request.form['lon']

      if not lat or not lon:
        return render_template('check.html',error='Please fill all fields')
      query = "SELECT * FROM inf_location WHERE locate_lat=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,lat)
      ibm_db.execute(stmt)
      islocate = ibm_db.fetch_assoc(stmt)


      if  not islocate:
        return render_template('check.html',error='Safe Zone!!')
      else:
        if request.method == 'GET':
           mail=session['useremail'] 
           send_alert(mail)
        return render_template('check.html',error='Covid Zone!! Please leave the zone!!')    
    return render_template('check.html')
  
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
