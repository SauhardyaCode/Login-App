from flask import Flask, render_template, request, redirect, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import password_hasher as ph
import re, os, random
from datetime import datetime, timedelta

app= Flask(__name__)
hasher= ph.PasswordHasher()

app.config['SQLALCHEMY_DATABASE_URI']= "mysql://sql7604785:Y7GAsDCUTM@sql7.freesqldatabase.com/sql7604785"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False


db= SQLAlchemy(app)
response= Response()

response.set_cookie('logged_info', '0')

class Data(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    username= db.Column(db.String(50), nullable= False)
    email= db.Column(db.String(50), nullable= False)
    pswd_hash= db.Column(db.String(100), nullable= False)
    date_created= db.Column(db.DateTime, default= datetime.utcnow())
    user_hash= db.Column(db.String(100), nullable= False)

    def __repr__(self):
        return f"User: {self.username}, Email: {self.email}, Date: {self.date_created}"
    

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    about = db.Column(db.String(500))
    extension = db.Column(db.String(5))

@app.route('/')
def home():
    db.session.commit()
    database_records= Data.query.all()
    return render_template('home.html', database_records= database_records)

@app.route('/signup', methods= ['GET', 'POST'])
def signup():
    db.session.commit()
    error= False
    message= None
    
    if request.method == 'POST':
        username= request.form['signup-username'].strip()
        email= request.form['signup-email'].strip()
        password= request.form['signup-password'].strip()
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
            data= Data(username= username, email= email, pswd_hash= hasher.get_hash(password), user_hash= hasher.get_hash(username))
            db.session.add(data)
            db.session.commit()
            redirect('/signup')

    if request.cookies.get('logged_info')=='1':
        return redirect('/profile')
    return render_template('sign_up.html', error= error, msg= message)

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
        user_hashes= [uniques[i].user_hash for i in range(len(uniques))]

        if (username, email) in unique_users:
            index= unique_users.index((username,email))
            hash= pswd_hashes[index]
            user_hash= user_hashes[index]
            code= int(re.findall('\$(\d+)\$', hash)[0])

            if hash == hasher.get_hash(password, code):
                return redirect(f'/set_cookie/{index}&{user_hash}')
            
            else:
                error= True
                message= "\u26a0 Wrong Password"

        else:
            error= True
            message= "\u26a0 This username and email is not signed up"
    
    if request.cookies.get('logged_info')=='1':
        return redirect('/profile')
    return render_template('login.html', error= error, msg= message)

@app.route('/set_cookie/<int:index>&<user_hash>')
def set_cookie(index, user_hash):
    resp= make_response(redirect(f'/login'))
    resp.set_cookie('logged_user', user_hash, expires= datetime.utcnow()+timedelta(weeks= 200))
    resp.set_cookie('logged_id', str(index), expires= datetime.utcnow()+timedelta(weeks= 200))
    resp.set_cookie('logged_info', '1', expires= datetime.utcnow()+timedelta(weeks= 200))
    return resp

@app.route('/profile')
def profile():
    db.session.commit()
    logged= request.cookies.get('logged_info')
    userhash= request.cookies.get('logged_user')

    if logged!='1':
        return redirect('/')

    uniques= Data.query.all()
    userhashes= [uniques[i].user_hash for i in range(len(uniques))]

    try:
        index= userhashes.index(userhash)
    except:
        return render_template('cookie_mismatch.html')
    else:
        return render_template('profile.html', username= uniques[index].username)

@app.route('/logout')
def logout():
    db.session.commit()
    resp= make_response(redirect('/'))
    resp.set_cookie('logged_user', '', expires=0)
    resp.set_cookie('logged_id', '', expires=0)
    resp.set_cookie('logged_info', '0')

    return resp

@app.route('/upload', methods= ['GET', 'POST'])
def upload():
    success= 0
    if request.method=='POST':
        about = request.form['about']
        image = request.files['image']

        ext = re.findall("\.([a-z0-9]*)$", image.filename)
        last_data = len(Posts.query.all())

        if len(ext)>0:
            if ext[0] in "tiff.jfif.bmp.gif.svg.png.webp.svgz.jpg.jpeg.ico.xbm.dib.pjp.apng.tif.pjpeg.avif".split('.'):
                if last_data:
                    data = Posts(about= about, extension= ext)
                else:
                    data = Posts(id= 1, about= about, extension= ext)
                db.session.add(data)
                db.session.commit()
                database = Posts.query.all()
                image.save(os.path.dirname(__file__)+f"/static/Posts/post{database[-1].id}.{database[-1].extension}")
                success = 1
            else:
                success = -1

    return render_template('upload.html', success= success)

@app.route('/posts')
def posts():
    database = Posts.query.all()
    random.shuffle(database)
    abouts = []
    urls = []
    for i in range(len(database)):
        if os.path.isfile(os.path.dirname(__file__)+f"/static/Posts/post{database[i].id}.{database[i].extension}"):
            abouts.append(database[i].about)
            urls.append(f"/static/Posts/post{database[i].id}.{database[i].extension}")
        else:
            db.session.query(Posts).delete()
            db.session.commit()
            break

    return render_template('posts.html', database= (abouts, urls))

@app.errorhandler(404)
def _404_(e):
    return render_template('404.html')

@app.errorhandler(500)
def _500_(e):
    url= request.url
    return render_template('500.html', url=url)

if __name__== '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=2000, debug=True)