from django.db import models
from django.contrib.auth.models import User

class FlashCard(models.Model):
    question = models.TextField()
    real_answer = models.TextField()
    possible_answers = models.JSONField(default=list)  # Default is an empty list

    def __str__(self):
        return self.question


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_answers")
    flashcard_data = models.JSONField(default=dict)  # Default is an empty dictionary
    answer_log = models.JSONField(default=list)  # Default is an empty list

    def __str__(self):
        return f"UserAnswer({self.user}, {self.flashcard_data})"
