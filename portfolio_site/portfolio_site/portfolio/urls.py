from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, ProjectViewSet, SkillViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("projects", ProjectViewSet)
router.register("skills", SkillViewSet)
router.register("contact", ContactViewSet, basename="contact")

urlpatterns = router.urls
