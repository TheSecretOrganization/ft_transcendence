from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
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

	try:
		target = get_user_model().objects.get(username=data['target'])
		Friend.objects.create(origin=request.user, target=target)
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	except IntegrityError as error:
		return JsonResponse({'error': f'{error}'}, status=400)
	except get_user_model().DoesNotExist:
		return JsonResponse({'error': "This user doesn't exist"}, status=400)
	return HttpResponse(status=200)

def update_invite_status(request: HttpRequest, status: str):
	data = json.loads(request.body.decode())
	if not request.user.is_authenticated:
		return HttpResponse(status=401)
	if not data or 'invite_id' not in data:
		return JsonResponse({'error': 'Missing arguments'}, status=400)

	try:
		invite = Friend.objects.get(id=data['invite_id'], target=request.user)
		if invite.status != Friend.Status.PENDING:
			return JsonResponse({'error': f'Invite should have status {status}'}, status=400)
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

@require_POST
def delete(request: HttpRequest):
	data = json.loads(request.body.decode())
	if not request.user.is_authenticated:
		return HttpResponse(status=401)
	if not data or 'invite_id' not in data:
		return JsonResponse({'error': 'Missing arguments'}, status=400)

	try:
		invite = Friend.objects.get(Q(origin=request.user) | Q(target=request.user), id=data['invite_id'])
		if invite.status not in (Friend.Status.PENDING, Friend.Status.ACCEPTED):
			return JsonResponse({'error': 'Invite should have status 1 or 2'}, status=400)
		if invite.status == Friend.Status.PENDING and invite.target == request.user:
			return JsonResponse({'error': 'You should accept or deny invite not delete it.'}, status=400)
		invite.status = Friend.Status.DELETED
		invite.save()
	except Friend.DoesNotExist:
		return JsonResponse({'error': "Friend invite doesn't exist"}, status=400)
	except ValidationError as error:
		return JsonResponse({'error': error.messages}, status=400)
	except IntegrityError as error:
		return JsonResponse({'error': str(error)}, status=400)
	return HttpResponse(status=200)
