from rest_framework import serializers
from .models import AboutSystem

class AboutSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSystem
        fields = "__all__"