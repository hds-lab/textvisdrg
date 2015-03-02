from django.test import TestCase
from models import Article, Question

# Create your tests here.
class GetSampleQuestionTest(TestCase):
    def setUp(self):
        article = Article.objects.create(year=2014, authors="Lalal, Lala", link="http://doi.org/xDrz", title="this is a mock paper", venue="A mock conference")
        self.article = article

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

    def test_no_dimensions(self):
        """When you don't request any dimensions it returns all the questions"""
        questions = Question.get_sample_questions()
        self.assertEquals(len(questions), 3)

    def test_one_dimension(self):
        """With a dimension that matches one question"""
        questions = Question.get_sample_questions('hashtags')
        self.assertEquals(len(questions), 1)

    def test_one_dimension_multi_match(self):
        """Try matching a dimension with multiple questions"""
        questions = Question.get_sample_questions('language')
        self.assertEquals(len(questions), 2)

    def test_multiple_dimensions(self):
        """Match against multiple dimensions"""
        questions = Question.get_sample_questions('language', 'urls')
        self.assertEquals(len(questions), 2)

    def test_question_with_dup_dimensions(self):
        """Questions can be linked to dimensions twice"""

        question = Question(source=self.article, text="This is a another question")
        question.save()
        question.add_dimension("hashtags")
        question.add_dimension("time")
        question.add_dimension("hashtags")
        question.save()

        dimensions = question.ordered_dimensions

        # retrieves the proper number of dimensions
        self.assertEquals(dimensions.count(), 3)

        # they are in the proper order
        keys = [d.key for d in dimensions]
        self.assertEquals(keys, ['hashtags', 'time', 'hashtags'])

