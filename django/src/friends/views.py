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

def update_invite_status(request: HttpRequest, status: str):
	data = json.loads(request.body.decode())
	if not request.user.is_authenticated:
		return HttpResponse(status=401)
	if not data or 'invite_id' not in data:
		return JsonResponse({'error': 'Missing arguments'}, status=400)

	try:
		invite = Friend.objects.get(id=data['invite_id'], target=request.user)
		if not invite.status == Friend.Status.PENDING:
			return JsonResponse({'error': f'Invite already {'denied' if invite.status is Friend.Status.DENIED else 'accepted'}'}, status=400)
		invite.status = status
		invite.save()
	except Friend.DoesNotExist:
		return JsonResponse({'error': "Friend invite doesn't exist"}, status=400)
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	except IntegrityError as error:
		return JsonResponse({'error': str(error)}, status=400)
	return HttpResponse(status=200)

@require_POST
def accept(request: HttpRequest):
	return update_invite_status(request, Friend.Status.ACCEPTED)

@require_POST
def deny(request: HttpRequest):
	return update_invite_status(request, Friend.Status.DENIED)
