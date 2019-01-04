from flask import Flask, render_template, request, redirect, \
   jsonify, url_for, flash, make_response
from flask_bcrypt import Bcrypt
# load form classes
from forms import *

# sqlalchemy dependencys
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

# load the necessary model classes
from models import BaseDb, CatalogCategory, User, CatalogItem

# pprint for debbugging stuff
from pprint import pprint

# is used to encrypt the password
# check the password if the user dont use
# a 3th provider like facebook or google
from flask_bcrypt import Bcrypt

# Import Pillow for resizing the uploaded image -> create a Thumbnail
from PIL import Image

# import the selfwritten securityManager,
# it makes it easier to handle diffrent login provider
from securityManager import SecurityManager
from authenticatorProvider import GoogleAuthenticatorProvider, \
    FormAuthenticatorProvider, FacebookAuthenticatorProvider


app = Flask(__name__)

# create connection to the database
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
BaseDb.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# -> so we can easily load them on every page
@app.context_processor
def passCatalogCategories():
    def loadCategories():
        categories = session.query(CatalogCategory).all()
        return categories

    # only load them when they are needed (reason why no laodCategories())
    return {'catalogCategories': loadCategories}


# pass the app to the template engine,
# so we can access the securityManager in our templates
@app.context_processor
def passApp():
    def returnApp():
        return app
    return {'app': returnApp()}


@app.route('/')
def home():
    latestItems = \
        session.query(CatalogItem).order_by(desc(CatalogItem.id)).limit(4)
    latestUsers = \
        session.query(User).order_by(desc(User.id)).limit(4)
    return render_template(
        'home.html',
        latestItems=latestItems,
        latestUsers=latestUsers
        )


@app.route('/logout')
def logout():
    message = ""
    try:
        app.securityManager.logout()
        return redirect(url_for('home'))
    except ValueError as x:
        message = x.message

    flash("logout failed (" + message + ")", 'danger')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    stateToken = app.securityManager.generateStateToken()

    if form.validate_on_submit():
        message = ""
        try:
            if app.securityManager.login(FormAuthenticatorProvider(), form):
                flash('hi you are logged in', 'success')
                return redirect(url_for('home'))
        except ValueError as x:
            message = x.message
            print message
        flash("Login failed ("+message+")", 'danger')
        return redirect(url_for('login'))

    return render_template('login.html', form=form, stateToken=stateToken)


@app.route('/oauth/google', methods=['GET', 'POST'])
def oauthGoogle():
    message = ""
    try:
        if app.securityManager.login(GoogleAuthenticatorProvider(), request):
            welcome_name = app.securityManager.getAuthenticatedUser().name
            if (welcome_name is None):
                welcome_name = app.securityManager.getAuthenticatedUser().email

            flash("Hi %s" % welcome_name, 'success')
            data = {'message': 'successfully logged in'}
            return jsonify(data), 200
    except ValueError as x:
        message = x.message

    flash("Google login failed ("+message+")", 'danger')
    data = {
        'message': 'Login konnte nicht erfolgreich duchgefuehrt werden',
        'status': 'error'
        }
    return jsonify(data), 403


@app.route('/oauth/facebook', methods=['GET', 'POST'])
def oauthFacebook():
    message = ""
    try:
        if app.securityManager.login(FacebookAuthenticatorProvider(), request):
            welcome_name = app.securityManager.getAuthenticatedUser().name
            if (welcome_name is None):
                welcome_name = app.securityManager.getAuthenticatedUser().email

            flash("Hi %s" % welcome_name, 'success')
            data = {'message': 'successfully logged in'}
            return jsonify(data), 200
    except ValueError as x:
        message = x.message

    flash("Facebook login failed (" + message + ")", 'danger')
    data = {
        'message': 'Login konnte nicht erfolgreich duchgefuehrt werden',
        'status': 'error'
        }
    return jsonify(data), 403


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = Bcrypt().generate_password_hash(
            form.password.data).decode('utf-8')
        newUser = User(
            email=form.email.data,
            password=hashed_password
            )
        session.add(newUser)
        session.commit()
        flash("Account created for %s!" % form.email.data, 'success')

        return redirect(url_for('home'))

    if app.securityManager.isLoggedIn():
        return "is logged In"

    return render_template('register.html', form=form)


@app.route('/catagory/show/<int:id>', methods=['GET'])
def showCategory(id):
    category = session.query(CatalogCategory).filter_by(id=id).one()
    items = category.items
    return render_template('category/show.html', category=category)


