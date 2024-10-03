from uuid import uuid4
from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpRequest
from django.template.loader import get_template
from urllib.parse import quote
import os

def create_response(
		request: HttpRequest,
		template_name: str,
		context = None,
		need_authentication: bool = False,
		title: str|None = None
		):
	if need_authentication and not request.user.is_authenticated:
		return JsonResponse({'error': 'Need authentication', 'redirect': '/login'}, status=403)
	content = {}
	content['html'] = get_template(template_name).render(context, request)
	if title:
		content['title'] = title
	return JsonResponse(content, status=200)

@require_GET
def index(request):
	return create_response(request, 'index.html', title="Home")

@require_GET
def pong(request):
	return create_response(request, 'pong.html', title="Pong", need_authentication=True)

@require_GET
def pong_local(request):
	return create_response(
		request=request,
		template_name='pong_game.html',
		title="Local Pong",
		context={
			"mode": "local",
			"room_id": str(uuid4()),
			"host": True,
		},
		need_authentication=True,
	)

@require_GET
def pong_online(request, id=None):
	return create_response(
		request=request,
		template_name='pong_game.html',
		title="Local Pong",
		context={
			"mode": "online",
			"room_id": str(uuid4()) if id == None else id,
			"host": True if id == None else False,
		},
		need_authentication=True,
	)

@require_GET
def authorize(request: HttpRequest):
	if (request.user.is_authenticated):
		return JsonResponse({'redirect': '/'}, status=403)
	return create_response(request, 'authorize.html')

@require_GET
def error_404(request):
	return create_response(request, '404.html', title="Page not found")

@require_GET
def authentification(request: HttpRequest):
	if (request.user.is_authenticated):
		return JsonResponse({'redirect': '/'}, status=403)
	return create_response(request, 'authentification.html', {
		'oauth_url': (f"https://api.intra.42.fr/oauth/authorize?client_id={os.getenv('OAUTH_UID')}"
		  f"&redirect_uri={quote(os.getenv('OAUTH_FALLBACK'))}&response_type=code"),
	}, title='Authentification')
