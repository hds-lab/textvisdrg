from django.db import models

from msgvis.apps.corpus.models import Sentiment
import textblob

# Create your models here.

def set_message_sentiment(message):
    sentiment_name = "neutral"

    sentiment_value = textblob.TextBlob(message.text).sentiment.polarity
    if sentiment_value > 0:
        sentiment_name = "positive"
    elif sentiment_value < 0:
        sentiment_name = "negative"

    sentiment_model, created = Sentiment.objects.get_or_create(value=sentiment_value, name=sentiment_name)

    message.sentiment = sentiment_model
    message.save()