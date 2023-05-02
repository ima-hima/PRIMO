import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question

# Create your tests here.


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class ViewsTests(TestCase):
    def test_concat_variable_list(self):
        assertEqual(concat_variable_list([]))

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)


def concat_variable_list(myList):
    """
    Return myList as comma-seperated string of values enclosed in parens.
    """
    return "(" + reduce((lambda b, c: b + str(c) + ","), myList, "")[:-1] + ")"
