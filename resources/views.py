from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import F, Sum, Count, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .forms import ResourceUploadForm, UserRegistrationForm, UserProfileForm
from .models import Course, CourseYear, Semester, Subject, Resource


def home(request):
    resources_for_course = (
        Resource.objects.filter(subject__semester__course_year__course=OuterRef("pk"))
        .values("subject__semester__course_year__course")
        .annotate(
            uploads_count=Count("id"),
            downloads_total=Coalesce(Sum("download_count"), 0),
        )
    )
    courses = Course.objects.prefetch_related("years").annotate(
        uploads_count=Coalesce(
            Subquery(resources_for_course.values("uploads_count")[:1]),
            0,
            output_field=IntegerField(),
        ),
        downloads_total=Coalesce(
            Subquery(resources_for_course.values("downloads_total")[:1]),
            0,
            output_field=IntegerField(),
        ),
    )
    user_course = None
    if request.user.is_authenticated:
        user_course = request.user.course
    courses_by_school = {}
    for course in courses:
        school = "Other"
        if course.description and course.description.lower().startswith("school:"):
            school = course.description.split(":", 1)[1].strip() or "Other"
        courses_by_school.setdefault(school, []).append(course)
    courses_by_school_items = sorted(courses_by_school.items(), key=lambda x: x[0].lower())
    top_resources = Resource.objects.select_related(
        "subject__semester__course_year__course"
    ).filter(subject__isnull=False).order_by("-download_count", "-uploaded_at")[:5]
    return render(
        request,
        "resources/home.html",
        {
            "courses": courses,
            "courses_by_school": courses_by_school_items,
            "top_resources": top_resources,
            "user_course": user_course,
        },
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect("resources:home")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("resources:home")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("resources:home")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "resources/edit_profile.html", {"form": form})


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    years = course.years.prefetch_related("semesters").all()
    return render(
        request,
        "resources/course_detail.html",
        {
            "course": course,
            "years": years,
        },
    )


def year_detail(request, year_id):
    course_year = get_object_or_404(CourseYear, pk=year_id)
    semesters = course_year.semesters.order_by("number")
    return render(
        request,
        "resources/year_detail.html",
        {
            "course_year": course_year,
            "semesters": semesters,
        },
    )


def semester_detail(request, year_id, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id, course_year_id=year_id)
    subjects = semester.subjects.all()
    return render(
        request,
        "resources/semester_detail.html",
        {
            "semester": semester,
            "subjects": subjects,
        },
    )


def subject_detail(request, year_id, semester_id, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, semester_id=semester_id)
    if subject.semester.course_year_id != year_id:
        return render(request, "resources/not_found.html", status=404)
    resources = subject.resources.select_related("uploaded_by__course").all()
    query = request.GET.get("q", "").strip()
    selected_type = request.GET.get("type", "").strip()
    selected_year = request.GET.get("year", "").strip()
    sort = request.GET.get("sort", "latest").strip()

    if query:
        resources = resources.filter(title__icontains=query)
    if selected_type in {"internal_exam", "semester_exam"}:
        resources = resources.filter(resource_type=selected_type)
    if selected_year.isdigit():
        resources = resources.filter(year=int(selected_year))
    if sort == "oldest":
        resources = resources.order_by("uploaded_at")
    elif sort == "most_downloaded":
        resources = resources.order_by("-download_count", "-uploaded_at")
    else:
        sort = "latest"
        resources = resources.order_by("-uploaded_at")

    grouped = {}
    for res in resources:
        label = res.get_resource_type_display()
        grouped.setdefault(label, []).append(res)
    resource_sections = [
        {"label": "Internal Exam", "items": grouped.get("Internal Exam", [])},
        {"label": "Semester Exam", "items": grouped.get("Semester Exam", [])},
    ]

    return render(
        request,
        "resources/subject_detail.html",
        {
            "subject": subject,
            "resource_sections": resource_sections,
            "resource_count": resources.count(),
            "query": query,
            "selected_type": selected_type,
            "selected_year": selected_year,
            "sort": sort,
        },
    )


