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
    Rank,
    Session,
    Sex,
    Specimen,
    SpecimenType,
    Taxon,
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
        "name",
    )
    list_filter = (("variable__name", DropdownFilter), ("session__id", DropdownFilter))
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Ageclass)
class AgeclassAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
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
        "name",
        "parent",
        "comments",
    ]
    fields = [
        "name",
        "parent",
        "comments",
    ]
    list_filter = (("name", DropdownFilter),)
    search_fields = ["id", "name"]
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
        ("variable__name", DropdownFilter),
        ("bodypart__name", DropdownFilter),
    )
    search_fields = ["id", "variable", "bodypart"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Captive)
class CaptiveAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
        "comments",
    ]
    fields = [
        "name",
        "abbr",
        "comments",
    ]


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "comments",
    ]
    fields = [
        "name",
        "comments",
    ]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
        "comments",
    ]
    fields = [
        "name",
        "abbr",
        "comments",
    ]
    list_filter = (
        ("name", DropdownFilter),
        ("abbr", DropdownFilter),
    )
    search_fields = [
        "id",
        "name",
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
        "name",
        "abbr",
        "comments",
    ]
    fields = [
        "name",
        "abbr",
        "comments",
    ]


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
        "institute_department",
        "locality",
    ]
    fields = [
        "name",
        "abbr",
        "institute_department",
        "locality",
    ]
    list_filter = (
        ("name", DropdownFilter),
        ("abbr", DropdownFilter),
        ("locality__name", DropdownFilter),
    )
    search_fields = ["name", "abbr", "institute_department", "locality__name"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Laterality)
class LateralityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
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
        "name",
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
        "name",
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
        ("name", DropdownFilter),
        ("continent__name", DropdownFilter),
        ("country__name", DropdownFilter),
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
        "name",
        "initials",
        "comments",
    ]
    fields = [
        "name",
        "initials",
        "comments",
    ]
    list_filter = (("name", DropdownFilter), ("initials", DropdownFilter))
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Original)
class OriginalAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
    ]
    fields = [
        "name",
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


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "comments",
    ]
    fields = [
        "name",
        "comments",
    ]
    list_filter = (("name", DropdownFilter),)
    search_fields = ["name", "comments"]
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
        ("observer__name", DropdownFilter),
        ("specimen__hypocode", DropdownFilter),
        ("protocol__label", DropdownFilter),
        ("filename", DropdownFilter),
    )
    search_fields = ["name", "abbr", "institute_dept", "locality__name"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Sex)
class SexAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
        "comments",
    ]
    fields = [
        "name",
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
        ("taxon__name", DropdownFilter),
        ("institute__name", DropdownFilter),
        ("sex__name", DropdownFilter),
        ("specimen_type__name", DropdownFilter),
        ("age_class__name", DropdownFilter),
        ("captive__name", DropdownFilter),
        ("fossil__name", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(SpecimenType)
class SpecimenTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "abbr",
        "comments",
    ]
    fields = [
        "name",
        "abbr",
        "comments",
    ]


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "parent",
        "rank",
        "fossil",
        "comments",
    ]
    fields = [
        "name",
        "parent",
        "rank",
        "fossil",
        "comments",
    ]
    list_filter = (
        ("name", DropdownFilter),
        ("parent__name", DropdownFilter),
        ("rank__name", DropdownFilter),
    )
    search_fields = [
        "id",
        "name",
        "parent__name",
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
        ("name", DropdownFilter),
        ("label", DropdownFilter),
        ("laterality__laterality", DropdownFilter),
        ("datatype__data_table", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True
