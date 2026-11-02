from django.views.generic import TemplateView

from courses.models import Course
from students.models import Student
from teachers.models import Teacher


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_count'] = Student.objects.filter(is_active=True).count()
        context['teacher_count'] = Teacher.objects.count()
        context['course_count'] = Course.objects.count()
        return context
