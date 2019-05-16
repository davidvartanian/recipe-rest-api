from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def get_sample_user(email='user@test.com', password='user12345678'):
    """Create sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating new user with email is successful"""
        email = 'test@test.com'
        password = 'test1234567'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """
        Test the email for a new user is normalised
        """
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, '1234321')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test creating user with no email raises an error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234321')

    def test_create_new_superuser(self):
        """
        Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            'super@test.com',
            'test12345678'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=get_sample_user(),
            name='meat eater'
        )

        self.assertEqual(str(tag), tag.name)
