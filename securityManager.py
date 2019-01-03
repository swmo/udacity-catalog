
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import User, BaseDb
from flask import session as login_session,flash
import requests
import random, string
import pickle
from sqlalchemy.orm.exc import NoResultFound
from app import session


class AbstractAuthenticatorProvider:

  #if you return None than the provicder will stop and run onFailure with 
  def getUser(self,request):
    raise Execption("you have to implement the getUser method in the provider class")

  def checkLogin(self,request,user):
    raise Execption("you have to implement the checkLogin  method in the provider class")

  def onLogout(self,user):
    return None

  def onSuccess(self,request,user):
    return None

  def onFailure(self,request,user,error):
    return None

  def storeValue(self,name,value):
    #self.securitySession[self.__class__.__name__][name] = value
    login_session[self.__class__.__name__ + '_' + name] = value

  def getValue(self,name):
    return login_session[self.__class__.__name__ + '_' + name]

  def getStateToken(self):
    return login_session['state']


#needs the global login_session
class SecurityManager:


  def getAuthenticatedUser(self):
    if 'userId' in login_session:
        try:
          return session.query(User).filter_by(id = login_session['userId']).one()
        except NoResultFound:
          del login_session['userId']
    return None

  def setProvider(self,provider):
    login_session['provider'] = pickle.dumps(provider)
   
  def getProvider(self):
    return pickle.loads(login_session['provider'])


  def login(self, provider, request):
    try:
      self.setProvider(provider)

      provider = self.getProvider()

      user = provider.getUser(request) 
      if user == None:
        return False

      if provider.checkLogin(request,user):
        provider.onSuccess(request,user)
        login_session['userId'] = user.id
        return True
   
    except ValueError as error:
      provider.onFailure(request,None,error)
      raise ValueError(error.message)

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
      try:
        provider = self.getProvider()
        provider.onLogout(self.getAuthenticatedUser())
        del login_session['userId']
      except ValueError as error:
        #logout user also if the token revoke did not worked
        del login_session['userId']
        raise ValueError(error.message)
      
    return True


