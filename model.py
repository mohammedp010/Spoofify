from unicodedata import category
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Music(db.Model):
    __tablename__ = 'music'
    music_id = db.Column(db.Integer, primary_key=True)
    music_name = db.Column(db.String(64))
    music_image = db.Column(db.LargeBinary)
    music_dor = db.Column(db.DateTime)
    artist_id = db.Column(db.ForeignKey("artist.artist_id"), nullable=False)

    def __repr__(self):
        return '<Music %r>' % self.name

class Artist(db.Model):
    __tablename__ = 'artist'
    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(64))
    artist_dob = db.Column(db.DateTime)
    artist_bio = db.Column(db.String(500))
    def __repr__(self):
        return '<Artist %r>' % self.artist_name