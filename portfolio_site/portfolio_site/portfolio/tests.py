from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserAPITestCase(TestCase):
    def test_users_endpoint_is_public_and_lists_users(self):
        User = get_user_model()
        User.objects.create_user(username="alice", password="secret123")
        User.objects.create_user(username="bob", password="secret123")

        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual({item["username"] for item in response.json()["results"]}, {"alice", "bob"})


class AuthFlowTestCase(TestCase):
    def test_user_can_register_and_access_dashboard(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "Student",
                "email": "newuser@example.com",
                "country_of_origin": "Georgia",
                "preferred_language": "English",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Your study journey starts here.")

        dashboard_response = self.client.get(reverse("dashboard"))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, "New Student")
        self.assertEqual(response.wsgi_request.user.profile.country_of_origin, "Georgia")

        self.client.logout()
        login_response = self.client.post(
            reverse("login"),
            {"username": "newuser@example.com", "password": "StrongPass123!"},
            follow=True,
        )
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)

    def test_existing_account_can_log_in_using_its_email(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="older-username",
            email="older-account@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            reverse("login"),
            {"username": "older-account@example.com", "password": "StrongPass123!"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.pk, user.pk)


class PublicLandingTestCase(TestCase):
    def test_landing_page_uses_relevel_brand_without_fake_progress(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ReLevel")
        self.assertContains(response, "Level up your future in Germany.")
        self.assertContains(response, "Your journey to studying in Germany starts here.")
        self.assertContains(response, "Get started")
        self.assertNotContains(response, "68%")
        self.assertNotContains(response, "Skills")


class LanguageSwitchTestCase(TestCase):
    def test_registration_language_choice_sets_the_site_language(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Mira",
                "last_name": "Student",
                "email": "mira@example.com",
                "country_of_origin": "Georgia",
                "preferred_language": "German",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "de")
        self.assertContains(response, "Dein Weg zum Studium beginnt hier.")
        self.assertContains(response, 'lang="de"')

    def test_selecting_german_translates_the_landing_page(self):
        response = self.client.post(reverse("set_language"), {"language": "de", "next": reverse("home")})

        self.assertRedirects(response, reverse("home"))
        german_home = self.client.get(reverse("home"))
        self.assertContains(german_home, "Dein Weg zum Studium in Deutschland beginnt hier.")
        self.assertContains(german_home, "Bringe deine Zukunft in Deutschland aufs nächste Level.")
        self.assertContains(german_home, "Jetzt starten")

    def test_german_selection_translates_authenticated_dashboard(self):
        self.client.force_login(get_user_model().objects.create_user(username="germanstudent", password="StrongPass123!"))
        self.client.post(reverse("set_language"), {"language": "de", "next": reverse("dashboard")})

        german_dashboard = self.client.get(reverse("dashboard"))

        self.assertEqual(german_dashboard.status_code, 200)
        self.assertContains(german_dashboard, "Deine nächsten Schritte")
        self.assertContains(german_dashboard, "Profil-Checkliste")

    def test_signed_in_pages_render_with_german_locale(self):
        self.client.force_login(get_user_model().objects.create_user(username="localeuser", password="StrongPass123!"))
        self.client.post(reverse("set_language"), {"language": "de", "next": reverse("dashboard")})

        for route_name in [
            "study_path",
            "university_search",
            "document_manager",
            "ai_assistant",
            "student_community",
            "life_in_germany",
            "profile_settings",
        ]:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'lang="de"')


class UserProfileSettingsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="profileuser", password="StrongPass123!")
        self.client.force_login(self.user)

    def test_dashboard_uses_custom_profile_settings(self):
        profile = self.user.profile
        profile.display_name = "Maya"
        profile.bio = "Frontend learner"
        profile.study_goal = "Build a portfolio"
        profile.preferred_focus = "Product design"
        profile.theme = "dark"
        profile.save()

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maya")
        self.assertContains(response, "Product design")
        self.assertContains(response, "Build a portfolio")

    def test_user_can_update_profile_settings(self):
        response = self.client.post(
            reverse("profile_settings"),
            {
                "display_name": "Maya",
                "bio": "Design-focused learner",
                "study_goal": "Get my first role",
                "preferred_focus": "Product design",
                "theme": "dark",
                "email_notifications": True,
            },
        )

        self.user.profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.profile.display_name, "Maya")
        self.assertEqual(self.user.profile.study_goal, "Get my first role")
        self.assertTrue(self.user.profile.email_notifications)

    def test_user_can_change_password_from_profile_settings(self):
        response = self.client.post(
            reverse("profile_settings"),
            {
                "old_password": "StrongPass123!",
                "new_password1": "NewPass456!",
                "new_password2": "NewPass456!",
                "password_change": "true",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.check_password("NewPass456!"))

    def test_student_onboarding_fields_are_saved(self):
        response = self.client.post(
            reverse("profile_settings"),
            {
                "preferred_language": "German",
                "country_of_origin": "Nigeria",
                "education_level": "Bachelor's degree",
                "desired_degree": "Master's",
                "preferred_subject": "Computer Science",
                "university_city": "Berlin",
                "planned_start_date": "2026-10-01",
                "certificate_recognition": "yes",
                "studienkolleg_required": "yes",
                "display_name": "Maya",
                "bio": "International student",
                "study_goal": "Study in Germany",
                "preferred_focus": "Admissions",
                "theme": "dark",
                "email_notifications": True,
            },
        )

        self.user.profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.profile.preferred_language, "German")
        self.assertEqual(self.user.profile.country_of_origin, "Nigeria")
        self.assertEqual(self.user.profile.desired_degree, "Master's")
        self.assertEqual(self.user.profile.university_city, "Berlin")
        self.assertTrue(self.user.profile.studienkolleg_required)

    def test_onboarding_wizard_preserves_settings_it_does_not_edit(self):
        profile = self.user.profile
        profile.bio = "Keep this profile note"
        profile.theme = "dark"
        profile.email_notifications = True
        profile.save()

        response = self.client.post(
            reverse("onboarding"),
            {
                "display_name": "Maya",
                "study_goal": "Study in Germany",
                "preferred_language": "English",
                "country_of_origin": "Georgia",
                "education_level": "High school diploma",
                "desired_degree": "Bachelor's",
                "preferred_subject": "Computer Science",
                "university_city": "Berlin",
                "planned_start_date": "2027-10-01",
                "certificate_recognition": "not sure",
            },
        )

        profile.refresh_from_db()
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(profile.country_of_origin, "Georgia")
        self.assertEqual(profile.bio, "Keep this profile note")
        self.assertEqual(profile.theme, "dark")
        self.assertTrue(profile.email_notifications)

    def test_dashboard_uses_saved_profile_progress_and_no_placeholder_deadlines(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0%")
        self.assertContains(response, "Add your planned study start date")
        self.assertNotContains(response, "Next 2 weeks")
