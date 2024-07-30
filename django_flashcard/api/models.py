from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FlashCard(models.Model):
    question = models.TextField()
    real_answer = models.TextField()
    possible_answer = models.TextField(default=None)

    @property
    def possible_answer(self):
        import json

        return json.loads(self.possible_answer)

    @possible_answer.setter
    def possible_answer(self, value):
        import json

        self.possible_answer = json.dumps(value)


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_answer")
    card = models.TextField()
    log = models.TextField()

    @property
    def card(self):
        import json

        return json.loads(self.card)

    @card.setter
    def card(self, value):
        import json

        self.card = json.dumps(value)

    @property
    def log(self):
        import json

        return json.loads(self.log)

    @log.setter
    def log(self, value):
        import json

        self.log = json.dumps(value)
