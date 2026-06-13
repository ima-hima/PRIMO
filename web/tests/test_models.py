"""
Test some __str__() methods for models. This is just proof-of-concept.
"""

from django.test import TestCase

import web.models as m


class ModelStrTest(TestCase):
    def test_original_string(self) -> None:
        original = m.Original.objects.create(original_or_cast="cast")
        assert str(original) == "cast"

    def test_protocol_string(self) -> None:
        original = m.Protocol.objects.create(label="p1")
        assert str(original) == "p1"

    def test_tax_rank_string(self) -> None:
        original = m.TaxonomicRank.objects.create(rank="r1")
        assert str(original) == "r1"
