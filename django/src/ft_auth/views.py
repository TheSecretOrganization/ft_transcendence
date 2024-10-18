from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login as dlogin, logout as dlogout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from logging import getLogger
from .oauth import get_token, ft_oauth, ft_register, RequestError
from .models import FtOauth
from .models import User
import json

logger = getLogger(__name__)

@require_POST
def login(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['username', 'password']):
		return JsonResponse({'error': _('Missing fields (required username and password)')}, status=400)
	user = authenticate(username=data['username'], password=data['password'])
	if user is None:
		logger.info(f"Tried to login to user {data['username']}")
		return JsonResponse({'error': _('Wrong credentials')}, status=401)
	dlogin(request, user)
	logger.info(f"{user.username} logged in.")
	return HttpResponse(status=200)

@require_GET
def logout(request: HttpRequest):
	if request.user.is_authenticated:
		username = request.user.username
		dlogout(request)
		logger.info(f"{username} logged out.")
		return HttpResponse(status=200)
	else:
		return JsonResponse({'error': _('You are not logged in')}, status=401)

@require_POST
def register(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['username', 'password']):
		return JsonResponse({'error': _('Missing fields')}, status=400)
	try:
		validate_password(data['password'])
		get_user_model().objects.create_user(data['username'], data['password'])
		logger.info(f"user '{data['username']}' created.")
	except IntegrityError:
		return JsonResponse({'error': _('Username already exist')}, status=400)
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	return HttpResponse(status=200)

@require_POST
def password_update(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['current_password', 'new_password']):
		return JsonResponse({'error': _('Missing fields')}, status=400)
	if not request.user.is_authenticated:
		return JsonResponse({'error': _('You must be authenticated to update password')}, status=401)
	if not request.user.check_password(data['current_password']):
		logger.info(f"Tried to update password of user {request.user.username}.")
		return JsonResponse({'error': _('Invalid current password')}, status=400)
	try:
		validate_password(data['new_password'])
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	request.user.set_password(data['new_password'])
	request.user.save()
	logger.info(f"Updated password of {request.user.username}.")
	return HttpResponse(status=200)

@require_POST
def upload_avatar(request):
	max_file_size = 2 * 1024 * 1024
	if request.FILES.get('avatar'):
		avatar_file = request.FILES['avatar']
		if avatar_file.size > max_file_size:
			return JsonResponse({'error': _('File size exceeds 2MB limit.')}, status=400)
		user = request.user
		user.avatar.save(avatar_file.name, avatar_file)
		user.save()
		return JsonResponse({'avatar_url': user.avatar.url}, status=200)
	return JsonResponse({'error': _('Invalid request')}, status=400)

@require_POST
def authorize(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data:
		return JsonResponse({'error': 'Missing body', 'code': 0}, status=400)

	try:
		if 'token' not in request.session and 'code' not in data:
				return JsonResponse({'error': 'Missing code field', 'code': 3}, status=400)
		token = get_token(data['code']) if 'token' not in request.session else request.session['token']

		user = ft_oauth(token).user
		dlogin(request, user)
		return HttpResponse(status=200)
	except FtOauth.DoesNotExist:
		request.session['token'] = token
		if 'username' not in data:
			return JsonResponse({'error': 'Unknown account', 'code': 1}, status=404)

		try:
			user = ft_register(token, data['username']).user
			dlogin(request, user)
			return HttpResponse(status=200)
		except IntegrityError:
			return JsonResponse({'error': 'Username already taken', 'code': 2}, status=400)
		except (ValidationError, TypeError) as err:
			return JsonResponse({'error': err.messages, 'code': 2}, status=400)
		except RequestError as err:
			request.session.pop('token', None)
			return JsonResponse(err.json, status=401)
	except RequestError as err:
		request.session.pop('token', None)
		return JsonResponse(err.json, status=401)
