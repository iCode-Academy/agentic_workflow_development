from django.contrib import admin

from students.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'date_of_birth', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('first_name', 'last_name', 'email')
