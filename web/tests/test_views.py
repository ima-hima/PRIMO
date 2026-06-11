import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from web import views
from web.views import tabulate_scalar


def _add_session(request: HttpRequest) -> None:
    middleware = SessionMiddleware(lambda request: HttpResponse())
    middleware.process_request(request)
    request.session.save()


class HomeViewTest(TestCase):
    def test_index_page(self) -> None:
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class TabulateScalarTest(TestCase):
    def test_tabulate_empty_results(self) -> None:
        self.assertEqual(tabulate_scalar([], False), [])

    def _make_row(
        self, hypocode: str, variable_label: str, scalar_value: str
    ) -> dict[str, str]:
        """Build a full row with all specimen metadata keys."""
        from web.views import get_specimen_metadata

        row = {k: f"val_{k}" for k, _ in get_specimen_metadata("Scalar")}
        row["hypocode"] = hypocode
        row["variable_label"] = variable_label
        row["scalar_value"] = scalar_value
        return row

    def test_tabulate_single_specimen(self) -> None:
        rows = [
            self._make_row("ABC", "Weight", "12"),
            self._make_row("ABC", "Height", "34"),
        ]
        result = tabulate_scalar(rows, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["hypocode"], "ABC")
        self.assertEqual(result[0]["Weight"], "12")
        self.assertEqual(result[0]["Height"], "34")

    def test_tabulate_multiple_specimens(self) -> None:
        rows = [
            self._make_row("AAA", "Weight", "10"),
            self._make_row("BBB", "Weight", "20"),
            self._make_row("BBB", "Other", "20"),
        ]
        result = tabulate_scalar(rows, False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["hypocode"], "AAA")
        self.assertEqual(result[1]["hypocode"], "BBB")
        self.assertEqual(result[1]["Other"], "20")

    def test_tabulate_preview_limit(self) -> None:
        rows = [self._make_row(f"H{i}", "V", str(i)) for i in range(20)]
        result = tabulate_scalar(rows, True)
        self.assertEqual(len(result), 15)


class ViewsHelpersTest(TestCase):
    def test_get_specimen_metadata_scalar_and_3d(self) -> None:
        scalar_meta = views.get_specimen_metadata("Scalar")
        keys = [k for k, _ in scalar_meta]
        self.assertIn("specimen_id", keys)
        self.assertNotIn("missing_pts", keys)

        three_meta = views.get_specimen_metadata("3D")
        three_keys = [k for k, _ in three_meta]
        self.assertIn("missing_pts", three_keys)

    def test_set_up_sql_query_scalar_and_3d(self) -> None:
        scalar_sql = views.set_up_sql_query(True, True)
        self.assertIn("variable.id in %s", scalar_sql)
        self.assertIn("ORDER BY `specimen_id` ASC", scalar_sql)

        three_sql = views.set_up_sql_query(False, True)
        self.assertIn("FROM session", three_sql)
        self.assertNotIn("variable.id in %s", three_sql)

    def test_init_query_table_and_tabulate_preview_limit(self) -> None:
        keys = [k for k, _ in views.get_specimen_metadata("Scalar")]
        base_row = {k: f"val_{k}" for k in keys}
        base_row.update({"variable_label": "V1", "scalar_value": "1", "hypocode": "H0"})

        out = views.init_query_table("Scalar", base_row)
        for k in keys:
            self.assertIn(k, out)
        self.assertEqual(out["variable_label"], "V1")

        rows = []
        for i in range(20):
            row = {k: f"val_{k}_{i}" for k in keys}
            row.update(
                {"variable_label": "V", "scalar_value": str(i), "hypocode": f"H{i}"}
            )
            rows.append(row)

        result = views.tabulate_scalar(rows, True)
        self.assertEqual(len(result), 15)


