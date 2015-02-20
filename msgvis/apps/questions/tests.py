from django.test import TestCase
from models import Article, Question

# Create your tests here.
class GetSampleQuestionTest(TestCase):
    def setUp(self):
        article = Article.objects.create(year=2014, authors="Lalal, Lala", link="http://doi.org/xDrz", title="this is a mock paper", venue="A mock conference")
        question = Question(source=article, text="This is a question")
        question.save()
        question.add_dimension("hashtags")
        question.add_dimension("time")
        question.save()
        question = Question(source=article, text="This is another question")
        question.save()
        question.add_dimension("urls")
        question.add_dimension("language")
        question.save()
        question = Question(source=article, text="This is the 3rd question")
        question.save()
        question.add_dimension("sentiment")
        question.add_dimension("language")
        question.save()

    def test_get_sample_question(self):

        dimension_list = []
        questions = Question.get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 3)

        dimension_list = ["hashtags"]
        questions = Question.get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 1)

        dimension_list = ["language"]
        questions = Question.get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 2)

        dimension_list = ["language", "urls"]
        questions = Question.get_sample_questions(dimension_list=dimension_list)
        self.assertEquals(questions.count(), 1)
