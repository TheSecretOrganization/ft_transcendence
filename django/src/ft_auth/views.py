from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login as dlogin, logout as dlogout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
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
