from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import ReLevelAuthenticationForm
from .views import (
    ai_assistant,
    community,
    dashboard,
    document_manager,
    home,
    life_in_germany,
    onboarding,
    profile_settings,
    register,
    study_path,
    university_search,
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html", authentication_form=ReLevelAuthenticationForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("onboarding/", onboarding, name="onboarding"),
    path("profile/settings/", profile_settings, name="profile_settings"),
    path("study-path/", study_path, name="study_path"),
    path("universities/", university_search, name="university_search"),
    path("documents/", document_manager, name="document_manager"),
    path("ai-assistant/", ai_assistant, name="ai_assistant"),
    path("student-community/", community, name="student_community"),
    path("life-in-germany/", life_in_germany, name="life_in_germany"),
]
