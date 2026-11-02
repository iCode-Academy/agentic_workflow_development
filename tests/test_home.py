import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from courses.models import Course
from students.models import Student
from teachers.models import Teacher

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username='teacher', password='pw-for-tests')


@pytest.fixture
def data(db):
    Course.objects.create(code='MATH101', title='Calculus I')
    Course.objects.create(code='PHY201', title='Physics II')
    Course.objects.create(code='ART100', title='Art History')
    Teacher.objects.create(
        first_name='Grace', last_name='Hopper', email='grace@example.com', subject='Math'
    )
    Teacher.objects.create(
        first_name='Alan', last_name='Turing', email='alan@example.com', subject='Computing'
    )
    Student.objects.create(
        first_name='Ada',
        last_name='Lovelace',
        email='ada@example.com',
        date_of_birth='2010-05-01',
    )
    Student.objects.create(
        first_name='Alan',
        last_name='Kay',
        email='alan.kay@example.com',
        date_of_birth='2010-06-01',
    )
    Student.objects.create(
        first_name='Inactive',
        last_name='Person',
        email='inactive@example.com',
        date_of_birth='2011-01-01',
        is_active=False,
    )


def test_home_url():
    assert reverse('home') == '/'


def test_home_renders_counts(client, data):
    response = client.get('/')

    assert response.status_code == 200
    assert response.context['student_count'] == 2
    assert response.context['teacher_count'] == 2
    assert response.context['course_count'] == 3


def test_home_renders_counts_in_page(client, data):
    response = client.get('/')

    assert b'Students: <strong>2</strong>' in response.content
    assert b'Teachers: <strong>2</strong>' in response.content
    assert b'Courses: <strong>3</strong>' in response.content


def test_home_renders_zero_counts(client, db):
    response = client.get('/')

    assert b'Students: <strong>0</strong>' in response.content
    assert b'Teachers: <strong>0</strong>' in response.content
    assert b'Courses: <strong>0</strong>' in response.content


def test_student_count_excludes_inactive_students(client, data):
    Student.objects.create(
        first_name='Another',
        last_name='Inactive',
        email='another.inactive@example.com',
        date_of_birth='2012-01-01',
        is_active=False,
    )

    response = client.get('/')

    assert response.context['student_count'] == 2


def test_home_links_to_each_list_page(client, data):
    response = client.get('/')

    assert f'href="{reverse("student-list")}"'.encode() in response.content
    assert f'href="{reverse("teachers:teacher_list")}"'.encode() in response.content
    assert f'href="{reverse("course-list")}"'.encode() in response.content


def test_home_extends_base(client, data):
    response = client.get('/')

    assert 'base.html' in [t.name for t in response.templates]


@pytest.mark.parametrize(
    ('url_name', 'requires_login'),
    [
        ('home', False),
        ('student-list', True),
        ('teachers:teacher_list', False),
        ('course-list', False),
    ],
)
def test_page_extends_base(client, user, data, url_name, requires_login):
    if requires_login:
        client.force_login(user)

    response = client.get(reverse(url_name))

    assert response.status_code == 200
    assert 'base.html' in [t.name for t in response.templates]
