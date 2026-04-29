from django.urls import path

from . import views

app_name = "resources"

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/profile/", views.edit_profile, name="edit_profile"),
    path("search/", views.global_search, name="global_search"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("years/<int:year_id>/", views.year_detail, name="year_detail"),
    path(
        "years/<int:year_id>/semesters/<int:semester_id>/",
        views.semester_detail,
        name="semester_detail",
    ),
    path(
        "years/<int:year_id>/semesters/<int:semester_id>/subjects/<int:subject_id>/",
        views.subject_detail,
        name="subject_detail",
    ),
    path(
        "years/<int:year_id>/semesters/<int:semester_id>/subjects/<int:subject_id>/upload/",
        views.upload_resource,
        name="upload_resource",
    ),
    path(
        "years/<int:year_id>/semesters/<int:semester_id>/subjects/<int:subject_id>/resources/<int:resource_id>/download/",
        views.download_resource,
        name="download_resource",
    ),
    path("about/", views.about, name="about"),
]
