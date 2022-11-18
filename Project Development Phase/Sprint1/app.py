from flask import Flask, render_template, request, redirect, url_for,session

import ibm_db
import bcrypt
try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=vxz92171;PWD=mCH7uu0w9WXH0hlY",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/",methods=['GET'])
def home():
    if 'email' not in session:
      return redirect(url_for('login'))
    return render_template('home.html',name='Home')

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
      return render_template('register.html',success="You can login")
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

      session['email'] = isUser['USEREMAIL']
      return redirect(url_for('home'))

    return render_template('login.html',name='Home')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)
