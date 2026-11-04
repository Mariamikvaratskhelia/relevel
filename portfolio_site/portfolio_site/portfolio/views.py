from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from .forms import OnboardingForm, ProfileSettingsForm, RegistrationForm, StudentDocumentForm, UniversitySearchForm
from .models import ContactMessage, Project, Skill, StudentDocument, UniversityListing, UserProfile
from .serializers import ContactMessageSerializer, ProjectSerializer, SkillSerializer, UserSerializer
from .tasks import send_contact_notification


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.filter(is_active=True).order_by("username")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related("skills")
    serializer_class = ProjectSerializer
    lookup_field = "slug"


class ContactThrottle(AnonRateThrottle):
    rate = "5/hour"


class ContactViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Public contact form; the email is sent asynchronously by Celery."""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ContactThrottle]

    def perform_create(self, serializer):
        obj = serializer.save()
        send_contact_notification.delay(obj.pk)


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def seed_universities():
    sample = [
        {
            "name": "Technische Universität Berlin",
            "city": "Berlin",
            "subject": "Computer Science",
            "degree": "Master's",
            "institution_type": "University",
            "language": "German",
            "admission_requirements": "Bachelor's degree, transcript, CV, language proof B2/C1",
            "application_deadline": "July 15",
            "tuition_fee": "Free",
            "website": "https://www.tu-berlin.de",
        },
        {
            "name": "Hochschule München",
            "city": "Munich",
            "subject": "Data Science",
            "degree": "Master's",
            "institution_type": "University of Applied Sciences",
            "language": "English",
            "admission_requirements": "Evidence of quantitative background and CV",
            "application_deadline": "June 30",
            "tuition_fee": "Approx. €1,500/semester",
            "website": "https://www.hm.edu",
        },
        {
            "name": "University of Mannheim",
            "city": "Mannheim",
            "subject": "Business Administration",
            "degree": "Bachelor's",
            "institution_type": "University",
            "language": "German",
            "admission_requirements": "High school diploma and German language proof",
            "application_deadline": "July 15",
            "tuition_fee": "Low fees",
            "website": "https://www.uni-mannheim.de",
        },
        {
            "name": "Deutsche Akademie für Studienkolleg",
            "city": "Berlin",
            "subject": "Engineering",
            "degree": "Bachelor's",
            "institution_type": "Studienkolleg",
            "language": "German",
            "admission_requirements": "Placement test and school qualification assessment",
            "application_deadline": "August 31",
            "tuition_fee": "Depends on provider",
            "website": "https://www.studienkolleg.de",
        },
    ]
    for item in sample:
        UniversityListing.objects.get_or_create(name=item["name"], defaults=item)
    return UniversityListing.objects.all()


def generate_ai_response(question, profile):
    text = question.lower()
    if "studienkolleg" in text:
        return _("Studienkolleg may be required depending on your qualification. Confirm your individual case with the university and an official recognition authority.")
    if "visa" in text:
        return _("For visa guidance, check the German embassy or consulate in your country and your official university documents. Requirements depend on your nationality and individual situation.")
    if "motivation" in text or "letter" in text:
        return _("A strong motivation letter explains your academic background, why you want to study in Germany, your chosen field, and how the program fits your goals. Keep it clear and personal.")
    if "grammar" in text or "deutsch" in text:
        return _("For German grammar, focus on sentence structure, articles, cases, and word order. In subordinate clauses, the verb usually moves to the end.")
    if "requirement" in text or "admission" in text:
        return _("For %(subject)s, verify the exact admission requirements on the university website, including language level, transcript recognition, and any entrance exams or foundation year needs.") % {"subject": profile.preferred_subject or _("your chosen subject")}
    return _("I can help with German preparation, applications, recognition questions, and study planning. Check official university pages and embassy guidance for final admission and visa decisions.")


def home(request):
    skills = cache.get("home_skills")
    if skills is None:
        skills = list(Skill.objects.all())
        cache.set("home_skills", skills, 300)
    grouped = {}
    for s in skills:
        grouped.setdefault(s.get_category_display(), []).append(s)
    projects = Project.objects.prefetch_related("skills")
    return render(request, "portfolio/index.html", {"grouped": grouped, "projects": projects})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session["welcome_message"] = _("Welcome! Your account has been created.")
            response = redirect("onboarding")
            language_code = "de" if form.cleaned_data["preferred_language"] == "German" else "en"
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                language_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
            return response
    else:
        form = RegistrationForm()
    return render(request, "portfolio/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def onboarding(request):
    profile = get_user_profile(request.user)
    form = OnboardingForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.session["welcome_message"] = _("Your study profile is ready. Your plan can be refined any time in settings.")
        return redirect("dashboard")
    return render(request, "portfolio/onboarding.html", {"form": form, "profile": profile})


@login_required
@require_http_methods(["GET", "POST"])
def profile_settings(request):
    profile = get_user_profile(request.user)
    profile_form = ProfileSettingsForm(instance=profile)
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        if "password_change" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                request.session["welcome_message"] = _("Your password was updated successfully.")
                return redirect("dashboard")
        else:
            profile_form = ProfileSettingsForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                request.session["welcome_message"] = _("Your profile settings were saved.")
                return redirect("dashboard")

    return render(
        request,
        "portfolio/profile_settings.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
            "profile": profile,
        },
    )


@login_required
def study_path(request):
    profile = get_user_profile(request.user)
    modules = [
        {
            "title": _("Understand admission requirements"),
            "description": _("Check requirements with the university and official recognition services."),
            "status": _("Start here"),
        },
        {
            "title": _("Prepare your documents"),
            "description": _("Collect certificates, translations, and language proofs required for your applications."),
            "status": _("Next step"),
        },
        {
            "title": _("Plan your applications"),
            "description": _("Compare programs and keep each institution's deadlines and instructions together."),
            "status": _("Then"),
        },
    ]
    return render(
        request,
        "portfolio/study_path.html",
        {
            "profile": profile,
            "focus_area": profile.preferred_focus or "Career growth",
            "study_goal": profile.study_goal or "Build momentum in your learning journey.",
            "modules": modules,
        },
    )


@login_required
def dashboard(request):
    profile = get_user_profile(request.user)
    welcome_message = request.session.pop("welcome_message", None)
    focus_area = profile.preferred_focus or "Career growth"
    goal = profile.study_goal or "Build a strong portfolio and stay consistent."
    planned_start = profile.planned_start_date or None
    checklist = [
        {"label": "Choose preferred language", "done": bool(profile.preferred_language)},
        {"label": "Confirm country of origin", "done": bool(profile.country_of_origin)},
        {"label": "Check education level", "done": bool(profile.education_level)},
        {"label": "Pick degree and subject", "done": bool(profile.desired_degree and profile.preferred_subject)},
        {"label": "Select target city and start date", "done": bool(profile.university_city and planned_start)},
        {"label": "Prepare language and visa docs", "done": bool(profile.certificate_recognition)},
    ]
    completed_steps = sum(item["done"] for item in checklist)
    profile_completion = round(completed_steps * 100 / len(checklist))
    next_steps = [
        {
            "title": _("Complete your study profile"),
            "detail": _("Add your education and study preferences to personalize your plan."),
            "url": "onboarding",
        },
        {
            "title": _("Explore universities"),
            "detail": _("Filter the current directory by city, subject, degree, or language."),
            "url": "university_search",
        },
        {
            "title": _("Organize your documents"),
            "detail": _("Upload and keep track of your application files."),
            "url": "document_manager",
        },
    ]
    if profile_completion == 100:
        next_steps = next_steps[1:]
    reminders = []
    if planned_start:
        reminders.append({"name": "Planned study start", "date": planned_start})
    return render(
        request,
        "portfolio/student_dashboard.html",
        {
            "user": request.user,
            "profile": profile,
            "welcome_message": welcome_message,
            "display_name": profile.display_name or request.user.username,
            "focus_area": focus_area,
            "goal": goal,
            "checklist": checklist,
            "completed_steps": completed_steps,
            "profile_completion": profile_completion,
            "next_steps": next_steps,
            "reminders": reminders,
        },
    )


@login_required
def university_search(request):
    universities = list(seed_universities())
    form = UniversitySearchForm(request.GET)
    if form.is_valid():
        city = form.cleaned_data.get("city", "").strip().lower()
        subject = form.cleaned_data.get("subject", "").strip().lower()
        degree = form.cleaned_data.get("degree", "")
        language = form.cleaned_data.get("language", "").strip().lower()
        institution_type = form.cleaned_data.get("institution_type", "")

        filtered = []
        for u in universities:
            if city and city not in (u.city or "").lower():
                continue
            if subject and subject not in (u.subject or "").lower():
                continue
            if degree and u.degree != degree:
                continue
            if language and language not in (u.language or "").lower():
                continue
            if institution_type and u.institution_type != institution_type:
                continue
            filtered.append(u)
        universities = filtered

    return render(request, "portfolio/university_search.html", {"universities": universities, "form": form})


@login_required
def document_manager(request):
    documents = StudentDocument.objects.filter(user=request.user)
    form = StudentDocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        request.session["welcome_message"] = _("Your document was saved in the document manager.")
        return redirect("document_manager")
    return render(request, "portfolio/document_manager.html", {"documents": documents, "form": form})


@login_required
def ai_assistant(request):
    profile = get_user_profile(request.user)
    answer = None
    if request.method == "POST":
        question = request.POST.get("question", "")
        answer = generate_ai_response(question, profile)
    return render(request, "portfolio/ai_assistant.html", {"profile": profile, "answer": answer})


@login_required
def community(request):
    groups = [
        {"name": _("Nigeria in Berlin"), "description": _("Support, tips, and roommate connections for students from Nigeria.")},
        {"name": _("Engineering applicants"), "description": _("Discuss application questions, study options, and language preparation.")},
        {"name": _("Scholarship desk"), "description": _("Share scholarship opportunities and funding ideas.")},
    ]
    return render(request, "portfolio/community.html", {"groups": groups})


@login_required
def life_in_germany(request):
    tips = [
        _("Finding accommodation: start with student housing portals and official city listings."),
        _("Opening a bank account: check the provider's requirements and prepare your identification documents."),
        _("Health insurance: check the requirements that apply to your student status and keep your documents ready."),
        _("Address registration: check the local authority's instructions after you move in."),
        _("Public transport: check whether your university offers a semester ticket or local transit pass."),
    ]
    return render(request, "portfolio/life_in_germany.html", {"tips": tips})
