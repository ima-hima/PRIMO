from django.test import TestCase


class ViewsTests(TestCase):
    def test_detail_view_with_a_past_question(self) -> None:
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
