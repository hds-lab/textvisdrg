from django.db import models

import textblob

# Create your models here.

def set_message_sentiment(message):

    message.sentiment = int(round(textblob.TextBlob(message.text).sentiment.polarity))
    message.save()