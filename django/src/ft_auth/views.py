from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest, JsonResponse
from django.contrib.auth import authenticate

def login(request: HttpRequest):
	if all(k not in request.POST for k in ('username', 'password')):
		return HttpResponseBadRequest({'message': 'Missing fields (required username and password)'})
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is None:
		return JsonResponse({'message': 'Wrong credentials'}, status=401)
	request.session['user_id'] = user.id
	return HttpResponse(status=200)

def logout(request: HttpRequest):
	if 'user_id' in request.session:
		del request.session['user_id']
		return HttpResponse(status=200)
	else:
		return JsonResponse({'message': 'You\'re not logged in'}, status=401)
