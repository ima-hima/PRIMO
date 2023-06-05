from django.db import models

""" All auth models are generated by Django. """


class AuthGroup(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=80, null=True)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", on_delete=models.PROTECT)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey("AuthGroup", on_delete=models.PROTECT)
    permission = models.ForeignKey("AuthPermission", on_delete=models.PROTECT)

    class Meta:
        managed = False


#         db_table = 'auth_group_permissions'
#         # unique_together = (('group', 'permission'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    user = models.ForeignKey("AuthUser", on_delete=models.PROTECT)
    group = models.ForeignKey("AuthGroup", on_delete=models.PROTECT)

    class Meta:
        managed = False
        # db_table = 'auth_user_groups'
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey("AuthUser", on_delete=models.PROTECT)
    # permission = models.ForeignKey("AuthPermission", on_delete=models.PROTECT)

    class Meta:
        managed = True
        # db_table = 'auth_user_user_permissions'
        # unique_together = (('user', 'permission'),)


""" End of auth models generated by Django. """


class Ageclass(models.Model):
    """Ages, can include Infant, Juvenile, Adult, Unknown."""

    CLASS_CHOICES = (
        ("infant", "Infant"),
        ("juvenile", "Juvenile"),
        ("adult", "Adult"),
        ("unknown", "Unknown"),
    )
    ABBR_CHOICES = (("i", "I"), ("j", "J"), ("a", "A"), ("u", "U"))
    age_class = models.CharField(
        verbose_name="Age class", max_length=50, unique=True, choices=CLASS_CHOICES
    )
    abbr = models.CharField(
        verbose_name="Abbreviation", max_length=2, unique=True, choices=ABBR_CHOICES
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.age_class

    class Meta:
        db_table = "age_class"
        verbose_name_plural = "age classes"


class Bodypart(models.Model):
    """
    Bodyparts, including information on where it fits in the tree
    generated in the front end by nlstree.
    """

    label = models.CharField(verbose_name="Bodypart name", max_length=191, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Parent Bodypart",
    )
    """Whether the taxon should be expanded in the tree view."""
    expand_in_tree = models.BooleanField(blank=False, null=False, default=False)
    """Whether the taxon is the root of the tree in the tree view."""
    tree_root = models.BooleanField(blank=False, null=False, default=False)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        db_table = "bodypart"
        ordering = ["id"]


class BodypartVariable(models.Model):
    """Lookup table for which bodypart a given variable belongs to."""

    variable = models.ForeignKey("Variable", on_delete=models.PROTECT)
    bodypart = models.ForeignKey("Bodypart", on_delete=models.PROTECT)

    class Meta:
        db_table = "bodypart_variable"
        verbose_name = "Bodypart-variable link"
        ordering = ["id"]


class Captive(models.Model):
    """Whether the specimen was wild-caught or captive."""

    CHOICES = (
        ("captive", "Captive"),
        ("wild-caught", "Wild-caught"),
        ("probably captive", "Probably Captive"),
        ("unknown", "Unknown"),
    )
    captive_or_wild = models.CharField(
        verbose_name="Captive or wild-caught",
        max_length=16,
        blank=True,
        choices=CHOICES,
        default="unknown",
    )
    abbr = models.CharField(
        verbose_name="Abbreviation", max_length=2, blank=True, null=True
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.captive_or_wild

    class Meta:
        db_table = "captive"
        verbose_name_plural = "captive"
        ordering = ["id"]


class Continent(models.Model):
    """A list of the continents"""

    CHOICES = (
        ("Africa", "Africa"),
        ("Asia", "Asia"),
        ("Europe", "Europe"),
        ("Australia", "Australia"),
        ("North America", "North America"),
        ("South America", "South America"),
        ("Unknown", "Unknown"),
    )
    continent_name = models.CharField(
        verbose_name="Continent name",
        max_length=32,
        blank=True,
        unique=True,
        choices=CHOICES,
        default="unknown",
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.continent_name

    class Meta:
        db_table = "continent"


class Country(models.Model):
    """A list of possible countries."""

    country_name = models.CharField(
        verbose_name="Country name",
        max_length=191,
        blank=False,
        null=False,
        unique=False,
        default=10000,
    )
    abbr = models.CharField(
        "Abbreviation", max_length=8, blank=True, null=True, unique=True
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.country_name

    class Meta:
        db_table = "country"
        verbose_name_plural = "countries"
        ordering = ["country_name"]


class Data3D(models.Model):
    """Point data for three-dimensional model points in space."""

    session = models.ForeignKey("Session", on_delete=models.PROTECT)
    variable = models.ForeignKey("Variable", on_delete=models.PROTECT)
    datindex = models.IntegerField(blank=True, null=True)
    x = models.DecimalField(
        blank=True,  # Decimals because we're checking
        null=True,  # against strings with four
        decimal_places=4,  # digits: "9999.0000".
        max_digits=8,  # Actually less important,
        default=9999.0000,  # we're storing to four
    )  # decimal places.
    y = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=4,
        max_digits=8,
        default=9999.0000,
    )
    z = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=4,
        max_digits=8,
        default=9999.0000,
    )

    class Meta:
        db_table = "data_3d"
        verbose_name = "3D data"
        verbose_name_plural = "3D data"


class DataScalar(models.Model):
    """Scalar data for a given session and variable."""

    session = models.ForeignKey("Session", on_delete=models.PROTECT)
    variable = models.ForeignKey("Variable", on_delete=models.PROTECT)
    value = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "data_scalar"
        verbose_name = "Scalar data"
        verbose_name_plural = "Scalar data"
        ordering = ["id"]


class Datatype(models.Model):
    """Whether it's scalar, 3D or from an external data source."""

    TYPES = (
        ("scalar", "Scalar"),
        ("data3d", "3D data"),
        ("external", "External"),
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    data_type = models.CharField(
        "Data type",
        max_length=32,
        blank=True,
        choices=TYPES,
        default="scalar",
        null=False,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.data_type

    class Meta:
        db_table = "data_type"
        ordering = ["id"]
        verbose_name = "data type"


class Device(models.Model):
    """The device used to capture 3D points."""

    label = models.CharField(max_length=255, null=False)

    def __str__(self) -> str:
        return self.label


class DjangoAdminLog(models.Model):
    """Set by Django."""

    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    user = models.ForeignKey(
        "AuthUser",
        on_delete=models.PROTECT,
    )

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    """Set by Django."""

    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = True
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class Fossil(models.Model):
    """Type of specimen, fossil or not, including abbreviation."""

    CHOICES = [("fossil", "Fossil"), ("extant", "Extant"), ("unknown", "Unknown")]
    fossil_or_extant = models.CharField(
        verbose_name="Fossil or Extant",
        max_length=16,
        choices=CHOICES,
        default="fossil",
        unique=True,
    )
    abbr = models.CharField(
        verbose_name="Abbreviation",
        max_length=2,
        unique=True,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.fossil_or_extant

    class Meta:
        db_table = "fossil"
        ordering = ["id"]
        verbose_name = "Fossil or Extant"
        verbose_name_plural = "Fossil or Extant"


class Institute(models.Model):
    """Research institution with locality as foreign key."""

    abbr = models.CharField(
        verbose_name="Abbreviation",
        max_length=8,
        blank=True,
        null=True,
    )
    institute_name = models.CharField(
        verbose_name="Institute",
        max_length=255,
        blank=False,
        null=False,
    )
    institute_department = models.CharField(
        verbose_name="Department",
        max_length=255,
        blank=True,
        null=True,
    )
    locality = models.ForeignKey(
        "Locality",
        on_delete=models.SET_DEFAULT,
        blank=False,
        null=False,
        default=10000,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.institute_name

    class Meta:
        db_table = "institute"
        ordering = ["institute_name"]


class Laterality(models.Model):
    """Whether two 3D points are lateral, and which kind of laterality."""

    CHOICES = (
        ("none", "None"),
        ("transverse", "Transverse"),
        ("median", "Median"),
        ("right", "Right"),
        ("left", "Left"),
        ("unknown", "Unknown"),
    )
    laterality = models.CharField(
        verbose_name="Laterality",
        max_length=255,
        choices=CHOICES,
        default="unknown",
    )
    abbr = models.CharField(
        verbose_name="Abbreviation",
        max_length=1,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.laterality

    class Meta:
        db_table = "laterality"
        verbose_name_plural = "laterality"


class Locality(models.Model):
    """
    A locality is a small region marked by a latitude and longitude.
    Foreign keys: country and continent.
    """

    locality_name = models.CharField(
        verbose_name="Locality",
        max_length=191,
        null=False,
    )
    continent = models.ForeignKey("Continent", default=7, on_delete=models.SET_DEFAULT)
    country = models.ForeignKey("Country", default=10000, on_delete=models.SET_DEFAULT)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.locality_name

    class Meta:
        db_table = "locality"
        verbose_name_plural = "localities"
        ordering = ["locality_name"]


class Observer(models.Model):
    """Name of researcher who did measurement."""

    researcher_name = models.CharField(
        max_length=191,
        unique=True,
    )
    initials = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        unique=True,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.researcher_name

    class Meta:
        db_table = "observer"
        ordering = ["researcher_name"]


class Original(models.Model):
    """Whether a specimen is a cast or an original."""

    CHOICES = (
        ("original", "Original"),
        ("cast", "Cast"),
    )
    original_or_cast = models.CharField(
        verbose_name="Type",
        max_length=16,
        choices=CHOICES,
        default="original",
        unique=True,
    )
    abbr = models.CharField(
        verbose_name="Abbreviation",
        max_length=2,
        unique=True,
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.original_or_cast

    class Meta:
        db_table = "original"
        ordering = ["id"]


class Protocol(models.Model):
    """The protocol under which a measurement is made."""

    label = models.CharField(verbose_name="Protocol label", max_length=255)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        db_table = "protocol"
        ordering = ["id"]


# class QueryWizard(models.Model):
#     query_name = models.CharField(max_length=100, blank=True, null=True)
#     query_friendly_name = models.CharField(max_length=255, blank=True, null=True)
#     query_description = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = True


class QueryWizardQuery(models.Model):
    data_table = models.CharField(max_length=20, blank=True, null=True)
    query = models.TextField(blank=True, null=True)
    query_suffix = models.TextField(blank=True, null=True)


class QueryWizardTable(models.Model):
    """
    A list of tables that will be used during query setup parameter selection.
    """

    query_wizard_query = models.ForeignKey(
        "QueryWizardQuery",
        related_name="tables",
        on_delete=models.PROTECT,
    )
    # How the name of the table will be displayed.
    display_name = models.CharField(max_length=100, blank=True, null=True)
    # When we're filtering by table name, what string to use.
    filter_table_name = models.CharField(max_length=50, blank=True, null=True)
    # Which order to display the tables in.
    display_order = models.IntegerField(blank=True, null=True)
    # If all values from a table (e.g. fossil, sex) will be pre-selected when
    # calling parameter selection, this is True.
    preselected = models.BooleanField(blank=False, null=False, default=False)


class TaxonomicRank(models.Model):
    rank = models.CharField(verbose_name="Taxonomic rank", max_length=255)
    CHOICES = [
        ("semisuborder", "Semisuborder"),
        ("hyporder", "Hyporder"),
        ("infraorder", "Infraorder"),
        ("parvorder", "Parvorder"),
        ("superfamily", "Superfamily"),
        ("family", "Family"),
        ("subfamily", "Subfamily"),
        ("tribe", "Tribe"),
        ("subtribe", "Subtribe"),
        ("genus", "Genus"),
        ("subgenus", "Subgenus"),
        ("species", "Species"),
        ("subspecies", "Subspecies"),
        ("synonym", "Synonym"),
        ("hybrid", "Hybrid"),
        ("Site or regional pop.", "Site or regional pop."),
        ("class", "Class"),
        ("superorder", "Superorder"),
        ("order", "Order"),
        ("semiorder", "Semiorder"),
    ]
    comments = models.TextField(blank=True, null=True, choices=CHOICES)

    def __str__(self) -> str:
        return self.rank

    class Meta:
        db_table = "taxonomic_rank"
        ordering = ["id"]


class Session(models.Model):
    observer = models.ForeignKey("Observer", on_delete=models.PROTECT)
    specimen = models.ForeignKey("Specimen", on_delete=models.PROTECT)
    protocol = models.ForeignKey("Protocol", on_delete=models.PROTECT)
    original = models.ForeignKey(
        "Original",
        on_delete=models.PROTECT,
        verbose_name="Original or Cast",
    )
    iteration = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    group = models.ForeignKey("AuthGroup", default=3, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        db_table = "session"
        ordering = ["id"]


class Sex(models.Model):
    CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("male?", "Male?"),
        ("female?", "Female?"),
        ("possibly male", "Possibly male"),
        ("possibly female", "Possibly female"),
        ("unknown", "Unknown"),
    )
    sex = models.CharField(
        verbose_name="Sex",
        max_length=16,
        choices=CHOICES,
        default="unknown",
    )
    abbr = models.CharField(
        verbose_name="Abbreviation",
        max_length=2,
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.sex

    class Meta:
        db_table = "sex"
        verbose_name_plural = "sexes"
        ordering = ["id"]


class Taxon(models.Model):
    parent = models.ForeignKey(
        "Taxon",
        on_delete=models.PROTECT,
        null=False,
        verbose_name="Parent Taxon",
    )
    taxonomic_rank = models.ForeignKey("TaxonomicRank", on_delete=models.PROTECT)
    label = models.CharField(
        verbose_name="Taxon name",
        max_length=255,
        blank=True,
        null=False,
    )
    fossil = models.ForeignKey("Fossil", on_delete=models.PROTECT)
    expand_in_tree = models.BooleanField(blank=False, null=False, default=False)
    tree_root = models.BooleanField(blank=False, null=False, default=False)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        db_table = "taxon"
        verbose_name_plural = "taxa"
        ordering = ["label"]


class TaxonomicType(models.Model):
    CHOICES = (
        ("holotype", "Holotype"),
        ("lectotype", "Lectotype"),
        ("syntype", "Syntype"),
        ("neotype", "Neotype"),
        ("future neotype", "Future neotype"),
        ("future lectotype", "Future lectotype"),
        ("unknown", "Unknown"),
    )
    taxonomic_type = models.CharField(
        verbose_name="Type", max_length=16, choices=CHOICES, default="unknown"
    )
    abbr = models.CharField(
        verbose_name="Abbreviation", max_length=2, blank=True, null=True
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.taxonomic_type

    class Meta:
        db_table = "taxonomic_type"
        ordering = ["id"]
        verbose_name = "taxonomic type"


class Variable(models.Model):
    """
    Label for a group of measurements; which measurements exist on a
    given item.
    Foreign keys: datatype (scalar or 3D)
                  variable, which other variables it is paired with.
    """

    label = models.CharField(
        max_length=32, null=False
    )  # this is the id, set by biologists
    variable_name = models.CharField(max_length=255)
    laterality = models.ForeignKey(
        "Laterality",
        null=False,
        on_delete=models.PROTECT,
    )
    datatype = models.ForeignKey("Datatype", on_delete=models.PROTECT)
    paired_with = models.ForeignKey(
        "Variable",
        null=True,
        on_delete=models.PROTECT,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.variable_name

    class Meta:
        db_table = "variable"


class Specimen(models.Model):
    """
    Data for a given specimen, including where it originated, its
    institute and catalog number, mass, sex, age, comments, etc.
    Foreign keys: taxon
                  institute
                  locality
                  sex
                  age_class
                  fossil
                  captive
                  taxonomic type
    """

    hypocode = models.CharField(max_length=20, blank=True)
    taxon = models.ForeignKey("Taxon", on_delete=models.PROTECT)
    institute = models.ForeignKey(
        "Institute",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=10000,
    )
    catalog_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )
    mass = models.IntegerField(
        blank=False,
        null=False,
        default=0,
    )
    locality = models.ForeignKey(
        "Locality",
        on_delete=models.SET_DEFAULT,
        blank=False,
        null=False,
        default=10000,
    )
    sex = models.ForeignKey(
        "Sex",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=9,
    )
    age_class = models.ForeignKey(
        "Ageclass",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=9,
    )
    fossil = models.ForeignKey(
        "Fossil",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=9,
    )
    captive = models.ForeignKey(
        "Captive",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=9,
    )
    taxonomic_type = models.ForeignKey(
        "TaxonomicType",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        default=7,
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.hypocode

    class Meta:
        db_table = "specimen"
        ordering = ["id"]
