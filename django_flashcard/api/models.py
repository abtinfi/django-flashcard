from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FlashCard(models.Model):
    question = models.TextField()
    real_answer = models.TextField()
    possible_answers_json = models.TextField(default=None)  # Renamed field

    @property
    def possible_answers(self):
        import json
        return json.loads(self.possible_answers_json)

    @possible_answers.setter
    def possible_answers(self, value):
        import json
        self.possible_answers_json = json.dumps(value)


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_answers")  # Renamed related_name
    flashcard_data_json = models.TextField()  # Renamed field
    answer_log_json = models.TextField()  # Renamed field

    @property
    def flashcard_data(self):
        import json
        return json.loads(self.flashcard_data_json)

    @flashcard_data.setter
    def flashcard_data(self, value):
        import json
        self.flashcard_data_json = json.dumps(value)

    @property
    def answer_log(self):
        import json
        return json.loads(self.answer_log_json)

    @answer_log.setter
    def answer_log(self, value):
        import json
        self.answer_log_json = json.dumps(value)
