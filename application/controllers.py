from flask import Flask, request, redirect, url_for,send_from_directory
from flask import render_template
from flask_sqlalchemy import SQLAlchemy 

from flask import current_app as app
from application.models import User, Deck, Card
from application.database import db
from main import login_manager
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
	user_id = current_user.id
	decks = Deck.query.filter_by(user_id = user_id).all()
	import datetime

	
	for deck in decks:
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

		deck.count = count
		deck.easy_count = easy_count
		deck.medium_count = medium_count
		deck.hard_count = hard_count

		if deck.last_reviewed == "2000-01-01 18:41:30.082089":
			deck.last_reviewed = "Never"

		score = 0
		if count != 0:
			score = int(((easy_count * 2 + medium_count) / (2 * count)) * 100)
		
		deck.score = score


	return render_template("dashboard.html", decks = decks)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "POST":
		form = request.form
		email = form["email"]
		password = form["password"]

		if not '@' in email:
			user = User.query.filter_by(username=email).first()

			if not user:
				return render_template("login.html", error = "User doesn't exist!")

			if check_password_hash(user.password, password):
				login_user(user)
				return redirect(url_for('dashboard'))
			else:
				return render_template("login.html", error = "Incorrect password!", email = email)

		user = User.query.filter_by(email=email).first()

		if not user:
			return render_template("login.html", error = "User doesn't exist!")

		if check_password_hash(user.password, password):
			login_user(user)
			return redirect(url_for('dashboard'))
		else:
			return render_template("login.html", error = "Incorrect password!", email = email)
		
	elif request.method == "GET":
		return render_template("login.html")


@app.route('/register', methods = ["GET", "POST"])
def register():
	if request.method == "POST":
		form = request.form
		username = form["username"]
		email = form["email"]
		password = form["password"]

		if not '@' in email:
			return render_template("register.html", error = "Invalid Email!", email = email, username = username, password = password)

		temp1 = User.query.filter_by(username=username).first()
		if temp1:
			return render_template("register.html", error = "Username already in use!", error1 = True, email = email, password = password)
		

		temp2 = User.query.filter_by(email=email).first()
		if temp2:
			return render_template("register.html", error = "Email already in use!", error2 = True, username = username, password = password)

		user = User(username = username, email = email, password = generate_password_hash(password, method='sha256'))
		db.session.add(user)
		db.session.commit()

		login_user(user)
		return redirect(url_for('dashboard'))
		
	elif request.method == "GET":
		return render_template("register.html")

