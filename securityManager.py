
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import User, BaseDb
from flask import session as login_session,flash
import requests
import random, string

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
BaseDb.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class AbstractAuthenticatorProvider:


  #if you return None than the provicder will stop and run onFailure with 
  def getUser(self,request):
    return None

  def checkLogin(self,request,user):
    return False

  def onLogout(self,user):
    return None

  def onSuccess(self,request,user):
    return None

  def onFailure(self,request,user,error):
    return None

#needs the global login_session
class SecurityManager:


  def getAuthenticatedUser(self):
    if 'userId' in login_session:
        return session.query(User).filter_by(id = login_session['userId']).one()
    return None

  def login(self, provider, request):
    try:
      user = provider.getUser(request) 
      if user == None:
        return False

      login_session['userId'] = user.id

      if provider.checkLogin(request,user):
        provider.onSuccess(request,user)
        return True
   
    except ValueError as error:
      provider.onFailure(request,None,error)
      print error
      return False

    return False

  def generateStateToken(self):
    login_session['state'] = ''.join(random.choice(string.ascii_uppercase+string.digits) for x in xrange(32))
    return login_session['state']

  def isLoggedIn(self):
    if 'userId' in login_session:
      if login_session['userId'] > 0:
        return True
    return False

  def logout(self):
    if 'userId' in login_session:
      del login_session['userId']
    return True


