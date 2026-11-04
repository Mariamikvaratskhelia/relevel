from django.contrib import admin
from .models import ContactMessage, Project, Skill, StudentDocument, UniversityListing, UserProfile

admin.site.register(Skill)
admin.site.register(ContactMessage)
admin.site.register(UserProfile)
admin.site.register(StudentDocument)
admin.site.register(UniversityListing)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("skills",)
