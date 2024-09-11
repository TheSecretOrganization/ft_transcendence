from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpRequest
from django.template.loader import get_template

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
	return create_response(request, 'index.html')

@require_GET
def games(request):
	return create_response(request, 'games.html')

@require_GET
def login(request: HttpRequest):
	if (request.user.is_authenticated):
		return JsonResponse({'redirect': '/'}, status=403)
	return create_response(request, 'login.html', title='Login')

@require_GET
def register(request: HttpRequest):
	if (request.user.is_authenticated):
		return JsonResponse({'redirect': '/'}, status=403)
	return create_response(request, 'register.html', title='Register')

@require_GET
def error_404(request):
	return create_response(request, '404.html')
