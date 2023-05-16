from functools import reduce
from typing import List

from django.test import TestCase


class ViewsTests(TestCase):
    def test_detail_view_with_a_past_question(self) -> None:
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """


def concat_variable_list(myList: List[int]) -> str:
    """
    Return myList as comma-seperated string of values enclosed in parens.
    """
    return "(" + reduce((lambda b, c: b + str(c) + ","), myList, "")[:-1] + ")"
