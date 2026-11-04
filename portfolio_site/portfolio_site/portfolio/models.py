from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    THEME_CHOICES = [
        ("light", _("Light")),
        ("dark", _("Dark")),
        ("midnight", _("Midnight")),
    ]
    DEGREE_CHOICES = [
        ("Bachelor's", _("Bachelor's")),
        ("Master's", _("Master's")),
    ]
    EDUCATION_CHOICES = [
        ("High school diploma", _("High school diploma")),
        ("Bachelor's degree", _("Bachelor's degree")),
        ("Master's degree", _("Master's degree")),
        ("Other", _("Other")),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    study_goal = models.CharField(max_length=200, blank=True)
    preferred_focus = models.CharField(max_length=80, blank=True)
    preferred_language = models.CharField(max_length=50, blank=True)
    country_of_origin = models.CharField(max_length=80, blank=True)
    education_level = models.CharField(max_length=80, choices=EDUCATION_CHOICES, blank=True)
    desired_degree = models.CharField(max_length=40, choices=DEGREE_CHOICES, blank=True)
    preferred_subject = models.CharField(max_length=100, blank=True)
    university_city = models.CharField(max_length=80, blank=True)
    planned_start_date = models.DateField(null=True, blank=True)
    certificate_recognition = models.CharField(max_length=10, blank=True)
    studienkolleg_required = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="light")
    email_notifications = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class StudentDocument(models.Model):
    CATEGORY_CHOICES = [
        ("certificate", _("Certificate")),
        ("passport", _("Passport")),
        ("language", _("Language proof")),
        ("transcript", _("Transcript")),
        ("motivation", _("Motivation letter")),
        ("visa", _("Visa")),
        ("other", _("Other")),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    document = models.FileField(upload_to="student_documents/%Y/%m/%d/")
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class UniversityListing(models.Model):
    INSTITUTION_TYPES = [
        ("University", _("University")),
        ("University of Applied Sciences", _("University of Applied Sciences")),
        ("Studienkolleg", _("Studienkolleg")),
        ("Private institution", _("Private institution")),
    ]

    name = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    subject = models.CharField(max_length=100)
    degree = models.CharField(max_length=50)
    institution_type = models.CharField(max_length=40, choices=INSTITUTION_TYPES, default="University")
    language = models.CharField(max_length=40, default="German")
    admission_requirements = models.TextField(default="Official transcript and language proof")
    application_deadline = models.CharField(max_length=80, blank=True)
    tuition_fee = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    CATEGORIES = [
        ("framework", "Frameworks"),
        ("backend", "Backend"),
        ("database", "Databases"),
        ("tool", "Tools"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default="other")

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, related_name="projects", blank=True)
    repo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