class DownloadAnd3DTest(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp(prefix="primo_test_dl_")
        self.factory = RequestFactory()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @override_settings(DOWNLOAD_ROOT="/tmp/does_not_exist_for_test")
    def test_set_up_download_scalar(self) -> None:
        req = self.factory.get("/")
        _add_session(req)
        req.session["scalar_or_3d"] = "Scalar"
        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            directory_name, file_to_download = views.set_up_download(req)
            self.assertEqual(directory_name, "")
            self.assertTrue(file_to_download.startswith("PRIMO_results_"))

    def test_set_up_download_scalar_no_user_agent(self) -> None:
        req = self.factory.get("/")
        req.META = {}
        _add_session(req)
        req.session["scalar_or_3d"] = "Scalar"
        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            directory_name, file_to_download = views.set_up_download(req)
            self.assertEqual(directory_name, "")
            self.assertTrue(file_to_download.startswith("PRIMO_results_"))

    def test_set_up_download_3d_creates_dir(self) -> None:
        req = self.factory.get("/")
        _add_session(req)
        req.session["scalar_or_3d"] = "3D"
        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            directory_name, file_to_download = views.set_up_download(req)
            fullpath = os.path.join(self.tmpdir, directory_name)
            self.assertTrue(os.path.isdir(fullpath))
            self.assertEqual(file_to_download, "specimen_metadata.csv")

    def test_create_3d_output_string_writes_file_and_missing_pts(self) -> None:
        req = self.factory.get("/")
        _add_session(req)
        req.session["newline_char"] = "\n"
        req.session["sessions"] = [1, 2]
        req.session["directory_name"] = "PRIMO_3D_testdir"
        dst = os.path.join(self.tmpdir, req.session["directory_name"])
        os.makedirs(dst, exist_ok=True)

        query_results = [
            {"specimen_id": 1, "hypocode": "A", "x": 1.0, "y": 2.0, "z": 3.0},
            {"specimen_id": 2, "hypocode": "B", "x": 9999.0, "y": 9999.0, "z": 9999.0},
        ]

        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            views.create_3d_output_string(req, query_results, output_file_type="grfnd")
            out_file = os.path.join(dst, "3d_data.txt")
            self.assertTrue(os.path.exists(out_file))
            self.assertIn(2, req.session["missing_pts"])


class DownloadViewTest(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp(prefix="primo_test_dl_")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_download_raises_404_when_file_missing(self) -> None:
        from django.http import Http404

        with self.assertRaises(Http404):
            views.download("Scalar", "", "nonexistent_file.csv")

    def test_download_scalar_returns_response(self) -> None:
        fname = "test_results.csv"
        fpath = os.path.join(self.tmpdir, fname)
        with open(fpath, "w") as f:
            f.write("col1,col2\nval1,val2\n")

        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            response = views.download("Scalar", "", fname)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"col1", response.content)

    def test_set_up_download_windows_user_agent(self) -> None:
        factory = RequestFactory()
        req = factory.get("/", HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0)")
        middleware = SessionMiddleware(lambda r: HttpResponse())
        middleware.process_request(req)
        req.session.save()
        req.session["scalar_or_3d"] = "Scalar"
        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            views.set_up_download(req)
        self.assertEqual(req.session["newline_char"], "\r\n")


class SimpleViewsTest(TestCase):
    def test_download_success_view(self) -> None:
        self.client.get(reverse("download_success"))

    def test_entity_relation_diagram_view(self) -> None:
        response = self.client.get(reverse("erd"))
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_login_get(self) -> None:
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_post_invalid_credentials(self) -> None:
        response = self.client.post(
            reverse("login"),
            {"user_name": "testuser", "password": "wrongpass", "next": "/"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "username/password combination")

    def test_login_post_valid_credentials(self) -> None:
        response = self.client.post(
            reverse("login"),
            {"user_name": "testuser", "password": "testpass123", "next": "/"},
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_login_get_with_next_param(self) -> None:
        response = self.client.get(reverse("login") + "?next=/some/path/")
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="logoutuser", password="pass123")

    def test_logout_view_requires_login(self) -> None:
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    def test_logout_view_authenticated(self) -> None:
        self.client.login(username="logoutuser", password="pass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)


class QueryStartViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="quser", password="qpass123")

    def test_query_start_requires_login(self) -> None:
        response = self.client.get(reverse("query_start"))
        self.assertEqual(response.status_code, 302)

    def test_query_start_authenticated(self) -> None:
        self.client.login(username="quser", password="qpass123")
        response = self.client.get(reverse("query_start"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session["scalar_or_3d"], "")


class EmailViewTest(TestCase):
    def test_email_get(self) -> None:
        response = self.client.get(reverse("email"))
        self.assertEqual(response.status_code, 200)

    def test_email_post_invalid(self) -> None:
        response = self.client.post(reverse("email"), {})
        self.assertEqual(response.status_code, 200)

    @patch("web.views.send_mail")
    def test_email_post_valid(self, mock_send_mail: MagicMock) -> None:
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "affiliation": "University",
            "position": "Researcher",
            "dept": "Biology",
            "institute": "Bio Inst",
            "country": "USA",
            "body": "Please grant access.",
        }
        response = self.client.post(reverse("email"), data)
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_called_once()
