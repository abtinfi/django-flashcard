from rest_framework.views import APIView, Response
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import FlashCard, UserFlashCard
from fsrs import Card
from datetime import datetime, timezone

class ApiRegister(APIView):
    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.POST)
        if ser_data.is_valid():
            User.objects.create_user(
                username=ser_data.validated_data["username"],
                email=ser_data.validated_data["email"],
                password=ser_data.validated_data["password"]
            )
            return Response(ser_data.data, status=201)
        
        return Response(ser_data.errors, status=400)


class FlashCardListAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user
        due_flashcards = []
        all_flashcards = FlashCard.objects.all()
        user_flashcards = UserFlashCard.objects.filter(user=user)

        reviewed_flashcards_ids = {uf.flashcard.id for uf in user_flashcards}

        for user_flashcard in user_flashcards:
            card = Card.from_dict(user_flashcard.card_data)
            if card.due <= datetime.now(timezone.utc):
                due_flashcards.append(user_flashcard.flashcard)

        new_flashcards = all_flashcards.exclude(id__in=reviewed_flashcards_ids)

        flashcards = list(due_flashcards) + list(new_flashcards)

        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)