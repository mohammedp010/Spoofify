import os, jwt
from flask import Flask, request, json, jsonify, render_template, make_response

import datetime
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from model import Music, Artist, Rating, User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func, inspect

app = Flask(__name__)

app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

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


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']

       if not token:
           return jsonify({'message': 'valid token missing'}), 401

       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           user = db.session.execute(db.select(User).filter(User.user_id==data['public_id'])).first()
       except:
           return jsonify({'message': 'token is invalid'}), 401
 
       return f(user, *args, **kwargs)
   return decorator

@app.route('/login', methods=['POST']) 
def login():
   auth = request.authorization
   if not auth or not auth.username or not auth.password: 
       return make_response('could not verify', 401, {'Authentication': 'login required"'})  #401: Unauthorized response
 
   user = db.session.execute(db.select(User.user_id, User.user_pwd).filter_by(user_name=auth.username)).first()

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
    data = request.json
    row= db.session.execute(db.select(User.user_name).filter(User.user_name==data["username"])).first()
    if row: return({"error": "User already exists"}), 409

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(user_name=data['username'], user_pwd=hashed_password, user_email=data["email"])
    db.session.add(new_user) 
    db.session.commit()   
    return jsonify({'message': 'registered successfully'})

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/addMusic", methods=["POST"])
@token_required
def add_music(user):
    """
    Endpoint to add music
    params: 
        - musicName
        - artistId
        - releaseDate
        - rating
    file:
        - musicImage
    """
    data = json.loads(request.form.get('data'))
    file = request.files['image'].read()

    if (
        "musicName" not in data
        or "releaseDate" not in data
        or "artistId" not in data
        or "rating" not in data
    ):
        return jsonify({"error": "missing parameters in request!"}), 400 #400: Bad Request response

    else:
        try:
            row= db.session.execute(db.select(Music.music_name).filter(Music.music_name==data["musicName"])).first()
            if row: return({"error": "Data already exists"}), 409 # 409: Conflict response 

            music = Music(music_name=data["musicName"], music_image=file, music_dor=data["releaseDate"], artist_id=data["artistId"])
            db.session.add(music)
            db.session.commit()
            music_data = db.session.execute(db.select(Music.music_id).filter(Music.music_name==data["musicName"])).first()
            rating = Rating(music_id=music_data.music_id, rating_val=data["rating"],user_id=user[0].user_id)
            db.session.add(rating)
            db.session.commit()
        except Exception as e:
            return jsonify({"error": repr(e)}), 500 #500: Internal server error
        
    return jsonify({"status": "success"}), 201 #201:created success

@app.route("/addArtist", methods=["POST"])
@token_required
def add_artist(user_id):
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
    
    if not data["artistBio"]: data["artistBio"] = None

    else:
        try:
            row= db.session.execute(db.select(Artist.artist_name).filter(Artist.artist_name==data["artistName"])).first()
            if row: return({"error": "Data already exists"}), 409

            artist = Artist(artist_name=data["artistName"], artist_dob=data["artistDob"], artist_bio=data["artistBio"])
            db.session.add(artist)
            db.session.commit()
        except Exception as e:
            return jsonify({"error": repr(e)}), 500
        
    return jsonify({"status": "success"}), 201

@app.route("/getArtist", methods=["GET"])
def get_artist():
    """
    Endpoint to get all music artists
    """
    ans=[]
    data = db.session.execute(db.select(Artist.artist_id, Artist.artist_name, db.func.avg(Rating.rating_val).label("avg_rating")).join(Music, Music.artist_id==Artist.artist_id).outerjoin(Rating, Music.music_id==Rating.music_id).group_by(Artist.artist_id).order_by(func.avg(Rating.rating_val).desc())).all()
    for obj in data:
        artist={}
        artist["artistId"]= obj.artist_id
        artist["artistName"]= obj.artist_name
        if obj.avg_rating == None: artist["avgRating"]= 0
        else: artist["avgRating"]= round(float(obj.avg_rating), 2)
        ans.append(artist)

    return jsonify(ans), 200

@app.route("/getMusic", methods=["GET"])
def get_top_ten_music():
    """
    Endpoint to get top ten music
    """
    ans=[]
    data = db.session.execute(db.select(Music.music_id, Music.music_name, Music.music_dor, Artist.artist_name, db.func.avg(Rating.rating_val).label("avg_rating")).join(Artist, Music.artist_id==Artist.artist_id).outerjoin(Rating, Music.music_id==Rating.music_id).group_by(Music.music_id).order_by(func.avg(Rating.rating_val).desc())).all()
    for obj in data:
        music={}
        music["musicId"]= obj.music_id
        music["musicName"]= obj.music_name
        music["musicDor"]= date.isoformat(obj.music_dor)
        music["artistName"]= obj.artist_name
        if obj[4]==None: music["avgRating"]= 0
        else: music["ratingAvg"]= round(float(obj.avg_rating),2)
        ans.append(music)
    return jsonify(ans), 200

if __name__ == "__main__":
        app.run(debug=True)
