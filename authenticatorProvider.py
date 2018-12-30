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

class GoogleAuthenticatorProvider(AbstractAuthenticatorProvider):

  def getUser(self,request):
	if request.args.get('state') != login_session['state']:
		raise ValueError('invalid request happen, no state token found')

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