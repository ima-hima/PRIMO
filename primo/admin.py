from django.contrib import admin

# because filters.py is at top level, import from .filters
from .filters import DropdownFilter
from .models import (
    Ageclass,
    Bodypart,
    BodypartVariable,
    Captive,
    Continent,
    Country,
    Data3D,
    DataScalar,
    Datatype,
    Fossil,
    Institute,
    Laterality,
    Locality,
    Observer,
    Original,
    Protocol,
    Session,
    Sex,
    Specimen,
    SpecimenType,
    Taxon,
    TaxonomicRank,
    Variable,
)

# Register your models here.


@admin.register(DataScalar)
class DataScalarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "variable",
        "value",
    )
    fields = (
        "session",
        "variable",
        "value",
    )
    list_filter = (("variable__value", DropdownFilter), ("session__id", DropdownFilter))
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Ageclass)
class AgeclassAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "age_class",
        "abbr",
        "comments",
    ]
    fields = [
        "ageclass",
        "abbr",
        "comments",
    ]
    search_fields = [
        "id",
    ]


@admin.register(Data3D)
class Data3DAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session",
        "variable",
        "datindex",
        "x",
        "y",
        "z",
    ]
    fields = [
        "session",
        "variable",
        "datindex",
        "x",
        "y",
        "z",
    ]
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Bodypart)
class BodypartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "body_part_name",
        "parent",
        "comments",
    ]
    fields = [
        "body_part_name",
        "parent",
        "comments",
    ]
    list_filter = (("body_part_name", DropdownFilter),)
    search_fields = ["id", "body_part_name"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(BodypartVariable)
class BodypartVariableAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "variable",
        "bodypart",
    ]
    fields = [
        "variable",
        "bodypart",
    ]
    list_filter = (
        ("variable__label", DropdownFilter),
        ("bodypart__body_part_name", DropdownFilter),
    )
    search_fields = ["id", "variable", "bodypart"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Captive)
class CaptiveAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "captive_or_wild",
        "abbr",
        "comments",
    ]
    fields = [
        "captive_or_wild",
        "abbr",
        "comments",
    ]


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "continent_name",
        "comments",
    ]
    fields = [
        "continent_name",
        "comments",
    ]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "country_name",
        "abbr",
        "comments",
    ]
    fields = [
        "country_name",
        "abbr",
        "comments",
    ]
    list_filter = (
        ("country_name", DropdownFilter),
        ("abbr", DropdownFilter),
    )
    search_fields = [
        "id",
        "country_name",
        "abbr",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Datatype)
class DatatypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "description",
        "data_type",
        "comments",
    ]
    fields = [
        "description",
        "data_type",
        "comments",
    ]


@admin.register(Fossil)
class FossilAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "fossil_or_extant",
        "abbr",
        "comments",
    ]
    fields = [
        "fossil_or_extant",
        "abbr",
        "comments",
    ]


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "institute_name",
        "abbr",
        "institute_department",
        "locality",
    ]
    fields = [
        "institute_name",
        "abbr",
        "institute_department",
        "locality",
    ]
    list_filter = (
        ("institute_name", DropdownFilter),
        ("abbr", DropdownFilter),
        ("locality__locality_name", DropdownFilter),
    )
    search_fields = [
        "institute_name",
        "abbr",
        "institute_department",
        "locality__locality_name",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Laterality)
class LateralityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "laterality",
        "abbr",
    ]
    fields = [
        "laterality",
        "abbr",
    ]


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "locality_name",
        "continent",
        "country",
        "latitude",
        "longitude",
        "site_unit",
        "plus_minus",
        "age",
        "comments",
    ]
    fields = [
        "locality_name",
        "continent",
        "country",
        "latitude",
        "longitude",
        "site_unit",
        "plus_minus",
        "age",
        "comments",
    ]
    list_filter = (
        ("locality_name", DropdownFilter),
        ("continent__continent_name", DropdownFilter),
        ("country__country_name", DropdownFilter),
        ("age", DropdownFilter),
    )
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Observer)
class ObserverAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "researcher_name",
        "initials",
        "comments",
    ]
    fields = [
        "researcher_name",
        "initials",
        "comments",
    ]
    list_filter = (("researcher_name", DropdownFilter), ("initials", DropdownFilter))
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Original)
class OriginalAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "original_or_cast",
        "abbr",
    ]
    fields = [
        "original_or_cast",
        "abbr",
    ]


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "comments",
    ]
    fields = [
        "label",
        "comments",
    ]
    search_fields = ["label", "comments"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(TaxonomicRank)
class TaxonomicRankAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "rank",
        "comments",
    ]
    fields = [
        "rank",
        "comments",
    ]
    list_filter = (("rank", DropdownFilter),)
    search_fields = ["rank", "comments"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "observer",
        "specimen",
        "protocol",
        "original",
        "iteration",
        "comments",
        "filename",
    ]
    fields = [
        "observer",
        "specimen",
        "protocol",
        "original",
        "iteration",
        "comments",
        "filename",
    ]
    list_filter = (
        ("observer__researcher_name", DropdownFilter),
        ("specimen__hypocode", DropdownFilter),
        ("protocol__label", DropdownFilter),
        ("filename", DropdownFilter),
    )
    search_fields = [
        "researcher_name",
        "abbr",
        "institute_dept",
        "locality__locality_name",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Sex)
class SexAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "sex",
        "abbr",
        "comments",
    ]
    fields = [
        "sex",
        "abbr",
        "comments",
    ]


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "hypocode",
        "taxon",
        "institute",
        "catalog_number",
        "mass",
        "specimen_type",
        "locality",
        "sex",
        "age_class",
        "fossil",
        "captive",
        "comments",
    ]
    fields = (
        "hypocode",
        "taxon",
        "institute",
        "catalog_number",
        "mass",
        "specimen_type",
        "locality",
        "sex",
        "age_class",
        "fossil",
        "captive",
        "comments",
    )
    list_filter = (
        ("taxon__taxon_name", DropdownFilter),
        ("institute__institute_name", DropdownFilter),
        ("sex__sex", DropdownFilter),
        ("specimen_type__specimen_type", DropdownFilter),
        ("age_class__age_class", DropdownFilter),
        ("captive__captive_or_wild", DropdownFilter),
        ("fossil__fossil_or_extant", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(SpecimenType)
class SpecimenTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "specimen_type",
        "abbr",
        "comments",
    ]
    fields = [
        "specimen_type",
        "abbr",
        "comments",
    ]


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "taxon_name",
        "parent",
        "taxonomic_rank",
        "fossil",
        "comments",
    ]
    fields = [
        "taxon_name",
        "parent",
        "taxonomic_rank",
        "fossil",
        "comments",
    ]
    list_filter = (
        ("taxon_name", DropdownFilter),
        ("parent__taxon_name", DropdownFilter),
        ("taxonomic_rank__rank", DropdownFilter),
    )
    search_fields = [
        "id",
        "taxon_name",
        "parent__taxon_name",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "variable_name",
        "laterality",
        "datatype",
        "paired_with",
        "comments",
    ]
    fields = [
        "label",
        "variable_name",
        "laterality",
        "datatype",
        "paired_with",
        "comments",
    ]
    list_filter = (
        ("label", DropdownFilter),
        ("variable_name", DropdownFilter),
        ("laterality__label", DropdownFilter),
        ("datatype__data_table", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True
