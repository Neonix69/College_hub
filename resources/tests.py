from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Course, CourseYear, Resource, Semester, Subject


class ResourceFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student1", password="testpass123"
        )
        self.course = Course.objects.create(name="Computer Science", code="CSE")
        self.course_year = CourseYear.objects.create(course=self.course, year_number=1)
        self.semester = Semester.objects.create(course_year=self.course_year, number=1)
        self.subject = Subject.objects.create(
            semester=self.semester, name="Mathematics", code="MATH101"
        )

    def test_navigation_pages_render(self):
        pages = [
            reverse("resources:home"),
            reverse("resources:signup"),
            reverse("resources:global_search"),
            reverse("resources:course_detail", args=[self.course.id]),
            reverse("resources:year_detail", args=[self.course_year.id]),
            reverse("resources:semester_detail", args=[self.course_year.id, self.semester.id]),
            reverse(
                "resources:subject_detail",
                args=[self.course_year.id, self.semester.id, self.subject.id],
            ),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_signup_creates_user_and_logs_in(self):
        signup_url = reverse("resources:signup")
        response = self.client.post(
            signup_url,
            {
                "username": "newstudent",
                "email": "newstudent@example.com",
                "course": self.course.id,
                "enrollment_year": 2024,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("resources:home"))
        self.assertTrue(get_user_model().objects.filter(username="newstudent").exists())
        self.assertEqual(
            get_user_model().objects.get(username="newstudent").course_id, self.course.id
        )
        self.assertEqual(
            get_user_model().objects.get(username="newstudent").enrollment_year, 2024
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_edit_profile_updates_course_but_not_enrollment_year(self):
        self.client.login(username="student1", password="testpass123")
        type(self.user).objects.filter(pk=self.user.pk).update(enrollment_year=2022)
        self.user.refresh_from_db()
        other_course = Course.objects.create(name="Electronics", code="ECE")
        url = reverse("resources:edit_profile")
        response = self.client.post(
            url,
            {
                "course": other_course.id,
                "enrollment_year": 2023,
                "about_me": "I love cybersecurity labs.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("resources:home"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.course_id, other_course.id)
        self.assertEqual(self.user.enrollment_year, 2022)
        self.assertEqual(self.user.about_me, "I love cybersecurity labs.")

    def test_upload_resource(self):
        self.client.login(username="student1", password="testpass123")
        upload_url = reverse(
            "resources:upload_resource",
            args=[self.course_year.id, self.semester.id, self.subject.id],
        )
        file_obj = SimpleUploadedFile(
            "sample.txt", b"study-material", content_type="text/plain"
        )
        response = self.client.post(
            upload_url,
            {
                "title": "Internal 1 Question Paper",
                "resource_type": "internal_exam",
                "exam_label": "Internal 1",
                "year": 2026,
                "notes": "Important questions",
                "file": file_obj,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.first().subject, self.subject)

    def test_download_increments_counter(self):
        resource = Resource.objects.create(
            subject=self.subject,
            title="Semester Paper",
            resource_type="semester_exam",
            file=SimpleUploadedFile("paper.txt", b"paper-data", content_type="text/plain"),
        )
        url = reverse(
            "resources:download_resource",
            args=[self.course_year.id, self.semester.id, self.subject.id, resource.id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resource.refresh_from_db()
        self.assertEqual(resource.download_count, 1)

    def test_subject_filter_by_type(self):
        Resource.objects.create(
            subject=self.subject,
            title="Internal Test 1",
            resource_type="internal_exam",
            file=SimpleUploadedFile("internal.txt", b"internal", content_type="text/plain"),
        )
        Resource.objects.create(
            subject=self.subject,
            title="Sem Exam",
            resource_type="semester_exam",
            file=SimpleUploadedFile("sem.txt", b"semester", content_type="text/plain"),
        )
        url = reverse(
            "resources:subject_detail",
            args=[self.course_year.id, self.semester.id, self.subject.id],
        )
        response = self.client.get(url, {"type": "internal_exam"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Internal Exam")
        self.assertContains(response, "Internal Test 1")
        self.assertNotContains(response, "Sem Exam")

    def test_upload_forbidden_for_invalid_role(self):
        self.client.login(username="student1", password="testpass123")
        # Simulate unexpected role value from DB; upload should be blocked.
        type(self.user).objects.filter(pk=self.user.pk).update(role="guest")
        self.user.refresh_from_db()
        upload_url = reverse(
            "resources:upload_resource",
            args=[self.course_year.id, self.semester.id, self.subject.id],
        )
        response = self.client.post(
            upload_url,
            {
                "title": "Should Fail",
                "resource_type": "internal_exam",
                "file": SimpleUploadedFile("deny.txt", b"x", content_type="text/plain"),
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_subject_sort_most_downloaded(self):
        high = Resource.objects.create(
            subject=self.subject,
            title="High",
            resource_type="semester_exam",
            download_count=9,
            file=SimpleUploadedFile("high.txt", b"h", content_type="text/plain"),
        )
        low = Resource.objects.create(
            subject=self.subject,
            title="Low",
            resource_type="semester_exam",
            download_count=1,
            file=SimpleUploadedFile("low.txt", b"l", content_type="text/plain"),
        )
        url = reverse(
            "resources:subject_detail",
            args=[self.course_year.id, self.semester.id, self.subject.id],
        )
        response = self.client.get(url, {"sort": "most_downloaded"})
        self.assertEqual(response.status_code, 200)
        sections = response.context["resource_sections"]
        semester_section = next(
            section for section in sections if section["label"] == "Semester Exam"
        )
        resources_list = list(semester_section["items"])
        self.assertEqual([r.id for r in resources_list], [high.id, low.id])

    def test_global_search_filters(self):
        Resource.objects.create(
            subject=self.subject,
            title="Linear Algebra Notes",
            resource_type="internal_exam",
            year=2026,
            file=SimpleUploadedFile("la.txt", b"la", content_type="text/plain"),
        )
        Resource.objects.create(
            subject=self.subject,
            title="Signals Paper",
            resource_type="semester_exam",
            year=2025,
            file=SimpleUploadedFile("sig.txt", b"sig", content_type="text/plain"),
        )
        url = reverse("resources:global_search")
        response = self.client.get(
            url,
            {
                "q": "Linear",
                "course": str(self.course.id),
                "type": "internal_exam",
                "year": "2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Linear Algebra Notes")
        self.assertNotContains(response, "Signals Paper")

    def test_global_search_dependent_dropdowns_and_pagination(self):
        other_course = Course.objects.create(name="Electronics", code="ECE")
        other_year = CourseYear.objects.create(course=other_course, year_number=1)
        Semester.objects.create(course_year=other_year, number=1)

        for i in range(18):
            Resource.objects.create(
                subject=self.subject,
                title=f"Material {i}",
                resource_type="internal_exam",
                file=SimpleUploadedFile(f"m{i}.txt", b"x", content_type="text/plain"),
            )

        url = reverse("resources:global_search")
        response = self.client.get(url, {"course": str(self.course.id)})
        self.assertEqual(response.status_code, 200)
        years = response.context["years"]
        self.assertEqual(years.count(), 1)
        self.assertEqual(years.first().course_id, self.course.id)
        self.assertContains(response, "Next")
