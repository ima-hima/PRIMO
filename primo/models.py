# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AgeClass(models.Model):
    age_class = models.CharField('Age class',    max_length=50, blank=True, null=True)
    abbr      = models.CharField("Abbreviation", max_length=50, blank=True, null=True)
    comments  = models.TextField(                               blank=True, null=True)

    def __str__(self):
        return self.age_class

    class Meta:
        managed             = True
        db_table            = 'ageclass'
        verbose_name_plural = "age classes"


class AuthGroup(models.Model):
    name        = models.CharField(max_length=80,            unique=True)
    description = models.CharField(max_length=80, null=True)

    class Meta:
        managed  = True
        db_table = 'auth_group'


class AuthPermission(models.Model):
    name         = models.CharField (                    max_length=255)
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.PROTECT)
    codename     = models.CharField (                    max_length=100)

    class Meta:
        managed         = True
        # db_table        = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthGroupPermissions(models.Model):
    group      = models.ForeignKey(AuthGroup, on_delete=models.PROTECT)
    permission = models.ForeignKey(AuthPermission, on_delete=models.PROTECT)

    class Meta:
        managed         = True
        # db_table        = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthUser(models.Model):
    password     = models.CharField    ( max_length=128)
    last_login   = models.DateTimeField(                 blank=True, null=True)
    is_superuser = models.IntegerField ()
    username     = models.CharField    (max_length=30,                          unique=True )
    first_name   = models.CharField    (max_length=30)
    last_name    = models.CharField    (max_length=30)
    email        = models.CharField    (max_length=254)
    is_staff     = models.IntegerField ()
    is_active    = models.IntegerField ()
    date_joined  = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user  = models.ForeignKey(AuthUser,  on_delete=models.PROTECT)
    group = models.ForeignKey(AuthGroup, on_delete=models.PROTECT)

    class Meta:
        managed         = True
        # db_table        = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user       = models.ForeignKey(AuthUser,       on_delete=models.PROTECT)
    permission = models.ForeignKey(AuthPermission, on_delete=models.PROTECT)

    class Meta:
        managed         = True
        # db_table        = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Bodypart(models.Model):
    name           = models.CharField   ('Bodypart name',   max_length=191, blank=True,  null=True,                unique=True)
    parent         = models.ForeignKey  ('Bodypart',                              null=True, on_delete=models.PROTECT, verbose_name="Parent Bodypart")
    expand_in_tree = models.BooleanField(                                   blank=False, null=False, default=False)
    tree_root      = models.BooleanField(                                   blank=False, null=False, default=False)
    comments       = models.TextField   (                                   blank=True,  null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'bodypart'
        ordering = ['id']


class BodypartVariable(models.Model):
    variable = models.ForeignKey('Variable', on_delete=models.PROTECT)
    bodypart = models.ForeignKey('Bodypart', on_delete=models.PROTECT)

    class Meta:
        managed      = True
        db_table     = 'bodypart_variable'
        verbose_name = 'Bodypart-variable link'
        ordering     = ['id']


class Captive(models.Model):
    CHOICES  = ( ('captive', 'captive'), ('wild-caught', 'wild-caught'), ('probably captive', 'probably captive'), )
    name     = models.CharField('Captive or wild-caught', max_length=16, blank=True, null=True, choices=CHOICES)
    abbr     = models.CharField('Abbreviation',           max_length=2,  blank=True, null=True)
    comments = models.TextField(                                         blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed             = True
        db_table            = 'captive'
        verbose_name_plural = 'captive'
        ordering            = ['id']


class Continent(models.Model):
    name     = models.CharField('Continent name', max_length=32, blank=True, null=True, unique=True)
    comments = models.TextField(                                 blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'continent'


class Country(models.Model):
    name     = models.CharField('Country name', max_length=191, blank=True, null=True, unique=True)
    abbr     = models.CharField('Abbreviation', max_length=8,   blank=True, null=True, unique=True)
    comments = models.TextField(                                blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed             = True
        db_table            = 'country'
        verbose_name_plural = 'countries'
        ordering            = ['name']


class Data3D(models.Model):
    session  = models.ForeignKey  ('Session',  on_delete=models.PROTECT)
    variable = models.ForeignKey  ('Variable', on_delete=models.PROTECT)
    datindex = models.IntegerField(            blank=True, null=True)
    x        = models.FloatField  (            blank=True, null=True)
    y        = models.FloatField  (            blank=True, null=True)
    z        = models.FloatField  (            blank=True, null=True)

    class Meta:
        managed             = True
        db_table            = 'data3d'
        verbose_name_plural = '3D data'
        verbose_name        = '3D data'


class Datatype(models.Model):
    TYPES = (
        ('scalar',   'scalar' ),
        ('data3d',   '3D data'),
        ('external', 'external'),
    )
    label      = models.CharField(             max_length=255, blank=True, null=True)
    data_table = models.CharField('Data type', max_length=32,  blank=True, null=True, choices=TYPES)
    comments   = models.TextField(                             blank=True, null=True)

    def __str__(self):
        return self.data_table

    class Meta:
        managed  = True
        db_table = 'datatype'
        ordering = ['id']


class Device(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'device'


class DjangoAdminLog(models.Model):
    action_time    = models.DateTimeField    ()
    object_id      = models.TextField        (                                     blank=True, null=True)
    object_repr    = models.CharField        (                     max_length=200)
    action_flag    = models.SmallIntegerField()
    change_message = models.TextField        ()
    content_type   = models.ForeignKey       ('DjangoContentType',                 blank=True, null=True, on_delete=models.PROTECT)
    user           = models.ForeignKey       (AuthUser, on_delete=models.PROTECT)

    class Meta:
        managed  = True
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model     = models.CharField(max_length=100)

    class Meta:
        managed         = True
        db_table        = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app     = models.CharField(max_length=255)
    name    = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed  = True
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed  = True
        db_table = 'django_session'


class Fossil(models.Model):
    name     = models.CharField('Fossil or Extant',  max_length=16, blank=True, null=True)
    abbr     = models.CharField("Abbreviation",      max_length=2,  blank=True, null=True)
    comments = models.TextField(                                    blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed             = True
        db_table            = 'fossil'
        ordering            = ['id']
        verbose_name        = 'Fossil or Extant'
        verbose_name_plural = 'Fossil or Extant'


class Institute(models.Model):
    abbr           = models.CharField ('Abbreviation', max_length=8,   blank=True, null=True)
    name           = models.CharField ('Institute',    max_length=255, blank=True, null=True)
    institute_dept = models.CharField ('Department',   max_length=255, blank=True, null=True)
    locality       = models.ForeignKey('Locality', on_delete=models.PROTECT)
    comments       = models.TextField (                                blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'institute'
        ordering = ['name']


class IslandRegion(models.Model):
    name     = models.CharField('Region Name', max_length=255, blank=True, null=True)
    comments = models.TextField(                               blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed      = True
        db_table     = 'island_region'
        ordering     = ['name']
        verbose_name = 'Island region'


class Laterality(models.Model):
    CHOICES = ( ('none', 'none'),
                ('transverse', 'transverse'),
                ('median', 'median'),
                ('right', 'right'),
                ('left', 'left'), )
    laterality = models.CharField(                max_length=255, blank=True, null=True, choices=CHOICES)
    abbr       = models.CharField('Abbreviation', max_length=1,   blank=True, null=True)
    comments   = models.TextField(                                blank=True, null=True)

    def __str__(self):
        return self.laterality

    class Meta:
        managed             = True
        db_table            = 'laterality'
        verbose_name_plural = 'laterality'


class Locality(models.Model):
    name           = models.CharField ('Locality',      max_length=191, blank=True, null=True)
    state_province = models.ForeignKey('StateProvince',                             null=True, on_delete=models.PROTECT)
    continent      = models.ForeignKey('Continent', on_delete=models.PROTECT)
    island_region  = models.ForeignKey('IslandRegion',                              null=True, on_delete=models.PROTECT)
    latitude       = models.FloatField(                                 blank=True, null=True)
    longitude      = models.FloatField(                                 blank=True, null=True)
    site_unit      = models.CharField (                 max_length=255, blank=True, null=True)
    plus_minus     = models.FloatField(                                 blank=True, null=True)
    age            = models.FloatField(                                 blank=True, null=True)
    comments       = models.TextField (                                 blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed             = True
        db_table            = 'locality'
        verbose_name_plural = 'localities'


class Observer(models.Model):
    name     = models.CharField(max_length=191, blank=True, null=True, unique=True)
    initials = models.CharField(max_length=4,   blank=True, null=True, unique=True)
    comments = models.TextField(                blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'observer'
        ordering = ['id']


class Original(models.Model):
    CHOICES  = ( ('original', 'original'), ('cast', 'cast'), )
    name     = models.CharField('Type',         max_length=16, blank=True, null=True, choices=CHOICES)
    abbr     = models.CharField("Abbreviation", max_length=2,  blank=True, null=True)
    comments = models.TextField(                               blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'original'
        ordering = ['id']


class Paired(models.Model):
    CHOICES  = ( ('Paired', 'Paired'), ('Unpaired', 'Unpaired'))
    name     = models.CharField('Type',         max_length=64, blank=True, null=True, choices=CHOICES)
    abbr     = models.CharField('Abbreviation', max_length=1,  blank=True, null=True)
    comments = models.TextField(                                      blank=True, null=True)

    def __str__(self):
        return self.label

    class Meta:
        managed             = True
        db_table            = 'paired'
        verbose_name_plural = 'paired'


class ProtocolVariable(models.Model):
    protocol = models.ForeignKey('Protocol', on_delete=models.PROTECT)
    variable = models.ForeignKey('Variable', on_delete=models.PROTECT)

    class Meta:
        managed      = True
        db_table     = 'protocol_variable'
        verbose_name = 'Protocol-variable link'
        ordering     = ['id']


class Protocol(models.Model):
    label    = models.CharField('Protocol label', max_length=255, blank=True, null=True)
    comments = models.TextField(                                  blank=True, null=True)

    def __str__(self):
        return self.label

    class Meta:
        managed  = True
        db_table = 'protocol'
        ordering = ['id']



# class QueryWizard(models.Model):
#     query_name = models.CharField(max_length=100, blank=True, null=True)
#     query_friendly_name = models.CharField(max_length=255, blank=True, null=True)
#     query_description = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = 'query_wizard'


class QueryWizardQuery(models.Model):
    query_type   = models.CharField(max_length=20, blank=True, null=True)
    query        = models.TextField(               blank=True, null=True)
    query_suffix = models.TextField(               blank=True, null=True)

    class Meta:
        managed  = True
        db_table = 'query_wizard_query'


class QueryWizardTable(models.Model):
    query_wizard_query = models.ForeignKey  ('QueryWizardQuery',                                         related_name='tables', on_delete=models.PROTECT)
    display_name       = models.CharField   (                  max_length=100, blank=True,  null=True)
    filter_table_name  = models.CharField   (                  max_length=50,  blank=True,  null=True)
    display_order      = models.IntegerField(                                  blank=True,  null=True)
    preselected        = models.BooleanField(                                  blank=False, null=False, default=False)

    class Meta:
        managed  = True
        db_table = 'query_wizard_table'


class Rank(models.Model):
    name     = models.CharField('Rank name', max_length=255, blank=True, null=True)
    comments = models.TextField(                             blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'rank'
        ordering = ['id']


class Scalar(models.Model):
    session  = models.ForeignKey('Session',  on_delete=models.PROTECT)
    variable = models.ForeignKey('Variable', on_delete=models.PROTECT)
    value    = models.CharField (max_length=10, blank=True, null=True)

    class Meta:
        managed             = True
        db_table            = 'scalar'
        verbose_name_plural = 'scalar'
        ordering            = ['id']


class Session(models.Model):
    observer  = models.ForeignKey  ('Observer', on_delete=models.PROTECT)
    specimen  = models.ForeignKey  ('Specimen', on_delete=models.PROTECT)
    protocol  = models.ForeignKey  ('Protocol', on_delete=models.PROTECT)
    original  = models.ForeignKey  ('Original', on_delete=models.PROTECT, verbose_name="Original or Cast")
    iteration = models.IntegerField(                                        blank=True, null=True)
    comments  = models.TextField   (                                        blank=True, null=True)
    filename  = models.CharField   (                        max_length=255, blank=True, null=True)
    group     = models.ForeignKey  ('AuthGroup', default=3, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    class Meta:
        managed  = True
        db_table = 'session'
        ordering = ['id']


class Sex(models.Model):
    CHOICES = ( ('male',            'male'),
                ('female',          'female'),
                ('male?',           'male?'),
                ('female?',         'female?'),
                ('possibly male',   'possibly male'),
                ('possibly female', 'possibly female'),
                ('unknown',         'unknown'),
              )
    name     = models.CharField('Sex',              max_length=16, blank=True, null=True, choices=CHOICES)
    abbr     = models.CharField('Abbreviation', max_length=2,  blank=True, null=True)
    comments = models.TextField(                                   blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        managed             = True
        db_table            = 'sex'
        verbose_name_plural = 'sexes'
        ordering            = ['id']


class Specimen(models.Model):
    hypocode       = models.CharField   (                    max_length=20, blank=True, null=True)
    taxon          = models.ForeignKey  ('Taxon',        on_delete=models.PROTECT)
    institute      = models.ForeignKey  ('Institute',    on_delete=models.PROTECT)
    catalog_number = models.CharField   (                    max_length=64, blank=True, null=True)
    mass           = models.IntegerField(                                   blank=True, null=True)
    locality       = models.ForeignKey  ('Locality',     on_delete=models.PROTECT)
    sex            = models.ForeignKey  ('Sex',          on_delete=models.PROTECT)
    ageclass       = models.ForeignKey  ('AgeClass',     on_delete=models.PROTECT)
    fossil         = models.ForeignKey  ('Fossil',       on_delete=models.PROTECT)
    captive        = models.ForeignKey  ('Captive',      on_delete=models.PROTECT)
    specimentype   = models.ForeignKey  ('SpecimenType', on_delete=models.PROTECT)
    comments       = models.TextField   (                                   blank=True, null=True)

    def __str__(self):
        return self.hypocode

    class Meta:
        managed  = True
        db_table = 'specimen'
        ordering = ['id']


class SpecimenType(models.Model):
    name     = models.CharField('Specimen Type', max_length=16, blank=True, null=True)
    abbr     = models.CharField('Abbreviation',  max_length=2,  blank=True, null=True)
    comments = models.TextField(                                blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed      = True
        db_table     = 'type'
        ordering     = ['id']
        verbose_name = 'specimen type'


class StateProvince(models.Model):
    country  = models.ForeignKey('Country', on_delete=models.PROTECT)
    name     = models.CharField ('State',        max_length=255, blank=True, null=True)
    abbr     = models.CharField ('Abbreviation', max_length=8,   blank=True, null=True)
    comments = models.TextField (                                blank=True, null=True)

    class Meta:
        managed             = True
        db_table            = 'state_province'
        verbose_name        = 'State/province'
        verbose_name_plural = 'States/provinces'
        ordering            = ['name']


class Taxon(models.Model):
    parent         = models.ForeignKey  ('Taxon',  on_delete=models.PROTECT,                   null=True, verbose_name="Parent Taxon")
    rank           = models.ForeignKey  ('Rank',   on_delete=models.PROTECT)
    name           = models.CharField   ('Taxon name',            max_length=255, blank=True,  null=True)
    fossil         = models.ForeignKey  ('Fossil', on_delete=models.PROTECT)
    expand_in_tree = models.BooleanField(                                         blank=False, null=False, default=False)
    tree_root      = models.BooleanField(                                         blank=False, null=False, default=False)
    comments       = models.TextField   (                                         blank=True,  null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed             = True
        db_table            = 'taxon'
        verbose_name_plural = 'taxa'
        ordering            =['name']


class Variable(models.Model):
    label      = models.CharField (              max_length=32,  blank=True, null=True)
    name       = models.CharField (              max_length=255, blank=True, null=True)
    laterality = models.ForeignKey('Laterality',                                         on_delete=models.PROTECT)
    datatype   = models.ForeignKey('Datatype',                                           on_delete=models.PROTECT)
    pairing    = models.ForeignKey('Variable',                                null=True, on_delete=models.PROTECT)
    comments   = models.TextField (                               blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed  = True
        db_table = 'variable'