@app.route('/myitems', methods=['GET'])
def myItems():
    if app.securityManager.isLoggedIn():
        user = app.securityManager.getAuthenticatedUser()
        return render_template('item/myitems.html', myitems=user.items)
    else:
        flash("Please login for manage your items", 'danger')
        return redirect(url_for('login'))


@app.route('/item/show/<int:id>', methods=['GET'])
def showItem(id):
    item = session.query(CatalogItem).filter_by(id=id).one()
    return render_template('item/show.html', item=item)


@app.route('/item/edit/<int:id>', methods=['GET', 'POST'])
def editItem(id):
    if app.securityManager.isLoggedIn():

        item = session.query(CatalogItem).filter_by(id=id).one()
        if item.user.id == app.securityManager.getAuthenticatedUser().id:
            form = CatalogItemForm()
            if form.validate_on_submit():
                item.name = form.name.data
                item.description = form.description.data
                item.category_id = form.category_id.data
                session.add(item)
                session.commit()
                flash("Item saved", "success")
                return redirect(url_for('showItem', id=item.id))

            if request.method == 'GET':
                form.name.data = item.name
                form.description.data = item.description
                form.category_id.data = item.category_id

            return render_template('item/edit.html', item=item, form=form)
        else:
            flash(
                "It's not your Item. Please login with the correct user",
                "danger"
                )
            return redirect(url_for('login'))
    else:
        flash("Please login for manage your items", 'danger')
        return redirect(url_for('login'))


@app.route('/item/delete/<int:id>', methods=['GET', 'POST'])
def deleteItem(id):
    if app.securityManager.isLoggedIn():
        item = session.query(CatalogItem).filter_by(id=id).one()
        if item.user.id == app.securityManager.getAuthenticatedUser().id:
            if request.method == 'POST':
                session.delete(item)
                session.commit()
                flash("item is deleted", "success")
                return redirect(url_for('myItems'))
            return render_template('item/delete.html', item=item)

    flash("It's not your Item. Please login with the correct user", "danger")
    return redirect(url_for('login'))


@app.route('/item/create', methods=['GET', 'POST'])
def createItem():
    if app.securityManager.isLoggedIn():
        form = CatalogItemForm()
        if form.validate_on_submit():
            item = CatalogItem(
                name=form.name.data,
                description=form.description.data,
                category_id=form.category_id.data,
                user_id=app.securityManager.getAuthenticatedUser().id
                )
            session.add(item)
            session.commit()
            flash("Item has been created", "success")
            return redirect(url_for('myItems'))
        return render_template('item/create.html', form=form)
    else:
        flash("Please login for create a new item", 'danger')
        return redirect(url_for('login'))


@app.route('/catalog.json', methods=['GET'])
def catalogJson():
    categories = session.query(CatalogCategory).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/item/<int:id>/json', methods=['GET'])
def catalogItemJson(id):
    item = session.query(CatalogItem).filter_by(id=id).one()
    return jsonify(item.serialize)


@app.route('/myaccount', methods=['GET', 'POST'])
def myAccount():
    if app.securityManager.isLoggedIn():
        user = app.securityManager.getAuthenticatedUser()
        form = MyAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                # split the filename at the "."
                # than reverse the array so the extension is sure at index 0
                extension = list(
                        reversed(
                            form.picture.data.filename.split('.')
                        )
                    )[0]
                filename = str(user.id) + '.' + extension
                path_relativ = 'static/images/profiles/' + filename
                path_absolute = app.root_path + "/" + path_relativ

                resizeImage = Image.open(form.picture.data)
                resizeImage.thumbnail((300, 300))

                resizeImage.save(path_absolute)
                user.picture = path_relativ

            user.email = form.email.data
            user.name = form.name.data

            # todo: clean up session handling
            # (at the moment in securityManager and
            # provider is alwasy a own session
            # -> better to be one?)
            current_session = session.object_session(user)
            current_session.add(user)
            current_session.commit()
            flash("Your Account is updated", 'success')
            redirect(url_for('myAccount'))
        elif request.method == 'GET':
            form.email.data = user.email
            form.name.data = user.name
        return render_template(
            'myaccount.html',
            user=user,
            form=form
            )
    else:
        redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'mq6c&+afehr(a=zvxo_isamyg675sbb$9u$fjo*#2nz_1@m$9x'
    app.debug = True
    app.securityManager = SecurityManager()
    app.run(host='0.0.0.0', port=8000)
