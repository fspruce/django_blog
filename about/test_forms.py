from django.test import TestCase
from .forms import CollaborateForm

# Create your tests here.


class TestCollaborateForm(TestCase):

    def test_form_is_valid(self):
        """Test for all fields"""
        form = CollaborateForm(
            {"name": "Fspruce", "email": "test@test.com", "message": "Hello!"}
        )
        self.assertTrue(form.is_valid(), msg="Form is not valid")

    def test_name_is_valid(self):
        """Test for name field"""
        form = CollaborateForm({"name": ""})
        self.assertFalse(
            form.is_valid(), msg="name is empty, but form still valid"
        )

    def test_email_is_valid(self):
        """Test for email field"""
        form = CollaborateForm({"email": ""})
        self.assertFalse(
            form.is_valid(), msg="email is empty, but form still valid"
        )

    def test_message_is_valid(self):
        """Test for message field"""
        form = CollaborateForm({"message": ""})
        self.assertFalse(
            form.is_valid(), msg="message is empty, but form still valid"
        )
