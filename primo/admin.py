from django.contrib import admin
from django.db import models
from django.forms import Textarea

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
    Device,
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
    Taxon,
    TaxonomicRank,
    TaxonomicType,
    Variable,
)

# Register your models here.

COMMENT_FIELD_OVERRIDE = {"widget": Textarea(attrs={"rows": 3})}


@admin.register(DataScalar)
class DataScalarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session_id",
        "variable_label",
        "value",
    )
    fields = (
        "session",
        "variable",
        "value",
    )
    search_fields = [
        "id",
    ]
    actions_on_top = True
    actions_on_bottom = True

    def variable_label(self, model_instance: DataScalar) -> Variable:
        return model_instance.variable

    def session_id(self, model_instance: DataScalar) -> Session:
        return model_instance.session


@admin.register(Ageclass)
class AgeclassAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "age_class",
        "abbr",
        "comments",
    ]
    fields = [
        "age_class",
        "abbr",
        "comments",
    ]
    list_editable = [
        "age_class",
        "abbr",
        "comments",
    ]
    search_fields = [
        "id",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


@admin.register(Data3D)
class Data3DAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session_id",
        "variable_label",
        "datindex",
        "x",
        "y",
        "z",
    ]
    list_filter = ["variable", "datindex"]
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

    def variable_label(self, model_instance: Data3D) -> Variable:
        return model_instance.variable

    def session_id(self, model_instance: Data3D) -> Session:
        return model_instance.session


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
        "captive_or_wild",
        "abbr",
        "comments",
    ]
    fields = [
        "captive_or_wild",
        "abbr",
        "comments",
    ]
    list_editable = [
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


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
    list_editable = [
        "continent_name",
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


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
    list_editable = [
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }
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
    list_editable = [
        "description",
        "data_type",
        "comments",
    ]
    list_filter = ["data_type"]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }
    list_editable = [
        "data_type",
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["id", "label"]
    fields = [
        "id",
        "label",
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
    list_editable = [
        "fossil_or_extant",
        "abbr",
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


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
        # "latitude",
        # "longitude",
        "comments",
    ]
    fields = [
        "locality_name",
        "continent",
        "country",
        "latitude",
        "longitude",
        "comments",
    ]
    list_filter = (
        ("locality_name", DropdownFilter),
        ("continent__continent_name", DropdownFilter),
        ("country__country_name", DropdownFilter),
    )
    search_fields = ["locality_name", "continent", "country"]
    list_editable = [
        "comments",
    ]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }
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
    list_editable = ["researcher_name", "initials", "comments"]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }
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
    list_editable = ["original_or_cast", "abbr"]


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
    search_fields = ["label", "abbr", "institute_dept", "locality__locality_name"]
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
        "taxonomic_type",
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
        "taxonomic_type",
        "locality",
        "sex",
        "age_class",
        "fossil",
        "captive",
        "comments",
    )
    list_filter = (
        ("taxon__label", DropdownFilter),
        ("institute__institute_name", DropdownFilter),
        ("sex__sex", DropdownFilter),
        ("taxonomic_type__taxonomic_type", DropdownFilter),
        ("age_class__age_class", DropdownFilter),
        ("captive__captive_or_wild", DropdownFilter),
        ("fossil__fossil_or_extant", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(TaxonomicType)
class TaxonomicTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "taxonomic_type",
        "abbr",
        "comments",
    ]
    fields = [
        "taxonomic_type",
        "abbr",
        "comments",
    ]
    list_editable = ["taxonomic_type", "abbr", "comments"]
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }


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
        ("taxonomic_rank__rank", DropdownFilter),
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
        "variable_name",
        "laterality",
        "datatype",
        "paired_with",
        "comments",
    ]
    list_editable = [
        # "label",
        # "variable_name",
        "laterality",
        "datatype",
        # "paired_with",
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
        ("laterality__laterality", DropdownFilter),
        ("datatype__data_type", DropdownFilter),
    )
    search_fields = ["id"]
    actions_on_top = True
    actions_on_bottom = True
    formfield_overrides = {
        models.TextField: COMMENT_FIELD_OVERRIDE,
    }
