from flask import Flask, request, json, jsonify, render_template

from model import Music, Artist
from flask_sqlalchemy import SQLAlchemy

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



if __name__ == "__main__":
        app.run(debug=True)
