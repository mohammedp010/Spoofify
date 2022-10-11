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
        return '<Music %r>' % self.music_name

class Artist(db.Model):
    __tablename__ = 'artist'
    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(64))
    artist_dob = db.Column(db.DateTime)
    artist_bio = db.Column(db.String(500))
    def __repr__(self):
        return '<Artist %r>' % self.artist_name

class Rating(db.Model):
    __tablename__ = 'ratings'
    rating_id = db.Column(db.Integer, primary_key=True)
    rating_val = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    music_id = db.Column(db.ForeignKey("music.music_id"), nullable=False)
    def __repr__(self):
        return '<Rating %r>' % self.music_id

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50))
    user_email = db.Column(db.String(50))
    user_pwd = db.Column(db.String(255))
    def __repr__(self):
        return '<User %r>' % self.user_name

    # def hash_password(self, password):
    #     self.password_hash = pwd_context.encrypt(password)

    # def verify_password(self, password):
    #     return pwd_context.verify(password, self.password_hash)
        