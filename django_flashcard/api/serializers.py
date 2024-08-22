from rest_framework import serializers
from .models import FlashCard, UserFlashCard
class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = '__all__'

class UserFlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlashCard
        fields = '__all__'
        