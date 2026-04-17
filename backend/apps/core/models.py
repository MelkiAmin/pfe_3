from django.db import models

class NewsletterSubscriber(models.Model):
    email      = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'newsletter_subscribers'

    def __str__(self):
        return self.email
