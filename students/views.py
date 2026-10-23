from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from students.models import Student


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.filter(is_active=True)
