from flask_restful import Resource, reqparse
from flask_restful import fields, marshal_with

from application.database import db
from application.models import User, Deck, Card
from application.validation import NotFoundError, BusinessValidationError, CustomError

from werkzeug.security import generate_password_hash, check_password_hash

output_fields = {
	"id" : fields.Integer,
	"username" : fields.String,
	"email" : fields.String,
}

output_fields_decks = {
	"id" : fields.Integer,
	"name" : fields.String,
	"last_reviewed" : fields.String,
}

output_fields_deck_score = {
	"id" : fields.Integer,
	"score" : fields.Integer,
}

output_fields_cards = {
	"id" : fields.Integer,
	"front" : fields.String, 
	"back" : fields.String, 
	"score" : fields.Integer,
	"deck_id" : fields.Integer,
	"last_reviewed" : fields.String,

}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('email')
create_user_parser.add_argument('password')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('email')


create_deck_parser = reqparse.RequestParser()
create_deck_parser.add_argument('name')
create_deck_parser.add_argument('user_id')

update_deck_parser = reqparse.RequestParser()
update_deck_parser.add_argument('name')


create_card_parser = reqparse.RequestParser()
create_card_parser.add_argument('front')
create_card_parser.add_argument('back')
create_card_parser.add_argument('deck_id')

update_card_parser = reqparse.RequestParser()
update_card_parser.add_argument('front')
update_card_parser.add_argument('back')

class UserAPI(Resource):
	@marshal_with(output_fields)
	def get(self, username):
		# Get the User from database based on username
		user = db.session.query(User).filter(User.username == username).first()

		if user:
			# return a valid user JSON
			return user
		else:
			# return 404 error
			raise NotFoundError(status_code=404)

	@marshal_with(output_fields)	
	def put(self, username):
		args = update_user_parser.parse_args()
		email = args.get("email", None)
		if email is None:
			raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")

		if not '@' in email:
			raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="Invalid email")

		user = db.session.query(User).filter(User.email == email).first()

		if user and user.username != username:
			raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="This email is already occupied")

		# Check if the user exists
		user = db.session.query(User).filter(User.username == username).first()

		if user is None:
			raise NotFoundError(status_code=404)

		user.email = email
		db.session.add(user)
		db.session.commit()

		return user

	def delete(self, username):
		# Check if the user exists
		user = db.session.query(User).filter(User.username == username).first()

		if user is None:
			raise NotFoundError(status_code=404)

		db.session.delete(user)
		db.session.commit()

		return "", 200

	def post(self):
		args = create_user_parser.parse_args()
		username = args.get("username", None)
		email = args.get("email", None)
		password = args.get("password", None)

		if username is None:
			raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

		if email is None:
			raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")

		if password is None:
			raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="password is required")

		if not '@' in email:
			raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="Invalid email")

		user = db.session.query(User).filter((User.username == username) | (User.email == email)).first()

		if user:
			raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="Duplicate user")

		new_user = User(username = username, email=email, password = generate_password_hash(password, method='sha256'))
		db.session.add(new_user)
		db.session.commit()
		return "", 201



class DeckAPI(Resource):
	@marshal_with(output_fields_decks)
	def get(self, id):

		deck = db.session.query(Deck).filter(Deck.id == id).first()

		if deck:
			# return a valid user JSON
			return deck
		else:
			# return 404 error
			raise NotFoundError(status_code=404)

	@marshal_with(output_fields_decks)	
	def put(self, id):
		args = update_deck_parser.parse_args()
		name = args.get("name", None)
		if name is None:
			raise BusinessValidationError(status_code=400, error_code="BE1008", error_message="deck name is required")

		# Check if the deck exists
		deck = db.session.query(Deck).filter(Deck.id == id).first()

		if deck is None:
			raise NotFoundError(status_code=404)

		deck.name = name
		db.session.add(deck)
		db.session.commit()

		return deck

	def delete(self, id):
		# Check if the deck exists
		deck = db.session.query(Deck).filter(Deck.id == id).first()

		if deck is None:
			raise NotFoundError(status_code=404)

		db.session.delete(deck)
		db.session.commit()

		return "", 200

	def post(self):
		import datetime
		args = create_deck_parser.parse_args()
		name = args.get("name", None)
		user_id = args.get("user_id", None)

		if name is None:
			raise BusinessValidationError(status_code=400, error_code="BE1008", error_message="deck name is required")

		if user_id is None:
			raise BusinessValidationError(status_code=400, error_code="BE1009", error_message="user_id is required")

		new_deck = Deck(name = name, user_id=user_id, last_reviewed = datetime.datetime.fromisoformat('2000-01-01 18:41:30.082089'))
		db.session.add(new_deck)
		db.session.commit()
		return "", 201

class DeckScoreAPI(Resource):
	@marshal_with(output_fields_deck_score)
	def get(self, id):

		deck = db.session.query(Deck).filter(Deck.id == id).first()

		if deck:
			count = 0
			easy_count = 0
			medium_count = 0
			hard_count = 0
			#lrtime = deck.last_reviewed
			#current_time = datetime.datetime.utcnow()


			cards = Card.query.filter_by(deck_id=deck.id).all()

			for card in cards:
				count += 1
				if card.score == 1:
					medium_count += 1
				elif card.score == 2:
					easy_count += 1
				elif card.score == 0:
					hard_count += 1

			score = 0
			if count != 0:
				score = int(((easy_count * 2 + medium_count) / (2 * count)) * 100)
			
			deck.score = score
			# return a valid user JSON
			return deck
		else:
			# return 404 error
			raise NotFoundError(status_code=404)

class CardAPI(Resource):
	@marshal_with(output_fields_cards)
	def get(self, id):
		
		card = db.session.query(Card).filter(Card.id == id).first()

		if card:
			# return a valid user JSON
			return card
		else:
			# return 404 error
			raise NotFoundError(status_code=404)

	@marshal_with(output_fields_cards)	
	def put(self, id):
		args = update_card_parser.parse_args()
		front = args.get("front", None)
		back = args.get("back", None)
		if front is None or back is None:
			raise BusinessValidationError(status_code=400, error_code="BE1011", error_message="front and back of card is required")

		# Check if the card exists
		card = db.session.query(Card).filter(Card.id == id).first()

		if card is None:
			raise NotFoundError(status_code=404)

		card.front = front
		card.back = back
		db.session.add(card)
		db.session.commit()

		return card

	def delete(self, id):
		# Check if the card exists
		card = db.session.query(Card).filter(Card.id == id).first()

		if card is None:
			raise NotFoundError(status_code=404)
		
		db.session.delete(card)
		db.session.commit()

		return "", 200

	def post(self):
		import datetime
		args = create_card_parser.parse_args()
		front = args.get("front", None)
		back = args.get("back", None)
		deck_id = args.get("deck_id", None)

		if front is None or back is None:
			raise BusinessValidationError(status_code=400, error_code="BE1011", error_message="front and back of card is required")

		if deck_id is None:
			raise BusinessValidationError(status_code=400, error_code="BE1012", error_message="deck_id is required")

		new_card = Card(front = front, back = back, deck_id=deck_id, score = 0, last_reviewed = datetime.datetime.fromisoformat('2000-01-01 18:41:30.082089'))
		db.session.add(new_card)
		db.session.commit()
		return "", 201