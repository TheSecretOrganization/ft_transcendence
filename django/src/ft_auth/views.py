from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, get_user_model
from django.db.utils import IntegrityError
import json

@require_POST
def login(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not all(k in data for k in ['username', 'password']):
		return JsonResponse({'message': 'Missing fields (required username and password)'}, status=400)
	username = data['username']
	password = data['password']
	user = authenticate(username=username, password=password)
	if user is None:
		return JsonResponse({'message': 'Wrong credentials'}, status=401)
	request.session['user_id'] = user.id
	return HttpResponse(status=200)

@require_GET
def logout(request: HttpRequest):
	if 'user_id' in request.session:
		del request.session['user_id']
		return HttpResponse(status=200)
	else:
		return JsonResponse({'message': 'You\'re not logged in'}, status=401)

@require_POST
def register(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not all(k in data for k in ['username', 'password']):
		return JsonResponse({'error': 'Missing fields'}, status=400)
	username = data['username']
	password = data['password']
	try:
		get_user_model().objects.create_user(username=username, password=password)
	except IntegrityError:
		return JsonResponse({'error': 'Username already exist'}, status=400)
	return HttpResponse(status=200)
