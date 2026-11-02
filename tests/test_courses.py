import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse

from courses.models import Course


@pytest.fixture
def course(db):
    return Course.objects.create(
        code='MATH101',
        title='Calculus I',
        description='Limits, derivatives and integrals.',
    )


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        username='admin', email='admin@example.com', password='pw-for-tests'
    )


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username='teacher', password='pw-for-tests')


@pytest.mark.django_db
def test_str_returns_code_and_title(course):
    assert str(course) == 'MATH101 Calculus I'


@pytest.mark.django_db
def test_description_is_blank_by_default():
    course = Course.objects.create(code='BIO102', title='Biology')
    assert course.description == ''


@pytest.mark.django_db
def test_duplicate_code_is_rejected(course):
    with pytest.raises(IntegrityError), transaction.atomic():
        Course.objects.create(code='MATH101', title='Another course')


@pytest.mark.django_db
def test_courses_are_ordered_by_code():
    Course.objects.create(code='PHY201', title='Physics II')
    Course.objects.create(code='ART100', title='Art History')
    Course.objects.create(code='MATH101', title='Calculus I')

    assert [c.code for c in Course.objects.all()] == ['ART100', 'MATH101', 'PHY201']


def test_course_list_url():
    assert reverse('course-list') == '/courses/'


@pytest.mark.django_db
def test_course_list_is_public(client, course):
    response = client.get('/courses/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_course_list_shows_courses(client, course):
    Course.objects.create(code='PHY201', title='Physics II')
    Course.objects.create(code='ART100', title='Art History')

    response = client.get('/courses/')

    assert [c.code for c in response.context['courses']] == ['ART100', 'MATH101', 'PHY201']
    assert b'MATH101 Calculus I' in response.content
    assert b'ART100 Art History' in response.content
    assert b'PHY201 Physics II' in response.content


@pytest.mark.django_db
def test_course_list_shows_empty_state(client):
    response = client.get('/courses/')

    assert response.status_code == 200
    assert b'No courses.' in response.content


@pytest.mark.django_db
def test_course_list_uses_template(client):
    response = client.get('/courses/')

    assert 'courses/course_list.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_course_is_registered_in_admin():
    assert admin.site.is_registered(Course)


@pytest.mark.django_db
def test_admin_course_changelist_lists_courses(client, admin_user, course):
    client.force_login(admin_user)

    response = client.get('/admin/courses/course/')

    assert response.status_code == 200
    assert b'MATH101' in response.content


@pytest.mark.django_db
def test_admin_course_changelist_is_not_reachable_by_non_staff(client, user):
    client.force_login(user)

    response = client.get('/admin/courses/course/')

    assert response.status_code == 302
