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

class GoogleAuthenticatorProvider(AbstractAuthenticatorProvider):

  def getUser(self,request):
    if request.args.get('state') != self.securitySession['state']:
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

    self.storeValue('access_token',credentials.access_token)
    self.storeValue('gplus_id',credentials.id_token['sub'])
    self.storeValue('gplus_id',credentials.id_token['sub'])

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