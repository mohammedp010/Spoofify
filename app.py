import os, jwt
from flask import Flask, request, json, jsonify, render_template, make_response

from flask_login import LoginManager
from flask_login import UserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from model import Music, Artist, Rating, User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)

# SQL configuration
user = 'root'
password = ''
host = '127.0.0.1'
port = 3306
database = 'spoofify'

url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
                 user, password, host, port, database
        )
app.config['SQLALCHEMY_DATABASE_URI'] = url
db = SQLAlchemy(app)
db.init_app(app)

app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           current_user = Users.query.filter_by(public_id=data['public_id']).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator

@app.route('/login', methods=['POST']) 
def login():
   auth = request.authorization
   if not auth or not auth.username or not auth.password: 
       return make_response('could not verify', 401, {'Authentication': 'login required"'})  
 
   user = db.session.execute(db.select(User).filter_by(user_name=auth.username)).first()[0]
   print(user)
   if check_password_hash(user.user_pwd, auth.password):
       token = jwt.encode({'public_id' : user.user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
       return jsonify({'token' : token})
 
   return make_response('could not verify',  401, {'Authentication': '"login required"'})

@app.route('/signup', methods=['POST'])
def signup(): 
    """
    Endpoint to signup
    params:
        - username
        - email
        - password
    """
   data = request.get_json() 
   hashed_password = generate_password_hash(data['password'], method='sha256')
   new_user = User(user_name=data['username'], user_pwd=hashed_password, user_email=data["email"])
   db.session.add(new_user) 
   db.session.commit()   
   return jsonify({'message': 'registered successfully'})

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/addMusic", methods=["POST"])
def add_music():
    """
    Endpoint to add music
    params: 
        - musicName
        - artistId
        - releaseDate
    file:
        - musicImage
    """
    data = json.loads(request.form.get('data'))
    file = request.files['image'].read()

    if (
        "musicName" not in data
        or "releaseDate" not in data
        or "artistId" not in data
    ):
        return jsonify({"error": "missing parameters in request!"}), 400

    else:
        try:
            music = Music(music_name=data["musicName"], music_image=file, music_dor=data["releaseDate"], artist_id=data["artistId"])
            db.session.add(music)
            db.session.commit()
        except:
            return jsonify({"error": "Unexpected error!"}), 400
        
    return jsonify({"status": "success"})

@app.route("/addArtist", methods=["POST"])
def add_artist():
    """
    Endpoint to add artist
    params: 
        - artistName
        - artistDob
        - artistBio(optional)
    """
    data = request.json

    if (
        "artistName" not in data
        or "artistDob" not in data
    ):
        return jsonify({"error": "missing parameters in request!"}), 400
    
    artistBio=None
    if data["artistBio"]:
        artistBio=data["artistBio"]
    else:
        try:
            artist = Artist(artist_name=data["artistName"], music_dor=data["artistDob"], artist_bio=artistBio)
            db.session.add(artist)
            db.session.commit()
        except:
            return jsonify({"error": "Unexpected error!"}), 400
        
    return jsonify({"status": "success"})

@app.route("/getArtist", methods=["GET"])
def get_artist():
    """
    Endpoint to get all music artists
    """
    ans=[]
    data = db.session.execute(db.select(Artist).order_by(Artist.artist_name)).scalars()
    
    for obj in data:
        artist={}
        artist["artistId"]= obj.artist_id
        artist["artistName"]= obj.artist_name
        ans.append(artist)

    return jsonify(ans)

@app.route("/getTopTenMusic", methods=["GET"])
def get_top_ten_music():
    """
    Endpoint to get top ten music
    """
    ans=[]
    # data = db.session.execute(db.select(Music, Rating).filter(Music.artist_id==Rating.artist_id).order_by(desc(Rating.rating_val))).scalars()
    
    # for obj in data:
    #     artist={}
    #     print(obj)
    #     ans.append(artist)

    return jsonify(ans)

if __name__ == "__main__":
        app.run(debug=True)
