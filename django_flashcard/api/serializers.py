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
        

class ReviewAnswerSerializer(serializers.Serializer):
    flashcard_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=0, max_value=4)  # Assuming rating is between 0 and 4

    def validate_flashcard_id(self, value):
        if not FlashCard.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Flashcard ID")
        return value