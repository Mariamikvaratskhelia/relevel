from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import StudentDocument, UniversityListing, UserProfile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label=_("First name"))
    last_name = forms.CharField(max_length=150, label=_("Last name"))
    email = forms.EmailField(label=_("Email address"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    country_of_origin = forms.CharField(max_length=80, label=_("Country of origin"))
    preferred_language = forms.ChoiceField(
        choices=[("English", _("English")), ("German", _("German"))],
        label=_("Preferred interface language"),
    )

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["first_name", "last_name", "email", "country_of_origin", "preferred_language", "password1", "password2"])
        placeholders = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "you@example.com",
            "country_of_origin": "Choose or enter your country",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "field", "autocomplete": "new-password" if name.startswith("password") else name.replace("_", "-")})
            if name in placeholders:
                field.widget.attrs["placeholder"] = _(placeholders[name])

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self._meta.model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.display_name = user.get_full_name()
            profile.country_of_origin = self.cleaned_data["country_of_origin"]
            profile.preferred_language = self.cleaned_data["preferred_language"]
            profile.save(update_fields=["display_name", "country_of_origin", "preferred_language", "updated_at"])
        return user


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "bio",
            "study_goal",
            "preferred_focus",
            "preferred_language",
            "country_of_origin",
            "education_level",
            "desired_degree",
            "preferred_subject",
            "university_city",
            "planned_start_date",
            "certificate_recognition",
            "studienkolleg_required",
            "theme",
            "email_notifications",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "field", "placeholder": "Your display name"}),
            "bio": forms.Textarea(attrs={"class": "field", "rows": 4, "placeholder": "Tell people a little about you"}),
            "study_goal": forms.TextInput(attrs={"class": "field", "placeholder": "e.g. Study Computer Science in Berlin"}),
            "preferred_focus": forms.TextInput(attrs={"class": "field", "placeholder": "e.g. Admissions"}),
            "preferred_language": forms.TextInput(attrs={"class": "field", "placeholder": "German"}),
            "country_of_origin": forms.TextInput(attrs={"class": "field", "placeholder": "Nigeria"}),
            "education_level": forms.Select(attrs={"class": "field"}),
            "desired_degree": forms.Select(attrs={"class": "field"}),
            "preferred_subject": forms.TextInput(attrs={"class": "field", "placeholder": "Computer Science"}),
            "university_city": forms.TextInput(attrs={"class": "field", "placeholder": "Berlin"}),
            "planned_start_date": forms.DateInput(attrs={"class": "field", "type": "date"}),
            "certificate_recognition": forms.Select(attrs={"class": "field"}, choices=[("yes", "Yes"), ("no", "No"), ("not sure", "Not sure")]),
            "studienkolleg_required": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "theme": forms.Select(attrs={"class": "field"}),
            "email_notifications": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
        labels = {
            "display_name": _("Display name"),
            "bio": _("Bio"),
            "study_goal": _("Study goal"),
            "preferred_focus": _("Preferred focus"),
            "preferred_language": _("Preferred interface language"),
            "country_of_origin": _("Country of origin"),
            "education_level": _("Current education level"),
            "desired_degree": _("Desired degree"),
            "preferred_subject": _("Preferred subject"),
            "university_city": _("Preferred university city"),
            "planned_start_date": _("Planned start date"),
            "certificate_recognition": _("Certificate recognition status"),
            "studienkolleg_required": _("Studienkolleg required"),
            "theme": _("Theme"),
            "email_notifications": _("Email notifications"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_language"] = forms.ChoiceField(
            required=False,
            label=_("Preferred interface language"),
            choices=[("", "---------"), ("English", _("English")), ("German", _("German"))],
            widget=forms.Select(attrs={"class": "field"}),
        )
        choice_labels = {
            "education_level": UserProfile.EDUCATION_CHOICES,
            "desired_degree": UserProfile.DEGREE_CHOICES,
            "theme": UserProfile.THEME_CHOICES,
            "certificate_recognition": [("yes", "Yes"), ("no", "No"), ("not sure", "Not sure")],
        }
        for field_name, choices in choice_labels.items():
            if field_name in self.fields:
                self.fields[field_name].choices = [(value, _(label)) for value, label in choices]


class OnboardingForm(ProfileSettingsForm):
    class Meta(ProfileSettingsForm.Meta):
        fields = [
            "display_name",
            "study_goal",
            "preferred_language",
            "country_of_origin",
            "education_level",
            "desired_degree",
            "preferred_subject",
            "university_city",
            "planned_start_date",
            "certificate_recognition",
            "studienkolleg_required",
        ]


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ["title", "category", "document", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "field", "placeholder": "Transcript of records"}),
            "category": forms.Select(attrs={"class": "field"}),
            "document": forms.ClearableFileInput(attrs={"class": "field"}),
            "notes": forms.Textarea(attrs={"class": "field", "rows": 4, "placeholder": "Adds context or deadline notes"}),
        }


class UniversitySearchForm(forms.Form):
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "field", "placeholder": "Berlin"}))
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "field", "placeholder": "Computer Science"}))
    degree = forms.ChoiceField(required=False, choices=[("", _("Any degree")), ("Bachelor's", _("Bachelor's")), ("Master's", _("Master's"))], widget=forms.Select(attrs={"class": "field"}))
    language = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "field", "placeholder": "German"}))
    institution_type = forms.ChoiceField(
        required=False,
        choices=[("", _("Any institution")), ("University", _("University")), ("University of Applied Sciences", _("University of Applied Sciences")), ("Studienkolleg", _("Studienkolleg")), ("Private institution", _("Private institution"))],
        widget=forms.Select(attrs={"class": "field"}),
    )


class ReLevelAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Email or username")
        self.fields["username"].widget.attrs.update({"autocomplete": "username", "placeholder": _("Email or username")})
        self.fields["password"].label = _("Password")
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        user_model = get_user_model()
        email_field = user_model.get_email_field_name()
        if "@" not in username or not email_field:
            return username

        matches = list(user_model._default_manager.filter(**{f"{email_field}__iexact": username})[:2])
        if len(matches) == 1:
            return getattr(matches[0], user_model.USERNAME_FIELD)
        return username


class UniversityListingForm(forms.ModelForm):
    class Meta:
        model = UniversityListing
        fields = ["name", "city", "subject", "degree", "institution_type", "language", "admission_requirements", "application_deadline", "tuition_fee", "website"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field"}),
            "city": forms.TextInput(attrs={"class": "field"}),
            "subject": forms.TextInput(attrs={"class": "field"}),
            "degree": forms.Select(attrs={"class": "field"}, choices=[("Bachelor's", "Bachelor's"), ("Master's", "Master's")]),
            "institution_type": forms.Select(attrs={"class": "field"}),
            "language": forms.TextInput(attrs={"class": "field"}),
            "admission_requirements": forms.Textarea(attrs={"class": "field", "rows": 4}),
            "application_deadline": forms.TextInput(attrs={"class": "field"}),
            "tuition_fee": forms.TextInput(attrs={"class": "field"}),
            "website": forms.URLInput(attrs={"class": "field"}),
        }
