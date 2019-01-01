from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import User, BaseDb
from flask import session as login_session
import requests

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
BaseDb.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

from securityManager import AbstractAuthenticatorProvider

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import pprint
import json

class GoogleAuthenticatorProvider(AbstractAuthenticatorProvider):

  def getUser(self,request):
    if request.args.get('state') != self.getStateToken():
      raise ValueError('invalid request happen, no state token found')
      
    #code to exchange for an access token
    code=request.data

    try:
      oauth_flow = flow_from_clientsecrets('client_secret.json', scope='openid')
      #why? postmessage
      oauth_flow.redirect_uri = 'postmessage'
      credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
      raise ValueError('failed to upgarde the authorization code')

    tokeninfo_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
    tokeninfo_params = {'access_token': credentials.access_token, 'alt': 'json'}
    tokeninfo = requests.get(tokeninfo_url, params=tokeninfo_params).json()
    #example tokeninfo: {u'aud': u'909512625928-hqhhdpj9ongevr805lcq4mat8p25144e.apps.googleusercontent.com', u'email_verified': u'true', u'expires_in': u'3598', u'access_type': u'offline', u'exp': u'1546380808', u'azp': u'909512625928-hqhhdpj9ongevr805lcq4mat8p25144e.apps.googleusercontent.com', u'scope': u'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile', u'email': u'moses.tschanz@gmail.com', u'sub': u'111..024690'}

    if tokeninfo['sub'] != credentials.id_token['sub']:
      raise ValueError("Token's user ID doesn't match given user ID.")
    
    #load the client id:
    client_id=json.loads(open('client_secret.json','r').read())['web']['client_id']
    if tokeninfo['aud'] != client_id:
      raise ValueError("Token's client ID does not match app's client id.")

    self.storeValue('access_token',credentials.access_token)
    self.storeValue('gplus_id',credentials.id_token['sub'])

    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    userinfo_params = {'access_token': credentials.access_token, 'alt': 'json'}
    userinfo = requests.get(userinfo_url, params=userinfo_params).json()
    #example userinfo: {u'profile': u'https://plus.google.com/111065870889369024690', u'family_name': u'Tschanz', u'sub': u'111065870889369024690', u'picture': u'https://lh4.googleusercontent.com/-9FCWF1O3AVM/AAAAAAAAAAI/AAAAAAAAAAA/AKxrwcYigX44Al5lCVT-3bUI4n16eUAn4Q/mo/photo.jpg', u'locale': u'de', u'email_verified': True, u'given_name': u'M.', u'gender': u'male', u'email': u'moses.tschanz@gmail.com', u'name': u'M. Tschanz'}

    user = session.query(User).filter_by(email = userinfo['email'])
    if user.count() == 0:
      user = User(email=userinfo['email'])

    return session.query(User).first()

  def checkLogin(self,request, user):
  	print user
  	return True

  def onLogout(self,user):
    #revoke token
    print "revoke token"



class FormAuthenticatorProvider(AbstractAuthenticatorProvider):

  def getUser(self,request):
    return session.query(User).first()

  def checkLogin(self,request, user):
  	print user
  	return True

  def onLogout(self,user):
    #revoke token
    print "revoke token"