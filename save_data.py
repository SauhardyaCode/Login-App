import datetime, os
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "mysql://sql8601155:DG89evD7Pj@sql8.freemysqlhosting.net/sql8601155"

db= SQLAlchemy(app)

class Data(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    username= db.Column(db.String(50), nullable= False)
    email= db.Column(db.String(50), nullable= False)
    pswd_hash= db.Column(db.String(100), nullable= False)
    date_created= db.Column(db.DateTime, default= datetime.datetime.utcnow())


@app.route('/')
def main():
    data= Data.query.all()
    response= Response()

    if response.status_code==200:
        with open(os.path.dirname(__file__)+"/data.py", 'w') as f:
            f.write("database= [\\\n")
        with open(os.path.dirname(__file__)+"/data.py", 'a') as f:
            for i in range(len(data)):
                if i+1==len(data):
                    f.write(f"({data[i].id}, '{data[i].username}', '{data[i].email}', '{data[i].pswd_hash}', '{data[i].date_created}')]")
                else:
                    f.write(f"({data[i].id}, '{data[i].username}', '{data[i].email}', '{data[i].pswd_hash}', '{data[i].date_created}'), \\\n")
        
        return "Done..."
    
    else:
        return f"Database breakdown..."


if __name__ == '__main__':
    app.run(port=5000)