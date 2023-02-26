from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql
import password_hasher as ph
import re
from datetime import datetime

app= Flask(__name__)
hasher= ph.PasswordHasher()

app.config['SQLALCHEMY_DATABASE_URI']= "mysql://sql12599439:Dcq64aG3qL@sql12.freemysqlhosting.net/sql12599439"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db= SQLAlchemy(app)

class Data(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    username= db.Column(db.String(50), nullable= False)
    email= db.Column(db.String(50), nullable= False)
    pswd_hash= db.Column(db.String(100), nullable= False)
    date_created= db.Column(db.DateTime, default= datetime.utcnow())

    def __repr__(self):
        return f"User: {self.username}, Email: {self.email}, Password: {self.pswd_hash}, Date: {self.date_created}"
    
@app.route('/')
def home():

    db.session.commit()
    database_records= Data.query.all()
    return render_template('home.html', database_records= database_records)

@app.route('/signin', methods= ['GET', 'POST'])
def signin():
    # mydb.commit()
    db.session.commit()
    error= False
    message= None
    
    if request.method == 'POST':
        username= request.form['signin-username'].strip()
        email= request.form['signin-email'].strip()
        password= request.form['signin-password'].strip()
        check_password= request.form['check-password'].strip()

        uniques= Data.query.all()
        unique_usernames= [uniques[i].username for i in range(len(uniques))]
        unique_emails= [uniques[i].email for i in range(len(uniques))]
        
        if len(username)<5:
            error=True
            message= "\u26a0 Username must be atleast 5 characters long"
        
        elif len(password)<8:
            error=True
            message= "\u26a0 Password needs to be atleast 8 characters long"
        
        elif username in unique_usernames:
            error=True
            message= "\u26a0 This username is already taken"
        
        elif email in unique_emails:
            error=True
            message= "\u26a0 This email is already registered"
        
        elif password!=check_password:
            error=True
            message= "\u26a0 Repeated Password is not same as Set Password"

        else:
            data= Data(username= username, email= email, pswd_hash= hasher.get_hash(password))
            db.session.add(data)
            db.session.commit()


    return render_template('sign_in.html', error= error, msg= message)

@app.route('/login', methods= ['GET', 'POST'])
def login():
    db.session.commit()
    error=False
    message= None
    if request.method == 'POST':
        username= request.form['login-username'].strip()
        email= request.form['login-email'].strip()
        password= request.form['login-password'].strip()

        uniques= Data.query.all()
        unique_users= [(uniques[i].username, uniques[i].email) for i in range(len(uniques))]
        pswd_hashes= [uniques[i].pswd_hash for i in range(len(uniques))]
        print(unique_users, pswd_hashes)

        if (username, email) in unique_users:
            index= unique_users.index((username,email))
            hash= pswd_hashes[index]
            code= int(re.findall('\$(\d+)\$', hash)[0])

            if hash == hasher.get_hash(password, code):
                return redirect(f'/set_cookie/{username}')
            
            else:
                error= True
                message= "\u26a0 Wrong Password"

        else:
            error= True
            message= "\u26a0 This username and email is not signed up"
        
    return render_template('login.html', error= error, msg= message)

@app.route('/set_cookie/<user>')
def set_cookie(user):
    resp= make_response(redirect(f'/profile/{user}'))
    resp.set_cookie('name', user)
    return resp

@app.route('/profile/<username>')
def profile(username):
    db.session.commit()

    uniques= Data.query.all()
    usernames= [uniques[i].username for i in range(len(uniques))]

    if username in usernames:
        return render_template('profile.html', username= username)
    else:
        return "404 error by you"

if __name__== '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug= True, port=2000)