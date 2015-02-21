from django.db import models

class Note(models.Model):
    # We're going to use sessions as authentication, for simplicity
    session = models.CharField(max_length=32, db_index=True)
    text = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_on',)
