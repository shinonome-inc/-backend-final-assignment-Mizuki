from django.test import TestCase
from django.urls import reverse

from accounts.forms import User

from .models import Like, Tweet


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        Tweet.objects.create(user=self.user, content="first")
        Tweet.objects.create(user=self.user, content="second")

    def test_success_get(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        test_list = response.context["tweet_list"]
        self.assertQuerysetEqual(test_list, Tweet.objects.all(), ordered=False)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {"content": "test"}
        first_count = Tweet.objects.count()
        response = self.client.post(self.url, valid_data)
        test_tweet = Tweet.objects.last()

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(Tweet.objects.count(), first_count + 1)
        self.assertEqual(test_tweet.content, valid_data["content"])

    def test_failure_post_with_empty_content(self):
        invalid_data = {"content": ""}
        first_count = Tweet.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tweet.objects.count(), first_count)
        self.assertIn("このフィールドは必須です。", form.errors["content"])

    def test_failure_post_with_too_long_content(self):
        invalid_data = {"content": "a" * 141}
        first_count = Tweet.objects.count()
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tweet.objects.count(), first_count)
        self.assertIn("この値は 140 文字以下でなければなりません( 141 文字になっています)。", form.errors["content"])


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})
        self.client.login(username="testuser", password="testpass")

    def test_success_get(self):
        response = self.client.get(self.url)
        test_tweet = response.context["tweet"]
        self.assertEqual(test_tweet, self.tweet)
        self.assertEqual(response.status_code, 200)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})
        self.client.login(username="testuser", password="testpass")

    def test_success_post(self):
        first_count = Tweet.objects.count()
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(Tweet.objects.count(), first_count - 1)

    def test_failure_post_with_not_exist_tweet(self):
        not_exist_pk = self.tweet.pk + 1
        self.url = reverse("tweets:delete", kwargs={"pk": not_exist_pk})

        first_count = Tweet.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.count(), first_count)

    def test_failure_post_with_incorrect_user(self):
        self.another_user = User.objects.create_user(username="another", password="testpass")
        self.client.login(username="another", password="testpass")

        first_count = Tweet.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.count(), first_count)


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.client.login(username="testuser", password="testpass")

    def test_success_post(self):
        self.url = reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        first_count = Like.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_failure_post_with_not_exist_tweet(self):
        self.url = reverse("tweets:like", kwargs={"pk": self.tweet.pk + 1})
        first_count = Like.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_liked_tweet(self):
        self.url = reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        response = self.client.post(self.url)
        first_count = Like.objects.count()
        self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count)
        self.assertEqual(response.status_code, 200)


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.client.login(username="testuser", password="testpass")
        self.client.post(reverse("tweets:like", kwargs={"pk": self.tweet.pk}))

    def test_success_post(self):
        self.url = reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        first_count = Like.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count - 1)
        self.assertEqual(response.status_code, 200)

    def test_failure_post_with_not_exist_tweet(self):
        self.url = reverse("tweets:unlike", kwargs={"pk": self.tweet.pk + 1})
        first_count = Like.objects.count()
        response = self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_unliked_tweet(self):
        self.url = reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        response = self.client.post(self.url)
        first_count = Like.objects.count()
        self.client.post(self.url)

        self.assertEqual(Like.objects.count(), first_count)
        self.assertEqual(response.status_code, 200)
