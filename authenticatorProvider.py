from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import User, BaseDb
from flask import session as login_session
import requests
from app import session
from securityManager import AbstractAuthenticatorProvider
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import pprint
import json
from flask_bcrypt import Bcrypt


class GoogleAuthenticatorProvider(AbstractAuthenticatorProvider):

    def getUser(self, request):
        if request.args.get('state') != self.getStateToken():
            raise ValueError(
                'invalid request happen, no state token found'
            )

        # code to exchange for an access token
        code = request.data

        try:
            oauth_flow = flow_from_clientsecrets(
                'google_client_secret.json',
                scope='openid'
            )
            # why? postmessage
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            raise ValueError('failed to upgarde the authorization code')

        tokeninfo_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
        tokeninfo_params = {
              'access_token': credentials.access_token,
              'alt': 'json'}

        tokeninfo = requests.get(
              tokeninfo_url,
              params=tokeninfo_params
              ).json()
        # example tokeninfo: {u'aud': u'9095...gleusercontent.com',
        # u'email_verified': u'true', u'expires_in': u'3598',
        # u'access_type': u'offline', u'exp': u'1546380808',
        # u'azp': u'90....44e.apps.googleusercontent.com',
        # u'scope': u'https://www.googleapis.com/auth/plus.me
        # https://www.googleapis.com/auth/userinfo.email
        # https://www.googleapis.com/auth/userinfo.profile',
        # u'email': u'moses.tschanz@gmail.com', u'sub': u'111..024690'}

        if tokeninfo['sub'] != credentials.id_token['sub']:
            raise ValueError("Token's user ID doesn't match given user ID.")

        # load the client id from the json file:
        client_id = json.loads(
            open('google_client_secret.json', 'r').read()
            )['web']['client_id']

        # compare fixed client id with tokeninfo client id
        if tokeninfo['aud'] != client_id:
            raise ValueError(
                "Token's client ID does not match app's client id."
                )

        self.storeValue(
            'access_token',
            credentials.access_token)
        self.storeValue(
            'gplus_id',
            credentials.id_token['sub'])

        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_params = {
            'access_token': credentials.access_token,
            'alt': 'json'}
        userinfo = requests.get(
            userinfo_url,
            params=userinfo_params
            ).json()
        # example userinfo: {u'profile': u'https://plus.google.com/1..0',
        # u'family_name': u'Tschanz', u'sub': u'11..90',
        # u'picture': u'https://lh4.go...n4Q/mo/photo.jpg',
        # u'locale': u'de', u'email_verified': True,
        # u'given_name': u'M.', u'gender': u'male', u'email':
        # u'mo...chanz@gmail.com', u'name': u'M. Tschanz'}

        users = session.query(User).filter_by(email=userinfo['email'])
        if users.count() == 0:
            user = User(email=userinfo['email'])
        else:
            user = users[0]
        user.picture = userinfo['picture']
        user.name = userinfo['name']
        session.add(user)
        session.commit()

        return user

    def checkLogin(self, request, user):
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_params = {
            'access_token': self.getValue('access_token'),
            'alt': 'json'}
        userinfo = requests.get(userinfo_url, params=userinfo_params).json()
        if 'error' in userinfo:
            raise ValueError('Invald Request or Access Token ist not valid')
        if(userinfo['email'] == user.email):
            return True
        else:
            return False

    def onLogout(self, user):
        access_token = self.getValue('access_token')
        self.revokeAccessToken(access_token)

    def revokeAccessToken(self, access_token):

        if access_token is None:
            raise ValueError("No access token given!")

        r = requests.post(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token': access_token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
            )
        if r.status_code != 200:
            raise ValueError("google token revoke failed")

        return True

    def onSuccess(self, request, user):
        print "logged in "


class FacebookAuthenticatorProvider(AbstractAuthenticatorProvider):
    def getUser(self, request):
        if request.args.get('state') != self.getStateToken():
            raise ValueError(
                'invalid request happen, no state token found'
                )
        # code to exchange for an access token
        fb_exchange_token = request.data
        app_id = json.loads(
            open('facebook_client_secret.json', 'r').read()
            )['web']['app_id']
        app_secret = json.loads(
            open('facebook_client_secret.json', 'r').read()
            )['web']['app_secret']

        # exchange the short live token with a long life token:
        tokenexchange_params = {
            'client_id': app_id,
            'client_secret': app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': fb_exchange_token}
        tokenexchange = requests.get(
            "https://graph.facebook.com/oauth/access_token",
            params=tokenexchange_params
            ).json()

        if 'error' in tokenexchange:
            raise ValueError(tokenexchange['error']['message'])

        self.storeValue(
            'access_token',
            tokenexchange['access_token']
            )

        # now the some user information:
        # curl -i -X GET \"https://graph.facebook.com/v3.2/me
        # ?fields=id%2Cname&access_token=EA....ZD"
        userinfo_params = {
            'fields': 'id, email, name, picture',
            'access_token': self.getValue('access_token')}
        userinfo = requests.get(
            "https://graph.facebook.com/v3.2/me",
            params=userinfo_params
            ).json()
        if 'error' in userinfo:
            raise ValueError(userinfo['error']['message'])

        self.storeValue('facebook_id', userinfo['id'])

        users = session.query(User).filter_by(
            email=userinfo['email']
            )

        if users.count() == 0:
            user = User(email=userinfo['email'])
        else:
            user = users[0]
        user.picture = userinfo['picture']['data']['url']
        user.name = userinfo['name']
        session.add(user)
        session.commit()

        return user

    def checkLogin(self, request, user):
        userinfo_params = {
            'fields': 'email',
            'access_token': self.getValue('access_token')}
        userinfo = requests.get(
            "https://graph.facebook.com/v3.2/me",
            params=userinfo_params
            ).json()

        if 'error' in userinfo:
            raise ValueError(userinfo['error']['message'])

        if(userinfo['email'] == user.email):
            return True
        else:
            return False

    def onLogout(self, user):
        access_token = self.getValue('access_token')
        facebook_id = self.getValue('facebook_id')
        self.revokeAccessToken(access_token, facebook_id)

    def revokeAccessToken(self, access_token, facebook_id):
        if access_token is None:
            raise ValueError("No access token given!")

        if facebook_id is None:
            raise ValueError("no facebook id is given")

        revoke_url = 'https://graph.facebook.com/' + \
            '%s/permissions?access_token=%s' \
            % (facebook_id, access_token)
        revokeinfo = requests.delete(revoke_url).json()

        if 'error' in revokeinfo:
            raise ValueError(revokeinfo['error']['message'])

        if revokeinfo['success'] is True:
            return True

        return False

    def onSuccess(self, request, user):
        print "logged in "


class FormAuthenticatorProvider(AbstractAuthenticatorProvider):

    def getUser(self, request):
        users = session.query(User).filter_by(
            email=request.email.data
            )
        if users.count() == 0:
            raise ValueError('User does not exists')
        if users.count() > 1:
            raise Exception(
                'more than one user found, this sould never happen'
                )
        user = users[0]
        return user

    def checkLogin(self, request, user):
        if(user.password is None) or (user.password == ""):
            raise ValueError(
                "Account is connected to a 3rd provider," +
                "please login and set a password")
        if (Bcrypt().check_password_hash(
            user.password,
            request.password.data
        )):
            return True
        else:
            raise ValueError("Password is not correct")

    def onLogout(self, user):
        # revoke token
        print "revoke token"
