from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login as dlogin, logout as dlogout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .oauth import get_token, ft_oauth, ft_register, RequestError
from .models import FtOauth
import json

@require_POST
def login(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['username', 'password']):
		return JsonResponse({'error': 'Missing fields (required username and password)'}, status=400)
	user = authenticate(username=data['username'], password=data['password'])
	if user is None:
		return JsonResponse({'error': 'Wrong credentials'}, status=401)
	dlogin(request, user)
	return HttpResponse(status=200)

@require_GET
def logout(request: HttpRequest):
	if request.user.is_authenticated:
		dlogout(request)
		return HttpResponse(status=200)
	else:
		return JsonResponse({'error': 'You\'re not logged in'}, status=401)

@require_POST
def register(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['username', 'password']):
		return JsonResponse({'error': 'Missing fields'}, status=400)
	try:
		validate_password(data['password'])
		get_user_model().objects.create_user(data['username'], data['password'])
	except IntegrityError:
		return JsonResponse({'error': 'Username already exist'}, status=400)
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	return HttpResponse(status=200)

@require_POST
def password_update(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data or not all(k in data for k in ['current_password', 'new_password']):
		return JsonResponse({'error': 'Missing fields'}, status=400)
	if not request.user.is_authenticated:
		return JsonResponse({'error': 'You must be authenticated to update password'}, status=401)
	if not request.user.check_password(data['current_password']):
		return JsonResponse({'error': 'Invalid current password'}, status=400)
	try:
		validate_password(data['new_password'])
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	request.user.set_password(data['new_password'])
	request.user.save()
	return HttpResponse(status=200)

@require_POST
def authorize(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not data:
		return JsonResponse({'error': 'Missing body', 'code': 0}, status=400)

	token = None
	try:
		if 'token' not in request.session:
			if 'code' not in data:
				return JsonResponse({'error': 'Missing code field', 'code': 3}, status=400)
			else:
				token = get_token(data['code'])
		else:
			token = request.session['token']
	except RequestError as err:
		return JsonResponse(err.json, status=500)

	try:
		user = ft_oauth(token).user
		dlogin(request, user)
		return HttpResponse(status=200)
	except FtOauth.DoesNotExist:
		request.session['token'] = token
		if 'username' in data:
			try:
				user = ft_register(token, data['username']).user
				dlogin(request, user)
				return HttpResponse(status=200)
			except IntegrityError:
				return JsonResponse({'error': 'Username already taken', 'code': 2}, status=400)
			except ValidationError or TypeError as err:
				return JsonResponse({'error': err.messages, 'code': 2}, status=400)
			except RequestError as err:
				if 'token' in request.session:
					del request.session['token']
				return JsonResponse(err.json, status=401)
		else:
			return JsonResponse({'error': 'Unknown account', 'code': 1}, status=404)
	except RequestError as err:
		if 'token' in request.session:
			del request.session['token']
		return JsonResponse(err.json, status=401)
