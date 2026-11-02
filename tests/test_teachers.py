import pytest
from django.contrib import admin
from django.db import IntegrityError
from django.urls import reverse

from teachers.admin import TeacherAdmin
from teachers.models import Teacher

pytestmark = pytest.mark.django_db


def make_teacher(**overrides):
    data = {
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'email': 'ada@example.com',
        'subject': 'Mathematics',
    }
    data.update(overrides)
    return Teacher.objects.create(**data)


def test_teacher_str():
    teacher = make_teacher()
    assert str(teacher) == 'Ada Lovelace'


def test_teacher_email_is_unique():
    make_teacher()
    with pytest.raises(IntegrityError):
        make_teacher(first_name='Grace', last_name='Hopper', email='ada@example.com')


def test_teachers_ordered_by_last_name_then_first_name():
    make_teacher(first_name='Grace', last_name='Hopper', email='grace@example.com')
    make_teacher(first_name='Alan', last_name='Turing', email='alan@example.com')
    make_teacher(first_name='Ada', last_name='Lovelace', email='ada@example.com')

    assert [t.last_name for t in Teacher.objects.all()] == ['Hopper', 'Lovelace', 'Turing']


def test_teacher_registered_in_admin():
    assert Teacher in admin.site._registry
    assert isinstance(admin.site._registry[Teacher], TeacherAdmin)


def test_teacher_list_view(client):
    make_teacher(first_name='Grace', last_name='Hopper', email='grace@example.com')
    make_teacher(first_name='Alan', last_name='Turing', email='alan@example.com')

    response = client.get(reverse('teachers:teacher_list'))

    assert response.status_code == 200
    assert [t.email for t in response.context['teachers']] == [
        'grace@example.com',
        'alan@example.com',
    ]
    assert 'Hopper' in response.content.decode()
    assert 'Turing' in response.content.decode()


def test_teacher_list_view_is_empty_without_teachers(client):
    response = client.get(reverse('teachers:teacher_list'))

    assert response.status_code == 200
    assert not response.context['teachers']
