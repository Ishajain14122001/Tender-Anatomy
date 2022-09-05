from ast import keyword
from flask import Flask,render_template,request,redirect,session
import snscrape.modules.twitter as sntwitter
from requests import Session
import mysql.connector
import os
from sentiment import*
email_id=""
app = Flask(__name__)
app.secret_key=os.urandom(24)

try:
    conn=mysql.connector.connect(host="remotemysql.com",user="N0MqkNNYSJ",password="Jc2CDtaJkz",database="N0MqkNNYSJ")
    cursor=conn.cursor()
    
except:
    print("Error........")    

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')


@app.route('/login_validation',methods=['POST'])
def login_validation():
    conn=mysql.connector.connect(host="remotemysql.com",user="N0MqkNNYSJ",password="Jc2CDtaJkz",database="N0MqkNNYSJ")
    cursor=conn.cursor()
    
    email=request.form.get('email')
    password=request.form.get('password')
    
    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    users=cursor.fetchall()
    if len(users)>0:
        session['user_id']=users[0][0]
        session['email_id']= users[0][2]
        return redirect('/home')
    else:
        return redirect('/')
# email=request.form.get('uemail')   
@app.route('/add_user',methods=['POST'])
def add_user():
    conn=mysql.connector.connect(host="remotemysql.com",user="N0MqkNNYSJ",password="Jc2CDtaJkz",database="N0MqkNNYSJ")
    cursor=conn.cursor() 
    
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('upassword') 
    
    cursor.execute("""INSERT INTO `users` (`user_id`,`name`,`email`,`password`) VALUES (NULL,'{}','{}','{}')""".format(name,email, password))
    conn.commit()
    
    cursor.execute("""SELECT * from `users` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['user_id']=myuser[0][0]
    session['email_id'] = myuser[0][2]
    return redirect('/home')

@app.route('/sentiment', methods=['GET'])
def sentiment():
    return render_template("sentiment.html")

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/sentiment_logic',methods=['GET','POST'])
def logic():
    q = request.form.get('keyword')
    n = request.form.get('tweets')
    em=session['email_id']
    pos,neu,neg,pol,sub=getQuery(q,em,n)
    return render_template('sentiment.html',polarity=pol,subjectivity=sub,positive=pos,neutral=neu,negative=neg, keyword=q,tweets=n)

@app.route('/visual')
def visualize():
    return render_template('visual.html')  


if __name__ == "__main__": 
    app.run(debug=True,port=8000)  