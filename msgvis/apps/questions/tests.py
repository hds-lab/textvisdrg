from django.test import TestCase
from models import Article, Question, Dimension, get_sample_questions

# Create your tests here.
class GetSampleQuestionTest(TestCase):
    def setUp(self):
        article = Article.objects.create(year=2014, authors="Lalal, Lala", link="http://doi.org/xDrz", title="this is a mock paper", venue="A mock conference")
        question = Question(source=article, text="This is a question")
        question.save()
        question.dimensions.add(Dimension.objects.get_or_create(key="hashtags")[0])
        question.dimensions.add(Dimension.objects.get_or_create(key="time")[0])
        question.save()
        question = Question(source=article, text="This is another question")
        question.save()
        question.dimensions.add(Dimension.objects.get_or_create(key="urls")[0])
        question.dimensions.add(Dimension.objects.get_or_create(key="language")[0])
        question.save()
        question = Question(source=article, text="This is the 3rd question")
        question.save()
        question.dimensions.add(Dimension.objects.get_or_create(key="sentiment")[0])
        question.dimensions.add(Dimension.objects.get_or_create(key="language")[0])
        question.save()

    def test_get_sample_question(self):

        dimension_list = []
        questions = get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 3)

        dimension_list = ["hashtags"]
        questions = get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 1)

        dimension_list = ["language"]
        questions = get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 2)

        dimension_list = ["language", "urls"]
        questions = get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 1)