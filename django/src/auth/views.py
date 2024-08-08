from django.template import loader
from django.http import JsonResponse

def login(request):
	content = loader.get_template('signin.html').render(request=request)
	return JsonResponse({'html': content})

