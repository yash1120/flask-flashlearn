from .database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String)
    email = db.Column(db.String, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean())
    decks = db.relationship('Deck',backref='user',cascade='all,delete')

    
class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    name = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    last_reviewed = db.Column(db.String)
    cards = db.relationship('Card',backref='deck',cascade='all,delete')

    
class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    front = db.Column(db.String, nullable = False)
    back = db.Column(db.String, nullable = False)
    score = db.Column(db.Integer, nullable = False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"))
    last_reviewed = db.Column(db.String)