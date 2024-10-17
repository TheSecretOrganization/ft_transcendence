from logging import getLogger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from . import models

logger = getLogger(__name__)


def tournament_json(request, name: str):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "You must be authenticated to get tournament results"},
            status=401,
        )

    if not name.isalpha():
        return JsonResponse({"error": "Invalid tournament name."}, status=400)

    tournament = get_object_or_404(models.PongTournament, name=name)
    data = tournament.serialize()

    return JsonResponse(data, safe=False)
