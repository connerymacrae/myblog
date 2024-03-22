from django.test import TestCase
from django.contrib.auth import get_user_model
from django_webtest import WebTest
from django.template import Template, Context


from blog.forms import CommentForm
from blog.models import Entry, Comment
# Create your tests here.


class EntryModelTest(TestCase):

    def test_string_representation(self):
        entry = Entry(title="My entry title")
        self. assertEqual(str(entry), entry.title)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Entry._meta.verbose_name_plural), "entries")

    def test_get_absolute_url(self):
        user = get_user_model().objects.create(username='some_user')
        entry = Entry.objects.create(title="My entry title", author=user)
        self.assertIsNotNone(entry.get_absolute_url())


class CommentModelTest(TestCase):

    def test_string_representation(self):
        comment = Comment(body="My comment body")
        self.assertEqual(str(comment), "My comment body")


class ProjectTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class HomePageTests(TestCase):

    """Test whether our blog entries show up on the homepage"""

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')

    def test_one_entry(self):
        Entry.objects.create(title='1-title', body='1-body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-body')

    def test_two_entries(self):
        Entry.objects.create(title='1-title', body='1-body', author=self.user)
        Entry.objects.create(title='2-title', body='2-body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-body')
        self.assertContains(response, '2-title')

    def test_no_entries(self):
        response = self.client.get('/')
        self.assertContains(response, 'No blog entries yet.')


class EntryViewTest(WebTest):

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')
        self.entry = Entry.objects.create(title='1-title', body='1-body',
                                          author=self.user)

    def test_basic_view(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_title_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.title)

    def test_body_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.body)

    def test_commenter_name_in_entry(self):
        test_comment = Comment.objects.create(entry=self.entry, name='commenter-1', body='body-1')
        test_comment.save()
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.comment_set.first().name)

    def test_comment_body_in_entry(self):
        test_comment = Comment.objects.create(entry=self.entry, name='commenter-1', body='body-1')
        test_comment.save()
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.comment_set.first().body)

    def test_no_comment_response(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, "No comments yet.")

    def test_view_page(self):
        page = self.app.get(self.entry.get_absolute_url())
        self.assertEqual(len(page.forms), 1)

    def test_form_error(self):
        page = self.app.get(self.entry.get_absolute_url())
        page = page.form.submit()
        self.assertContains(page, "This field is required.")

    def test_form_success(self):
        page = self.app.get(self.entry.get_absolute_url())
        page.form['name'] = "Phillip"
        page.form['email'] = "phillip@example.com"
        page.form['body'] = "Test comment body."
        page = page.form.submit()
        self.assertRedirects(page, self.entry.get_absolute_url())


class CommentFormTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user('zoidberg')
        self.entry = Entry.objects.create(author=user, title="My entry title")

    def test_init(self):
        CommentForm(entry=self.entry)

    def test_init_without_entry(self):
        with self.assertRaises(KeyError):
            CommentForm()

    def test_valid_data(self):
        form = CommentForm({
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'body': "Hi there",
        }, entry=self.entry)
        self.assertTrue(form.is_valid())
        comment = form.save()
        self.assertEqual(comment.name, "Turanga Leela")
        self.assertEqual(comment.email, "leela@example.com")
        self.assertEqual(comment.body, "Hi there")
        self.assertEqual(comment.entry, self.entry)

    def test_blank_data(self):
        form = CommentForm({}, entry=self.entry)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
            'email': ['This field is required.'],
            'body': ['This field is required.'],
        })


class EntryHistoryTagTest(TestCase):

    TEMPLATE = Template("{% load blog_tags %} {% entry_history %}")

    def setUp(self):
        self.user = get_user_model().objects.create(username='zoidberg')

    def test_entry_shows_up(self):
        entry = Entry.objects.create(author=self.user, title="My entry title")
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn(entry.title, rendered)