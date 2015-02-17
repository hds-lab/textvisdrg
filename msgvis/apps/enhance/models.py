from django.db import models

from msgvis.apps.corpus.models import Sentiment
import textblob

# Create your models here.

def set_message_sentiment(message):

    sentiment_value = int(round(textblob.TextBlob(message.text).sentiment.polarity))
    sentiment_model = Sentiment.objects.get(value=sentiment_value)
    message.sentiment = sentiment_model
    message.save()