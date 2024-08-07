from django.db import models
from django.contrib.auth.models import User

class FlashCard(models.Model):
    question = models.TextField()
    real_answer = models.TextField()
    possible_answers = models.JSONField(default=list)

    def __str__(self):
        return self.question

class UserFlashCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_flashcards")
    flashcard = models.ForeignKey(FlashCard, on_delete=models.CASCADE, related_name="user_flashcards")
    card_data = models.JSONField(default=dict)
    review_log = models.JSONField(default=dict)
    last_reviewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.flashcard.question}"
