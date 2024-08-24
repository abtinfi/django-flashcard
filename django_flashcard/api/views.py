from rest_framework.views import APIView, Response
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import FlashCard, UserFlashCard
from fsrs import Card
from datetime import datetime, timezone
from fsrs import FSRS, Card, ReviewLog, Rating
from rest_framework import status
from django.shortcuts import get_object_or_404

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
    

from fsrs import FSRS, Card, Rating

class ReviewAnswerAPIView(APIView):
    def post(self, request):
        serializer = ReviewAnswerSerializer(data=request.data)
        if serializer.is_valid():
            flashcard_id = serializer.validated_data['flashcard_id']
            rating = serializer.validated_data['rating']
            user = request.user

            flashcard = get_object_or_404(FlashCard, id=flashcard_id)
            user_flashcard, created = UserFlashCard.objects.get_or_create(
                user=user,
                flashcard=flashcard,
                defaults={'card_data': Card().to_dict()}
            )

            card = Card.from_dict(user_flashcard.card_data)

            # بررسی اینکه آیا زمان بررسی فلش‌کارت رسیده است یا نه
            if card.due > datetime.now(timezone.utc):
                return Response({"detail": "It is not time to review this flashcard yet."}, status=status.HTTP_400_BAD_REQUEST)

            # اگر زمان پاسخگویی رسیده است، پاسخ را ذخیره کنید
            f = FSRS()
            review_log = (
                ReviewLog.from_dict(user_flashcard.review_log)
                if user_flashcard.review_log else None
            )
            card, review_log = f.review_card(card, Rating(rating))
            user_flashcard.card_data = card.to_dict()
            user_flashcard.review_log = review_log.to_dict()
            user_flashcard.save()

            return Response({"detail": "Review saved successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)