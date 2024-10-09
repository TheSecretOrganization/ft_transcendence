from .models import FtOauth, User
from logging import getLogger
import os
import requests

logger = getLogger(__name__)

class RequestError(Exception):
	def __init__(self, json, *args: object) -> None:
		super().__init__(*args)
		self.json = json

def get_ft(token):
	req = requests.get('https://api.intra.42.fr/v2/me', headers={
		'Authorization': f'Bearer {token}',
	})
	res = req.json()
	if req.status_code != 200:
		logger.warning(f"Failed to fetch profile {res}")
		raise RequestError(res, 'failed to gather user informations')
	logger.debug(f"fetched profile for {res['login']}")
	return res

def ft_register(token, username) -> FtOauth:
	res = get_ft(token)
	user = User.objects.create_user(username)
	oauth = FtOauth.objects.create(ft_id=res['id'], login=res['login'], user=user)
	logger.info(f"User {username} created for {res['login']}")
	return oauth

def ft_oauth(token) -> FtOauth:
	oauth = get_ft(token)
	oauth = FtOauth.objects.get(ft_id=oauth['id'])
	logger.info(f"got oauth link for {oauth.user.username} alias {oauth.login}")
	return oauth

def get_token(code):
	req = requests.post('https://api.intra.42.fr/oauth/token', data={
		'grant_type': 'authorization_code',
		'client_id': os.getenv('OAUTH_UID'),
		'client_secret': os.getenv('OAUTH_SECRET'),
		'code': code,
		'redirect_uri': os.getenv('OAUTH_FALLBACK'),
	})
	if req.status_code != 200:
		logger.debug('failed to fetch token')
		raise RequestError(req.json(), 'failed to fetch token')
	logger.debug('fetched token')
	return req.json()['access_token']
