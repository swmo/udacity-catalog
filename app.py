from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, make_response
from flask_bcrypt import Bcrypt
app = Flask(__name__)

from forms import *

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from models import BaseDb,CatalogCategory, User, CatalogItem
from pprint import pprint
from flask_bcrypt import Bcrypt

from securityManager import SecurityManager
from authenticatorProvider import GoogleAuthenticatorProvider,FacebookAuthenticatorProvider

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
BaseDb.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.context_processor
def passCatalogCategories():
    def loadCategories():
    	categories = session.query(CatalogCategory).all()
        return categories
    return {'catalogCategories': loadCategories} #only load them when they are needed (reason why no laodCategories() )

@app.context_processor
def passApp():
    def returnApp():
        return app
    return {'app': returnApp()}

@app.route('/')
def home():
	latestItems = session.query(CatalogItem).order_by(desc(CatalogItem.id)).limit(4)
	latestUsers = session.query(User).order_by(desc(User.id)).limit(4)
	return render_template('home.html',latestItems=latestItems, latestUsers=latestUsers)

@app.route('/logout')
def logout():
	message = ""
	try: 
		app.securityManager.logout()
		return redirect(url_for('home'))
	except ValueError as x:
		message = x.message

	flash("logout failed ("+message+")",'danger')
	return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	stateToken = app.securityManager.generateStateToken()

	if form.validate_on_submit():
		return redirect(url_for('home'))

	return render_template('login.html',form=form, stateToken = stateToken)

@app.route('/oauth/google', methods=['GET','POST'])
def oauthGoogle():
	message = ""
	try: 
		if app.securityManager.login(GoogleAuthenticatorProvider(),request):
			welcome_name = app.securityManager.getAuthenticatedUser().name
			if (welcome_name is None):
				welcome_name = app.securityManager.getAuthenticatedUser().email

			flash("Hi %s" % welcome_name,'success')
			data = {'message': 'successfully logged in'}
			return jsonify(data), 200
	except ValueError as x:
		message = x.message


	flash("Google login failed ("+message+")",'danger')
	data = {'message':'Login konnte nicht erfolgreich duchgefuehrt werden','status':'error'}
	return jsonify(data), 403

@app.route('/oauth/facebook', methods=['GET','POST'])
def oauthFacebook():
	message = ""
	try: 
		if app.securityManager.login(FacebookAuthenticatorProvider(),request):
			welcome_name = app.securityManager.getAuthenticatedUser().name
			if (welcome_name is None):
				welcome_name = app.securityManager.getAuthenticatedUser().email

			flash("Hi %s" % welcome_name,'success')
			data = {'message': 'successfully logged in'}
			return jsonify(data), 200
	except ValueError as x:
		message = x.message


	flash("Facebook login failed ("+message+")",'danger')
	data = {'message':'Login konnte nicht erfolgreich duchgefuehrt werden','status':'error'}
	return jsonify(data), 403	


@app.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		hashed_password = Bcrypt().generate_password_hash(form.password.data).decode('utf-8')
		newUser = User(email = form.email.data,password=hashed_password)
		session.add(newUser)
		session.commit()
		flash("Account created for %s!" % form.email.data, 'success')

		return redirect(url_for('home'))

	if app.securityManager.isLoggedIn():
		return "is logged In"

	return render_template('register.html',form=form)


@app.route('/catagory/show/<int:id>', methods=['GET'])
def showCategory(id):
	category = session.query(CatalogCategory).filter_by(id = id).one()
	items = category.items
	return render_template('category/show.html', category=category)

@app.route('/item/show/<int:id>', methods=['GET'])
def showItem(id):
	item = session.query(CatalogItem).filter_by(id = id).one()
	return render_template('item/show.html', item=item)

@app.route('/catalog.json', methods=['GET'])
def catalogJson():
	return "return json of the catalog"

if __name__ == '__main__':
	app.secret_key = 'mq6c&+afehr(a=zvxo_isamyg675sbb$9u$fjo*#2nz_1@m$9x'
	app.debug = True
	app.securityManager = SecurityManager()
	app.run(host = '0.0.0.0', port = 8000)

