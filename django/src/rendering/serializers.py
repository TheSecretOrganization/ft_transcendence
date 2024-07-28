from rest_framework import serializers

class PageSerializer(serializers.Serializer):
    html = serializers.CharField()
