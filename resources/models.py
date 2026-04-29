from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    course = models.ForeignKey(
        "Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    enrollment_year = models.PositiveIntegerField(null=True, blank=True)
    about_me = models.TextField(blank=True)
    avatar = models.FileField(upload_to="avatars/", null=True, blank=True)


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Semester(models.Model):
    course_year = models.ForeignKey(
        "CourseYear", on_delete=models.CASCADE, related_name="semesters"
    )
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.course_year} | Semester {self.number}"

    class Meta:
        ordering = ["number"]
        unique_together = ["course_year", "number"]


class CourseYear(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="years")
    year_number = models.PositiveIntegerField()
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        title = self.label or str(self.year_number)
        return f"{self.course.code} | {title}"

    class Meta:
        ordering = ["year_number"]
        unique_together = ["course", "year_number"]


class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name

    class Meta:
        ordering = ['name']


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("internal_exam", "Internal Exam"),
        ("semester_exam", "Semester Exam"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    title = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPE_CHOICES, default="internal_exam"
    )
    exam_label = models.CharField(
        max_length=100, blank=True, help_text="Optional: Internal 1, Internal 2, etc."
    )
    file = models.FileField(upload_to="resources/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='uploaded_resources'
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    download_count = models.PositiveIntegerField(default=0)
    year = models.PositiveIntegerField(null=True, blank=True, help_text="Exam/Test year")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

    class Meta:
        ordering = ['-uploaded_at']