@app.route('/logout', methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return render_template("login.html")


@app.route('/edit_profile', methods = ["GET", "POST"])
@login_required
def edit_profile():
	if request.method == "GET":
		return render_template("edit_profile.html")
	elif request.method == "POST":
		form = request.form
		operation_type = form["type"]
		if operation_type == "change_username":
			username = form["username"]
			password = form["password"]

			print(current_user.username)

			if password == current_user.password:
				user = User.query.filter_by(username=username).first()

				if user and current_user.username != username:
					return render_template("edit_profile.html",error1 = True, error_cu = "Username already taken!",password = password)

				user = User.query.filter_by(username=current_user.username).first()
				user.username = username
				db.session.add(user)
				db.session.commit()

				return render_template("edit_profile.html",  success1 = "Successfully updated username!")
			else:
				return render_template("edit_profile.html",  error2 = True, error_cu = "Incorrect password!",username = username)

		elif operation_type == "change_password":
			old_password = form["old-password"]
			new_password = form["new-password"]

			if current_user.password == old_password:
				user = User.query.filter_by(username=current_user.username).first()
				user.password = new_password
				db.session.add(user)
				db.session.commit()

				return render_template("edit_profile.html",  success2 = "Successfully updated password!")
			else:
				return render_template("edit_profile.html",  error3 = True, error_cp = "Incorrect password!", new_password = new_password)


@app.route('/new_deck', methods = ["POST"])
@login_required
def add_deck():
	import datetime
	form = request.form
	name = form["name"]

	deck = Deck(name = name, user_id=current_user.id, last_reviewed = datetime.datetime.fromisoformat('2000-01-01 18:41:30.082089'))
	db.session.add(deck)
	db.session.commit()

	return redirect(url_for('dashboard'))

@app.route('/delete_deck/<deck_id>', methods = ["GET", "POST"])
@login_required
def delete_deck(deck_id):

	deck = Deck.query.filter_by(id=int(deck_id)).first()

	db.session.delete(deck)
	db.session.commit()

	return redirect(url_for('dashboard'))

@app.route('/edit_deck/<deck_id>', methods = ["GET", "POST"])
@login_required
def edit_deck(deck_id):

	if request.method == "GET":

		deck_id = int(deck_id)

		deck = Deck.query.filter_by(id=deck_id).first()

		cards = Card.query.filter_by(deck_id=deck_id).all()

		return render_template("edit_deck.html", deck = deck, cards = cards)

	elif request.method == "POST":
		deck_id = int(deck_id)
		form = request.form
		name = form["name"]

		deck = Deck.query.filter_by(id=deck_id).first()

		deck.name = name
		db.session.add(deck)
		db.session.commit()

		xd = "/edit_deck/" + str(deck_id)

		return redirect(xd)




@app.route('/edit_deck/<deck_id>/new_card', methods = ["POST"])
@login_required
def add_card(deck_id):
	import datetime
	form = request.form
	front = form["front"]
	back = form["back"]
	deck_id = int(deck_id)

	card = Card(front = front, back=back, score = 0, deck_id= deck_id, last_reviewed = datetime.datetime.fromisoformat('2000-01-01 18:41:30.082089'))
	db.session.add(card)
	db.session.commit()

	xd = "/edit_deck/" + str(deck_id)

	return redirect(xd)

@app.route('/edit_deck/<deck_id>/update_card', methods = ["POST"])
@login_required
def update_card(deck_id):
	form = request.form
	front = form["front"]
	back = form["back"]
	card_id = form["id"]
	deck_id = int(deck_id)

	card = Card.query.filter_by(id = card_id).first()

	card.front = front
	card.back = back

	db.session.add(card)
	db.session.commit()

	xd = "/edit_deck/" + str(deck_id)

	return redirect(xd)


@app.route('/edit_deck/<deck_id>/delete_card/<card_id>', methods = ["GET", "POST"])
@login_required
def delete_card(deck_id, card_id):

	card = Card.query.filter_by(id = card_id).first()

	db.session.delete(card)
	db.session.commit()

	deck = Deck.query.filter_by(id=deck_id).first()

	db.session.add(deck)
	db.session.commit()

	xd = "/edit_deck/" + str(deck_id)

	return redirect(xd)


@app.route('/review/<deck_id>', methods = ["GET", "POST"])
@login_required
def review(deck_id):
	if request.method == "GET":
		import datetime
		deck = Deck.query.filter_by(id = deck_id).first()
		cards = Card.query.filter_by(deck_id = deck_id).order_by(Card.score, Card.last_reviewed).all()

		curr_time = datetime.datetime.utcnow()

		new_cards = []

		for card in cards:
			lrtime = datetime.datetime.fromisoformat(card.last_reviewed)
			if card.last_reviewed is None:
				continue
			diff =  curr_time - lrtime

			print(diff)
			if card.score == 2:
				if diff.seconds > 18000:
					new_cards.append(card)
			elif card.score == 1:
				if diff.seconds > 1800:
					new_cards.append(card)
			elif card.score == 0:
				if diff.seconds > 300:
					new_cards.append(card)

		if len(new_cards) == 0:
			if len(cards) > 0:
				message = "All the cards have been reviewed. Kindly try again after some time to review again."
				dummy_eroor = "something went wrong"
				return render_template('no_cards_for_review.html', deck = deck, message = message,dummy_eroor=dummy_eroor)
			else:
				message = "No cards available for review. Try adding new cards to the deck."
				return render_template('no_cards_for_review.html', deck = deck, message = message)


		return render_template('review.html', deck = deck, card = new_cards[0])
	elif request.method == "POST":
		import datetime
		form = request.form
		card_id = int(form["id"])
		score = int(form["score"])

		card = Card.query.filter_by(id = card_id).first()

		card.score = score
		card.last_reviewed = datetime.datetime.utcnow()

		db.session.add(card)
		db.session.commit()

		deck = Deck.query.filter_by(id = deck_id).first()
		deck.last_reviewed = datetime.datetime.utcnow()

		db.session.add(deck)
		db.session.commit()

		cards = Card.query.filter_by(deck_id = deck_id).order_by(Card.score, Card.last_reviewed).all()

		curr_time = datetime.datetime.utcnow()

		new_cards = []

		for card in cards:
			lrtime = datetime.datetime.fromisoformat(card.last_reviewed)
			if card.last_reviewed is None:
				continue
			diff =  curr_time - lrtime

			if card.score == 2:
				if diff.seconds > 18000:
					new_cards.append(card)
			elif card.score == 1:
				if diff.seconds > 1800:
					new_cards.append(card)
			elif card.score == 0:
				if diff.seconds > 300:
					new_cards.append(card)

		if len(new_cards) == 0:
			if len(cards) > 0:
				message = "All the cards have been reviewed. Kindly try again after some time to review again."
				return render_template('no_cards_for_review.html', deck = deck, message = message)
			else:
				message = "No cards available for review. Try adding new cards to the deck."
				return render_template('no_cards_for_review.html', deck = deck, message = message)


		return render_template('review.html', deck = deck, card = new_cards[0])







