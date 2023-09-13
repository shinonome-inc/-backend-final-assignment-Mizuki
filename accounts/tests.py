from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from accounts.models import FriendShip
from tweets.models import Tweet

from .forms import User


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        User.objects.create_user(username="testuser")

        duplicated_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, duplicated_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_email_data = {
            "username": "testuser",
            "email": "test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, invalid_email_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        short_pass_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "test",
            "password2": "test",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, short_pass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        similar_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testsuser",
            "password2": "testsuser",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, similar_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        numberpass_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "23571113",
            "password2": "23571113",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, numberpass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        mismatch_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpass",
            "password2": "testpassword",
        }
        first_count = User.objects.count()
        response = self.client.post(self.url, mismatch_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), first_count)
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        User.objects.create_user(username="testuser", password="testpass")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpass",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        nouser_data = {
            "username": "testuser1",
            "password": "testpass",
        }
        response = self.client.post(self.url, nouser_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])

    def test_failure_post_with_empty_password(self):
        emptypass_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, emptypass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass")
        Tweet.objects.create(user=self.user1, content="test")
        Tweet.objects.create(user=self.user2, content="content")
        self.friendship = FriendShip.objects.create(follower=self.user1, following=self.user2)
        self.url = reverse("accounts:user_profile", kwargs={"username": "testuser1"})

    def test_success_get(self):
        self.client.login(username="testuser1", password="testpass")
        response = self.client.get(self.url)
        test_list = response.context["profile_list"]
        test_following_count = FriendShip.objects.filter(follower=self.user1).count()
        test_follower_count = FriendShip.objects.filter(following=self.user1).count()

        self.assertQuerysetEqual(test_list, Tweet.objects.filter(user=self.user1), ordered=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["following_count"], test_following_count)
        self.assertEqual(response.context["follower_count"], test_follower_count)


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass")
        self.client.login(username="testuser1", password="testpass")

    def test_success_post(self):
        self.url = reverse("accounts:follow", kwargs={"username": "testuser2"})
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FriendShip.objects.filter(follower=self.user1).exists())

    def test_failure_post_with_not_exist_user(self):
        self.url = reverse("accounts:follow", kwargs={"username": "testuser3"})
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.filter(follower=self.user1).exists())

    def test_failure_post_with_self(self):
        self.url = reverse("accounts:follow", kwargs={"username": "testuser1"})
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.filter(follower=self.user1).exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass")
        self.client.login(username="testuser1", password="testpass")
        FriendShip.objects.create(follower=self.user1, following=self.user2)

    def test_success_post(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": "testuser2"})
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.filter(follower=self.user1).exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": "testuser3"})
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.filter(follower=self.user1).exists())

    def test_failure_post_with_incorrect_user(self):
        self.url = reverse("accounts:unfollow", kwargs={"username": "testuser1"})
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(FriendShip.objects.filter(follower=self.user1).exists())


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.client.login(username="testuser1", password="testpass")

    def test_success_get(self):
        self.url = reverse("accounts:following_list", kwargs={"username": "testuser1"})
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.client.login(username="testuser1", password="testpass")

    def test_success_get(self):
        self.url = reverse("accounts:follower_list", kwargs={"username": "testuser1"})
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
