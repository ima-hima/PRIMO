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


def _make_taxon() -> m.Taxon:
    from django.db import connection

    rank = m.TaxonomicRank.objects.create(rank="species")
    fossil, _ = m.Fossil.objects.get_or_create(label="extant", defaults={"abbr": "E"})
    # parent_id is non-nullable and self-referential; use raw SQL to bootstrap
    # a root taxon that points to itself.
    with connection.cursor() as c:
        c.execute("SET FOREIGN_KEY_CHECKS=0")
        c.execute(
            "INSERT INTO taxon (parent_id, taxonomic_rank_id, label, fossil_id,"
            f" expand_in_tree, tree_root, comments) VALUES (0, {rank.id},"
            f"' Test taxon', {fossil.id}, 0, 0, NULL)"
        )
        taxon_id = c.lastrowid
        c.execute("UPDATE taxon SET parent_id = %s WHERE id = %s", [taxon_id, taxon_id])
        c.execute("SET FOREIGN_KEY_CHECKS=1")
    return m.Taxon.objects.get(id=taxon_id)


def _make_specimen(**kwargs: object) -> m.Specimen:
    continent, _ = m.Continent.objects.get_or_create(continent_name="Unknown")
    country, _ = m.Country.objects.get_or_create(country_name="Unknown")
    locality, _ = m.Locality.objects.get_or_create(
        locality_name="Test Locality",
        defaults={"continent": continent, "country": country},
    )
    institute, _ = m.Institute.objects.get_or_create(
        institute_name="Test Institute",
        defaults={"locality": locality},
    )
    sex, _ = m.Sex.objects.get_or_create(label="unknown")
    fossil, _ = m.Fossil.objects.get_or_create(label="unknown", defaults={"abbr": "U"})
    captive, _ = m.Captive.objects.get_or_create(captive_or_wild="unknown")
    taxon = _make_taxon()
    defaults: dict[str, object] = {
        "taxon": taxon,
        "institute": institute,
        "locality": locality,
        "sex": sex,
        "fossil": fossil,
        "captive": captive,
        "taxonomic_type": None,
    }
    defaults.update(kwargs)
    return m.Specimen.objects.create(**defaults)
