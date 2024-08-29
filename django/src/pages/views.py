from django.views.decorators.http import require_GET
from django.shortcuts import render

@require_GET
def index(request):
	return render(request, 'index.html')

@require_GET
def games(request):
	return render(request, 'games.html')
