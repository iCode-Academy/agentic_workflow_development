import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse

from students.models import Student


@pytest.fixture
def active_student(db):
    return Student.objects.create(
        first_name='Ada',
        last_name='Lovelace',
        email='ada@example.com',
        date_of_birth='2010-05-01',
    )


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username='teacher', password='pw-for-tests')


@pytest.mark.django_db
def test_str_returns_full_name(active_student):
    assert str(active_student) == 'Ada Lovelace'


@pytest.mark.django_db
def test_is_active_defaults_to_true(active_student):
    assert active_student.is_active is True


@pytest.mark.django_db
def test_email_is_lowercased_on_save():
    student = Student.objects.create(
        first_name='Alan',
        last_name='Turing',
        email='Alan.Turing@Example.COM',
        date_of_birth='1912-06-23',
    )
    student.refresh_from_db()
    assert student.email == 'alan.turing@example.com'


@pytest.mark.django_db
def test_duplicate_email_is_rejected(active_student):
    with pytest.raises(IntegrityError), transaction.atomic():
        Student.objects.create(
            first_name='Grace',
            last_name='Hopper',
            email='ADA@example.com',
            date_of_birth='1906-12-09',
        )


def test_student_list_url():
    assert reverse('student-list') == '/students/'


@pytest.mark.django_db
def test_student_list_requires_login(client):
    response = client.get('/students/')
    assert response.status_code == 302
    assert response['Location'].startswith('/accounts/login/')


@pytest.mark.django_db
def test_student_list_shows_only_active_students(client, user, active_student):
    Student.objects.create(
        first_name='Inactive',
        last_name='Person',
        email='inactive@example.com',
        date_of_birth='2011-01-01',
        is_active=False,
    )
    client.force_login(user)

    response = client.get('/students/')

    assert response.status_code == 200
    assert [s.email for s in response.context['students']] == ['ada@example.com']
    assert b'Ada Lovelace' in response.content
    assert b'Inactive Person' not in response.content


@pytest.mark.django_db
def test_student_list_uses_template(client, user):
    client.force_login(user)
    response = client.get('/students/')
    assert 'students/student_list.html' in [t.name for t in response.templates]
