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
        "label",
    )
    list_filter = (("variable__label", DropdownFilter), ("session__id", DropdownFilter))
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Ageclass)
class AgeclassAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
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
        "label",
        "parent",
        "comments",
    ]
    fields = [
        "label",
        "parent",
        "comments",
    ]
    list_filter = (("label", DropdownFilter),)
    search_fields = ["id", "label"]
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
        ("bodypart__label", DropdownFilter),
    )
    search_fields = ["id", "variable", "bodypart"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Captive)
class CaptiveAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "comments",
    ]
    fields = [
        "label",
        "abbr",
        "comments",
    ]


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "comments",
    ]
    fields = [
        "label",
        "comments",
    ]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "comments",
    ]
    fields = [
        "label",
        "abbr",
        "comments",
    ]
    list_filter = (
        ("label", DropdownFilter),
        ("abbr", DropdownFilter),
    )
    search_fields = [
        "id",
        "label",
        "abbr",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Datatype)
class DatatypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "data_table",
        "comments",
    ]
    fields = [
        "label",
        "data_table",
        "comments",
    ]


@admin.register(Fossil)
class FossilAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "comments",
    ]
    fields = [
        "label",
        "abbr",
        "comments",
    ]


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "institute_department",
        "locality",
    ]
    fields = [
        "label",
        "abbr",
        "institute_department",
        "locality",
    ]
    list_filter = (
        ("label", DropdownFilter),
        ("abbr", DropdownFilter),
        ("locality__label", DropdownFilter),
    )
    search_fields = ["label", "abbr", "institute_department", "locality__label"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Laterality)
class LateralityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
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
        "label",
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
        "label",
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
        ("label", DropdownFilter),
        ("continent__label", DropdownFilter),
        ("country__label", DropdownFilter),
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
        "label",
        "abbr",
    ]
    fields = [
        "label",
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
        "label",
        "comments",
    ]
    fields = [
        "label",
        "comments",
    ]
    list_filter = (("label", DropdownFilter),)
    search_fields = ["label", "comments"]
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
        ("observer__label", DropdownFilter),
        ("specimen__hypocode", DropdownFilter),
        ("protocol__label", DropdownFilter),
        ("filename", DropdownFilter),
    )
    search_fields = ["label", "abbr", "institute_dept", "locality__label"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Sex)
class SexAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "comments",
    ]
    fields = [
        "label",
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
        ("taxon__label", DropdownFilter),
        ("institute__label", DropdownFilter),
        ("sex__label", DropdownFilter),
        ("specimen_type__label", DropdownFilter),
        ("age_class__label", DropdownFilter),
        ("captive__label", DropdownFilter),
        ("fossil__label", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(SpecimenType)
class SpecimenTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "abbr",
        "comments",
    ]
    fields = [
        "label",
        "abbr",
        "comments",
    ]


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "parent",
        "taxonomic_rank",
        "fossil",
        "comments",
    ]
    fields = [
        "label",
        "parent",
        "taxonomic_rank",
        "fossil",
        "comments",
    ]
    list_filter = (
        ("label", DropdownFilter),
        ("parent__label", DropdownFilter),
        ("taxonomic_rank__label", DropdownFilter),
    )
    search_fields = [
        "id",
        "label",
        "parent__label",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "label",
        "name",
        "laterality",
        "datatype",
        "paired_with",
        "comments",
    ]
    fields = [
        "label",
        "name",
        "laterality",
        "datatype",
        "paired_with",
        "comments",
    ]
    list_filter = (
        ("label", DropdownFilter),
        ("name", DropdownFilter),
        ("laterality__label", DropdownFilter),
        ("datatype__data_table", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True
