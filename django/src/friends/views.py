from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Friend
import json

@require_POST
def invite(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not request.user.is_authenticated:
		return HttpResponse(status=401)
	if not data or 'target' not in data:
		return JsonResponse({'error': 'Missing arguments'}, status=400)

	if not get_user_model().objects.filter(id=data['target']).exists():
		return JsonResponse({'error': "Target doesn't exist"}, status=400)

	try:
		Friend.objects.create(origin=request.user, target_id=data['target'])
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	except IntegrityError as error:
		return JsonResponse({'error': f'{error}'}, status=400)
	return HttpResponse(status=200)