@login_required
def upload_resource(request, year_id, semester_id, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, semester_id=semester_id)
    if subject.semester.course_year_id != year_id:
        return render(request, "resources/not_found.html", status=404)
    if request.user.role not in {"student", "admin"}:
        return HttpResponseForbidden("You do not have permission to upload resources.")

    if request.method == "POST":
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.subject = subject
            if request.user.is_authenticated:
                resource.uploaded_by = request.user
            resource.save()
            return redirect(
                "resources:subject_detail",
                year_id=year_id,
                semester_id=semester_id,
                subject_id=subject_id,
            )
    else:
        form = ResourceUploadForm()

    return render(
        request,
        "resources/upload_resource.html",
        {"subject": subject, "form": form},
    )


def download_resource(request, year_id, semester_id, subject_id, resource_id):
    subject = get_object_or_404(Subject, pk=subject_id, semester_id=semester_id)
    if subject.semester.course_year_id != year_id:
        raise Http404("Resource not found for this path.")

    resource = get_object_or_404(Resource, pk=resource_id, subject=subject)
    if not resource.file:
        raise Http404("File is unavailable.")

    Resource.objects.filter(pk=resource.pk).update(download_count=F("download_count") + 1)
    resource.refresh_from_db(fields=["download_count"])
    return FileResponse(resource.file.open("rb"), as_attachment=True, filename=resource.file.name.split("/")[-1])


def about(request):
    stats = {
        "courses": Course.objects.count(),
        "years": CourseYear.objects.count(),
        "subjects": Subject.objects.count(),
        "resources": Resource.objects.count(),
    }
    top_resources = Resource.objects.select_related(
        "subject__semester__course_year__course"
    ).filter(subject__isnull=False).order_by("-download_count", "-uploaded_at")[:10]
    return render(
        request, "resources/about.html", {"stats": stats, "top_resources": top_resources}
    )


def global_search(request):
    resources = Resource.objects.select_related(
        "subject__semester__course_year__course"
    ).filter(subject__isnull=False)

    query = request.GET.get("q", "").strip()
    course_id = request.GET.get("course", "").strip()
    course_year_id = request.GET.get("course_year", "").strip()
    semester_id = request.GET.get("semester", "").strip()
    resource_type = request.GET.get("type", "").strip()
    exam_year = request.GET.get("year", "").strip()
    sort = request.GET.get("sort", "latest").strip()

    if query:
        resources = resources.filter(title__icontains=query)
    if course_id.isdigit():
        resources = resources.filter(subject__semester__course_year__course_id=int(course_id))
    if course_year_id.isdigit():
        resources = resources.filter(subject__semester__course_year_id=int(course_year_id))
    if semester_id.isdigit():
        resources = resources.filter(subject__semester_id=int(semester_id))
    if resource_type in {"internal_exam", "semester_exam"}:
        resources = resources.filter(resource_type=resource_type)
    if exam_year.isdigit():
        resources = resources.filter(year=int(exam_year))

    if sort == "oldest":
        resources = resources.order_by("uploaded_at")
    elif sort == "most_downloaded":
        resources = resources.order_by("-download_count", "-uploaded_at")
    else:
        sort = "latest"
        resources = resources.order_by("-uploaded_at")

    selected_course_obj = None
    selected_course_year_obj = None
    if course_id.isdigit():
        selected_course_obj = Course.objects.filter(pk=int(course_id)).first()
    if course_year_id.isdigit():
        selected_course_year_obj = CourseYear.objects.filter(pk=int(course_year_id)).first()

    courses = Course.objects.all()
    years = CourseYear.objects.select_related("course").all()
    semesters = Semester.objects.select_related("course_year__course").all()

    # Dependent dropdowns: narrow year/semester options from selected parent.
    if selected_course_obj:
        years = years.filter(course=selected_course_obj)
        if selected_course_year_obj and selected_course_year_obj.course_id != selected_course_obj.id:
            selected_course_year_obj = None
            course_year_id = ""
            semester_id = ""
    if selected_course_year_obj:
        semesters = semesters.filter(course_year=selected_course_year_obj)
        if semester_id.isdigit() and not semesters.filter(pk=int(semester_id)).exists():
            semester_id = ""

    paginator = Paginator(resources, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "resources": page_obj.object_list,
        "total_count": paginator.count,
        "page_obj": page_obj,
        "courses": courses,
        "years": years,
        "semesters": semesters,
        "query": query,
        "selected_course": course_id,
        "selected_course_year": course_year_id,
        "selected_semester": semester_id,
        "selected_type": resource_type,
        "selected_year": exam_year,
        "sort": sort,
        "query_string": query_params.urlencode(),
    }
    return render(request, "resources/global_search.html", context)