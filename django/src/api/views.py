from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExampleView(APIView):
    def get(self, request):
        data = {"message": "Hello, world!"}
        return Response(data, status=status.HTTP_200_OK)
