from django.test import TestCase

from web.models import Fossil


class HomeViewTest(TestCase):
    def test_fossil_creation(self) -> None:
        fossil = Fossil.objects.create(label="Test", abbr="tst")

        assert fossil.label == "Alice"
        assert fossil.abbr == "tst"
