from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PageSerializer

class PagesView(APIView):
    def get(self, request, page_name):
        try:
            html_content = render_to_string(f'{page_name}.html')
            serializer = PageSerializer(data={'html': html_content})
            if serializer.is_valid():
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TemplateDoesNotExist:
            return Response({'error': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
