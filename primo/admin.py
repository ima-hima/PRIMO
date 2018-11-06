from django.contrib import admin
from .models import AgeClass, Bodypart, BodypartVariable, Captive, Continent, Country, Data3D, Datatype, Fossil, Institute, IslandRegion, Laterality, Locality, Observer, Original, Paired, ProtocolVariable, Protocol, Rank, Scalar, Session, Sex, Specimen, StateProvince, Taxon, SpecimenType, Variable

# because filters.py is at top level, import from .filters
from .filters import DropdownFilter

# Register your models here.

@admin.register(Scalar)
class ScalarAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'variable', 'value', )
    fields = ('session', 'variable', 'name', )
    list_filter = (('variable__name', DropdownFilter), ('session__id', DropdownFilter))
    search_fields = ['id', ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(AgeClass)
class AgeClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['age_class', 'abbr', 'comments', ]
    search_fields = ['id', ]


@admin.register(Data3D)
class Data3DAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'variable', 'datindex', 'x', 'y', 'z', ]
    fields = ['session', 'variable', 'datindex', 'x', 'y', 'z', ]
    search_fields = ['id', ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Bodypart)
class BodypartAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'comments', ]
    fields = ['name', 'parent', 'comments', ]
    list_filter = (('name', DropdownFilter), )
    search_fields = ['id', 'name']
    actions_on_top = True
    actions_on_bottom = True


@admin.register(BodypartVariable)
class BodypartVariableAdmin(admin.ModelAdmin):
    list_display = ['id', 'variable', 'bodypart', ]
    fields = ['variable', 'bodypart', ]
    list_filter = (('variable__name', DropdownFilter), ('bodypart__name', DropdownFilter))
    search_fields = ['id', 'variable', 'bodypart']
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Captive)
class CaptiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['name', 'abbr', 'comments', ]


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'comments', ]
    fields = ['name', 'comments', ]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['name', 'abbr', 'comments', ]
    list_filter = (('name', DropdownFilter), ('abbr', DropdownFilter), )
    search_fields = ['id', 'name', 'abbr', ]
    actions_on_top = True
    actions_on_bottom = True

@admin.register(Datatype)
class DatatypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'data_table', 'comments', ]
    fields = ['label', 'data_table', 'comments', ]


@admin.register(Fossil)
class FossilAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['name', 'abbr', 'comments', ]


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'institute_department', 'locality', ]
    fields = ['name', 'abbr', 'institute_department', 'locality', ]
    list_filter = (('name', DropdownFilter), ('abbr', DropdownFilter), ('locality__name', DropdownFilter), )
    search_fields = ['name', 'abbr', 'institute_department', 'locality__name' ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(IslandRegion)
class IslandRegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'comments', ]
    fields = ['name', 'comments', ]


@admin.register(Laterality)
class LateralityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', ]
    fields = ['laterality', 'abbr', ]


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'state_province', 'continent', 'island_region', 'latitude', 'longitude', 'site_unit', 'plus_minus', 'age', 'comments', ]
    fields = ['name', 'state_province', 'continent', 'island_region', 'latitude', 'longitude', 'site_unit', 'plus_minus', 'age', 'comments',  ]
    list_filter = (('name', DropdownFilter), ('state_province__name', DropdownFilter), ('continent__name', DropdownFilter), ('island_region__name', DropdownFilter), ('age', DropdownFilter), )
    search_fields = ['id', ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Observer)
class ObserverAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'initials', 'comments', ]
    fields = ['name', 'initials', 'comments', ]
    list_filter = (('name', DropdownFilter), ('initials', DropdownFilter))
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Original)
class OriginalAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', ]
    fields = ['name', 'abbr', ]


@admin.register(Paired)
class PairedAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['paired', 'abbr', 'comments', ]


@admin.register(ProtocolVariable)
class ProtocolVariableAdmin(admin.ModelAdmin):
    list_display = ['id', 'protocol', 'variable', ]
    fields = ['protocol', 'variable', ]
    list_filter = (('protocol__label', DropdownFilter), ('variable__name', DropdownFilter))
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'comments', ]
    fields = ['label', 'comments', ]
    search_fields = ['label', 'comments']
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'comments', ]
    fields = ['name', 'comments', ]
    list_filter = (('name', DropdownFilter), )
    search_fields = ['name', 'comments']
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'observer', 'specimen', 'protocol', 'original', 'iteration', 'comments', 'filename', ]
    fields = ['observer', 'specimen', 'protocol', 'original', 'iteration', 'comments', 'filename', ]
    list_filter = (('observer__name', DropdownFilter), ('specimen__hypocode', DropdownFilter), ('protocol__label', DropdownFilter), ('filename', DropdownFilter), )
    search_fields = ['name', 'abbr', 'institute_dept', 'locality__name' ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Sex)
class SexAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['name', 'abbr', 'comments', ]


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = ['id', 'hypocode', 'taxon', 'institute', 'catalog_number', 'mass', 'specimen_type', 'locality', 'sex', 'ageclass', 'fossil', 'captive', 'comments', ]
    fields = ('hypocode', 'taxon', 'institute', 'catalog_number', 'mass', 'specimentype', 'locality', 'sex', 'ageclass', 'fossil', 'captive', 'comments', )
    list_filter = (('taxon__name', DropdownFilter), ('institute__name', DropdownFilter), ('sex__name', DropdownFilter), ('specimentype__name', DropdownFilter), ('ageclass__age_class', DropdownFilter), ('captive__name', DropdownFilter), ('fossil__name', DropdownFilter), )
    search_fields = ['id']
    actions_on_top = True
    actions_on_bottom = True


@admin.register(SpecimenType)
class SpecimenTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbr', 'comments', ]
    fields = ['name', 'abbr', 'comments', ]


@admin.register(StateProvince)
class StateProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'name', 'abbr', 'comments', ]
    fields = ['country', 'name', 'abbr', 'comments', ]
    list_filter = (('country__name', DropdownFilter), ('name', DropdownFilter), ('abbr', DropdownFilter), )
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'rank', 'fossil', 'comments', ]
    fields = ['name', 'parent', 'rank', 'fossil', 'comments', ]
    list_filter = (('name', DropdownFilter), ('parent__name', DropdownFilter), ('rank__name', DropdownFilter), )
    search_fields = ['id', 'name', 'parent__name', ]
    actions_on_top = True
    actions_on_bottom = True


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'laterality', 'datatype', 'paired_with', 'comments', ]
    fields = ['label', 'name', 'laterality', 'datatype', 'pairing', 'comments', ]
    list_filter = (('name', DropdownFilter), ('label', DropdownFilter), ('laterality__laterality', DropdownFilter), ('datatype__data_table', DropdownFilter), )
    search_fields = ['id']
    actions_on_top = True
    actions_on_bottom = True
