from django.test import TestCase
from django.urls import reverse


class HomeViewTest(TestCase):
    def test_index_page(self) -> None:
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
