from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, get_user_model
from django.db.utils import IntegrityError

@require_POST
def login(request: HttpRequest):
	if not all(k in request.POST for k in ['username', 'password']):
		return HttpResponseBadRequest({'message': 'Missing fields (required username and password)'})
	username = request.POST['username']
	password = request.POST['password']
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
	if not all(k in request.POST for k in ['username', 'password']):
		return JsonResponse({'error': 'Missing fields'}, status=400)
	username = request.POST['username']
	password = request.POST['password']
	try:
		get_user_model().objects.create_user(username=username, password=password)
	except IntegrityError:
		return JsonResponse({'error': 'Username already exist'}, status=400)
	return HttpResponse(status=200)
