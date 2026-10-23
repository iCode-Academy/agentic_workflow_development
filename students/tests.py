import pytest
from django.contrib import admin
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


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        username='admin', email='admin@example.com', password='pw-for-tests'
    )


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
def test_student_list_shows_empty_state_when_no_active_students(client, user):
    client.force_login(user)
    response = client.get('/students/')
    assert response.status_code == 200
    assert b'No active students.' in response.content


@pytest.mark.django_db
def test_students_are_ordered_by_last_name_then_first_name():
    Student.objects.create(
        first_name='Grace', last_name='Hopper', email='grace@example.com', date_of_birth='1906-12-09'
    )
    Student.objects.create(
        first_name='Ada', last_name='Lovelace', email='ada@example.com', date_of_birth='1815-12-10'
    )
    Student.objects.create(
        first_name='Alan', last_name='Hopper', email='alan@example.com', date_of_birth='1910-01-01'
    )

    assert [str(s) for s in Student.objects.all()] == [
        'Alan Hopper',
        'Grace Hopper',
        'Ada Lovelace',
    ]


@pytest.mark.django_db
def test_student_list_renders_active_students_in_ordering(client, user):
    Student.objects.create(
        first_name='Grace', last_name='Hopper', email='grace@example.com', date_of_birth='1906-12-09'
    )
    Student.objects.create(
        first_name='Ada', last_name='Lovelace', email='ada@example.com', date_of_birth='1815-12-10'
    )
    client.force_login(user)

    response = client.get('/students/')

    assert [str(s) for s in response.context['students']] == ['Grace Hopper', 'Ada Lovelace']


@pytest.mark.django_db
def test_student_is_registered_in_admin():
    assert admin.site.is_registered(Student)


@pytest.mark.django_db
def test_admin_student_changelist_lists_students(client, admin_user, active_student):
    client.force_login(admin_user)

    response = client.get('/admin/students/student/')

    assert response.status_code == 200
    assert b'ada@example.com' in response.content


@pytest.mark.django_db
def test_admin_student_changelist_is_not_reachable_by_non_staff(client, user):
    client.force_login(user)

    response = client.get('/admin/students/student/')

    assert response.status_code == 302


@pytest.mark.django_db
def test_student_list_redirect_preserves_next_parameter(client):
    response = client.get('/students/')
    assert response['Location'] == '/accounts/login/?next=/students/'


@pytest.mark.django_db
def test_student_list_uses_template(client, user):
    client.force_login(user)
    response = client.get('/students/')
    assert 'students/student_list.html' in [t.name for t in response.templates]
