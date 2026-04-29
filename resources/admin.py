from django.contrib import admin

from .models import Course, CourseYear, Semester, Subject, Resource


class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 1


class CourseYearInline(admin.TabularInline):
    model = CourseYear
    extra = 1


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('code', 'name')
    inlines = [CourseYearInline]


@admin.register(CourseYear)
class CourseYearAdmin(admin.ModelAdmin):
    list_display = ("course", "year_number", "label")
    list_filter = ("course",)
    inlines = [SemesterInline]


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("__str__", "course_year", "number")
    list_filter = ("course_year__course", "course_year")
    inlines = [SubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'semester')
    list_filter = ('semester__course_year__course', 'semester__course_year')
    search_fields = ('name', 'code')
    inlines = [ResourceInline]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'exam_label', 'subject', 'uploaded_by', 'uploaded_at', 'year')
    list_filter = ('resource_type', 'subject__semester__course_year__course')
    search_fields = ('title',)
    readonly_fields = ('uploaded_at',)