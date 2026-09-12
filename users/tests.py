from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password123', role='FREELANCER')
        Profile.objects.create(user=user, title='Python Developer', hourly_rate=50.00)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_freelancer())
        self.assertEqual(user.profile.title, 'Python Developer')
