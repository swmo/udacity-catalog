from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, make_response
app = Flask(__name__)
from forms import *

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from models import BaseDb,CatalogCategory
from pprint import pprint

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
BaseDb.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.context_processor
def catalogCategories():
    def loadCategories():
    	categories = session.query(CatalogCategory).all()
        return categories
    return {'catalogCategories': loadCategories}


@app.route('/')
def home():
	return render_template('home.html')
	return "START"

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		return redirect(url_for('home'))
	return render_template('login.html',form=form)

@app.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		flash("Account created for %s!" % form.email.data, 'success')

		
		return redirect(url_for('home'))

	return render_template('register.html',form=form)


if __name__ == '__main__':
	app.secret_key = 'mq6c&+afehr(a=zvxo_isamyg675sbb$9u$fjo*#2nz_1@m$9x'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
