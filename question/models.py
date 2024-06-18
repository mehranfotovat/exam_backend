from django.db import models

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Explanation(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text
