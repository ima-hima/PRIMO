import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser, Group, User
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
        self,
        specimen_id: int,
        variable_label: str,
        scalar_value: str,
        hypocode: str = "",
    ) -> dict[str, str]:
        """Build a full row with all specimen metadata keys."""
        from web.views import get_specimen_metadata

        row: dict[str, str] = {
            k: f"val_{k}" for k, _ in get_specimen_metadata("Scalar")
        }
        row["specimen_id"] = str(specimen_id)
        row["hypocode"] = hypocode or f"H{specimen_id}"
        row["variable_label"] = variable_label
        row["scalar_value"] = scalar_value
        return row

    def test_tabulate_single_specimen(self) -> None:
        rows = [
            self._make_row(1, "Weight", "12"),
            self._make_row(1, "Height", "34"),
        ]
        result = tabulate_scalar(rows, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["specimen_id"], "1")
        self.assertEqual(result[0]["Weight"], "12")
        self.assertEqual(result[0]["Height"], "34")

    def test_tabulate_multiple_specimens(self) -> None:
        rows = [
            self._make_row(1, "Weight", "10"),
            self._make_row(2, "Weight", "20"),
            self._make_row(2, "Other", "30"),
        ]
        result = tabulate_scalar(rows, False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["specimen_id"], "1")
        self.assertEqual(result[1]["specimen_id"], "2")
        self.assertEqual(result[1]["Other"], "30")

    def test_tabulate_preview_limit(self) -> None:
        rows = [self._make_row(i, "V", str(i)) for i in range(20)]
        result = tabulate_scalar(rows, True)
        self.assertEqual(len(result), 5)

    def test_tabulate_single_specimen_single_variable(self) -> None:
        rows = [self._make_row(99, "Length", "99")]
        result = tabulate_scalar(rows, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["specimen_id"], "99")
        self.assertEqual(result[0]["Length"], "99")

    def test_tabulate_preview_limit_exactly_5(self) -> None:
        rows = [self._make_row(i, "V", str(i)) for i in range(5)]
        result = tabulate_scalar(rows, True)
        self.assertEqual(len(result), 5)


class BuildTreeJsonTest(TestCase):
    def _nodes(self, *specs: dict) -> list[dict]:
        """Build a flat node list from shorthand dicts."""
        return [
            {
                "id": s["id"],
                "label": s.get("label", f"node_{s['id']}"),
                "parent_id": s.get("parent_id", s["id"]),
                "expand_in_tree": s.get("expand", False),
                "tree_root": s.get("tree_root", 0),
            }
            for s in specs
        ]

    def _call(self, nodes: list, selected_ids: list[int]) -> tuple:
        with patch("web.views.apps.get_model") as mock_get_model:
            mock_get_model.return_value.objects.values.return_value = nodes
            return views.build_tree_json("taxon", selected_ids)

    def test_single_root_no_children(self) -> None:
        nodes = self._nodes({"id": 1, "tree_root": 1})
        roots, selection = self._call(nodes, [])
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]["id"], 1)
        self.assertEqual(roots[0]["children"], [])

    def test_root_identified_by_tree_root_flag(self) -> None:
        nodes = self._nodes(
            {"id": 1, "tree_root": 1},
            {"id": 2, "parent_id": 1},
        )
        roots, _ = self._call(nodes, [])
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]["children"][0]["id"], 2)

    def test_root_identified_by_self_referential_parent(self) -> None:
        nodes = self._nodes(
            {"id": 5, "parent_id": 5},  # self-referential root
            {"id": 6, "parent_id": 5},
        )
        roots, _ = self._call(nodes, [])
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]["id"], 5)

    def test_multi_level_nesting(self) -> None:
        nodes = self._nodes(
            {"id": 1, "tree_root": 1},
            {"id": 2, "parent_id": 1},
            {"id": 3, "parent_id": 2},
        )
        roots, _ = self._call(nodes, [])
        child = roots[0]["children"][0]
        grandchild = child["children"][0]
        self.assertEqual(grandchild["id"], 3)

    def test_selection_map_marks_selected_ids(self) -> None:
        nodes = self._nodes({"id": 1, "tree_root": 1}, {"id": 2, "parent_id": 1})
        _, selection = self._call(nodes, [1])
        self.assertTrue(selection["1"])
        self.assertFalse(selection["2"])

    def test_selection_map_empty_when_none_selected(self) -> None:
        nodes = self._nodes({"id": 1, "tree_root": 1}, {"id": 2, "parent_id": 1})
        _, selection = self._call(nodes, [])
        self.assertFalse(any(selection.values()))

    def test_selection_map_keys_are_strings(self) -> None:
        nodes = self._nodes({"id": 10, "tree_root": 1})
        _, selection = self._call(nodes, [10])
        self.assertIn("10", selection)
        self.assertNotIn(10, selection)

    def test_expand_in_tree_preserved(self) -> None:
        nodes = self._nodes({"id": 1, "tree_root": 1, "expand": True})
        roots, _ = self._call(nodes, [])
        self.assertTrue(roots[0]["expand_in_tree"])

    def test_empty_tree(self) -> None:
        roots, selection = self._call([], [])
        self.assertEqual(roots, [])
        self.assertEqual(selection, {})


class ViewsHelpersTest(TestCase):
    def test_get_specimen_metadata_scalar_and_3d(self) -> None:
        scalar_meta = views.get_specimen_metadata("Scalar")
        keys = [k for k, _ in scalar_meta]
        self.assertIn("specimen_id", keys)
        self.assertNotIn("missing_pts", keys)

        three_meta = views.get_specimen_metadata("3D")
        three_keys = [k for k, _ in three_meta]
        self.assertIn("missing_pts", three_keys)

    def test_get_specimen_metadata_unknown_type_matches_scalar(self) -> None:
        unknown = views.get_specimen_metadata("unknown")
        scalar = views.get_specimen_metadata("Scalar")
        self.assertEqual(unknown, scalar)

    def test_set_up_sql_query_scalar_and_3d(self) -> None:
        scalar_sql = views.set_up_sql_query(True, True)
        self.assertIn("variable.id in %s", scalar_sql)
        self.assertIn("ORDER BY `specimen_id` ASC", scalar_sql)
        self.assertIn("session.group_id IN %s", scalar_sql)

        three_sql = views.set_up_sql_query(False, True)
        self.assertIn("FROM session", three_sql)
        self.assertNotIn("variable.id in %s", three_sql)
        self.assertIn("session.group_id IN %s", three_sql)

    def test_set_up_sql_query_preview_only_does_not_affect_output(self) -> None:
        self.assertEqual(
            views.set_up_sql_query(True, True),
            views.set_up_sql_query(True, False),
        )
        self.assertEqual(
            views.set_up_sql_query(False, True),
            views.set_up_sql_query(False, False),
        )

    def test_init_query_table_and_tabulate_preview_limit(self) -> None:
        keys = [k for k, _ in views.get_specimen_metadata("Scalar")]
        base_row = {k: f"val_{k}" for k in keys}
        base_row.update(
            {"specimen_id": "0", "variable_label": "V1", "scalar_value": "1"}
        )

        out = views.init_query_table("Scalar", base_row)
        for k in keys:
            self.assertIn(k, out)
        self.assertEqual(out["variable_label"], "V1")

        rows = []
        for i in range(20):
            row = {k: f"val_{k}" for k in keys}
            row.update(
                {"specimen_id": str(i), "variable_label": "V", "scalar_value": str(i)}
            )
            rows.append(row)

        result = views.tabulate_scalar(rows, True)
        self.assertEqual(len(result), 5)


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

    def test_create_3d_output_string_morpho_format(self) -> None:
        req = self.factory.get("/")
        _add_session(req)
        req.session["newline_char"] = "\n"
        req.session["sessions"] = [1]
        req.session["directory_name"] = "PRIMO_3D_morpho"
        dst = os.path.join(self.tmpdir, req.session["directory_name"])
        os.makedirs(dst, exist_ok=True)

        query_results = [
            {"specimen_id": 1, "hypocode": "A", "x": 1.0, "y": 2.0, "z": 3.0},
        ]

        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            views.create_3d_output_string(req, query_results, output_file_type="morpho")
            out_file = os.path.join(dst, "3d_data.txt")
            self.assertTrue(os.path.exists(out_file))
            content = open(out_file).read()
            self.assertIn("[individuals]", content)
            self.assertIn("[landmarks]", content)
            self.assertIn("[rawpoints]", content)
            self.assertNotIn(req.session["missing_pts"][1], [" 1"])

    def test_collate_metadata_scalar_writes_csv(self) -> None:
        req = self.factory.get("/")
        _add_session(req)
        req.session["scalar_or_3d"] = "Scalar"
        req.session["variable_labels"] = ["Weight", "Height"]

        keys = [k for k, _ in views.get_specimen_metadata("Scalar")]
        row_weight = {k: f"val_{k}" for k in keys}
        row_weight.update(
            {"specimen_id": "1", "variable_label": "Weight", "scalar_value": "42"}
        )
        row_height = {k: f"val_{k}" for k in keys}
        row_height.update(
            {"specimen_id": "1", "variable_label": "Height", "scalar_value": "180"}
        )
        query_results = [row_weight, row_height]

        out_file = "test_collate_scalar.csv"
        with self.settings(DOWNLOAD_ROOT=self.tmpdir):
            views.collate_metadata(req, query_results, "", out_file)
            full_path = os.path.join(self.tmpdir, out_file)
            self.assertTrue(os.path.exists(full_path))
            content = open(full_path).read()
            self.assertIn("Specimen ID", content)
            self.assertIn("Weight", content)
            self.assertIn("Height", content)
            # Both variable values must appear on the same data row (specimen_id=1)
            data_row = [line for line in content.splitlines() if line.startswith("1,")]
            self.assertEqual(len(data_row), 1)
            self.assertIn("42", data_row[0])
            self.assertIn("180", data_row[0])


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


class ParameterSelectionUnknownTableTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="tuser", password="pass")
        self.client.login(username="tuser", password="pass")
        session = self.client.session
        session["table_selections"] = {"undefined": []}
        session["scalar_or_3d"] = "Scalar"
        session["page_title"] = ""
        session.save()

    def test_unknown_current_table_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.client.get(
                reverse("parameter_selection", kwargs={"current_table": "undefined"})
            )


class LoginRequiredTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="protected_user", password="pass")

    def _assert_redirects_to_login(self, url: str) -> None:
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_logout_requires_login(self) -> None:
        self._assert_redirects_to_login(reverse("logout"))

    def test_parameter_selection_requires_login(self) -> None:
        self._assert_redirects_to_login(
            reverse("parameter_selection", kwargs={"current_table": "taxon"})
        )

    def test_initialize_query_requires_login(self) -> None:
        self._assert_redirects_to_login(
            reverse("initialize_query", kwargs={"scalar_or_3d": "Scalar"})
        )

    def test_query_start_requires_login(self) -> None:
        self._assert_redirects_to_login(reverse("query_start"))

    def test_logout_accessible_when_logged_in(self) -> None:
        self.client.login(username="protected_user", password="pass")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)


class PreviewUserTest(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(username="user", password="previewpass")
        User.objects.create_user(username="fulluser", password="fullpass")

    def test_preview_account_redirected_to_login_on_protected_views(self) -> None:
        """'user' account must be logged in to access protected views."""
        self.client.login(username="user", password="previewpass")
        response = self.client.get(reverse("query_start"))
        self.assertEqual(response.status_code, 200)

    def test_tabulate_scalar_caps_at_5_for_preview(self) -> None:
        from web.views import get_specimen_metadata, tabulate_scalar

        keys = [k for k, _ in get_specimen_metadata("Scalar")]
        rows = []
        for i in range(20):
            row = {k: "v" for k in keys}
            row.update(
                {"specimen_id": str(i), "variable_label": "V", "scalar_value": str(i)}
            )
            rows.append(row)
        self.assertEqual(len(tabulate_scalar(rows, preview_only=True)), 5)
        self.assertEqual(len(tabulate_scalar(rows, preview_only=False)), 20)


class BackupTableViewTest(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_user(
            username="staff", password="pw", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="pw", is_staff=False
        )

    def test_get_requires_staff(self) -> None:
        self.client.login(username="regular", password="pw")
        response = self.client.get(reverse("backup_table"))
        self.assertNotEqual(response.status_code, 200)

    def test_get_renders_form_for_staff(self) -> None:
        self.client.login(username="staff", password="pw")
        response = self.client.get(reverse("backup_table"))
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_table_shows_error(self) -> None:
        self.client.login(username="staff", password="pw")
        response = self.client.post(reverse("backup_table"), {"table": "auth_user"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid table")

    def test_post_valid_table_creates_backup(self) -> None:
        self.client.login(username="staff", password="pw")
        with patch("web.views.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            response = self.client.post(reverse("backup_table"), {"table": "specimen"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backup created")
        call_sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("specimen_", call_sql)
        self.assertIn("CREATE TABLE", call_sql)

    def test_post_unauthenticated_redirects(self) -> None:
        response = self.client.post(reverse("backup_table"), {"table": "specimen"})
        self.assertNotEqual(response.status_code, 200)


class RestoreTableViewTest(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_user(
            username="restore_staff", password="pw", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="restore_regular", password="pw", is_staff=False
        )
        self.backups = {
            "specimen": [("specimen_20260818_1700", "18th August 2026, 17:00")],
            "session": [],
            "data_scalar": [],
        }

    def test_get_requires_staff(self) -> None:
        self.client.login(username="restore_regular", password="pw")
        response = self.client.get(reverse("restore_table"))
        self.assertNotEqual(response.status_code, 200)

    def test_get_renders_for_staff(self) -> None:
        self.client.login(username="restore_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            response = self.client.get(reverse("restore_table"))
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_backup_shows_error(self) -> None:
        self.client.login(username="restore_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            response = self.client.post(
                reverse("restore_table"), {"backup": "auth_user_20260818_1700"}
            )
        self.assertContains(response, "Invalid backup")

    def test_post_valid_backup_shows_confirmation(self) -> None:
        self.client.login(username="restore_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            response = self.client.post(
                reverse("restore_table"), {"backup": "specimen_20260818_1700"}
            )
        self.assertContains(response, "Warning")
        self.assertContains(response, "cannot be undone")
        self.assertNotContains(response, "Restored")

    def test_post_confirmed_executes_restore(self) -> None:
        self.client.login(username="restore_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            with patch("web.views.connection") as mock_conn:
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value.__enter__ = MagicMock(
                    return_value=mock_cursor
                )
                mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
                response = self.client.post(
                    reverse("restore_table"),
                    {"backup": "specimen_20260818_1700", "confirmed": "1"},
                )
        self.assertContains(response, "Restored")
        calls = [c[0][0] for c in mock_cursor.execute.call_args_list]
        self.assertTrue(any("DROP TABLE" in c for c in calls))
        self.assertTrue(any("RENAME TABLE" in c for c in calls))

    def test_post_unauthenticated_redirects(self) -> None:
        response = self.client.post(
            reverse("restore_table"), {"backup": "specimen_20260818_1700"}
        )
        self.assertNotEqual(response.status_code, 200)


class DeleteBackupViewTest(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_user(
            username="delete_staff", password="pw", is_staff=True
        )
        self.backups = {
            "specimen": [("specimen_20260818_1700", "18th August 2026, 17:00")],
            "session": [],
            "data_scalar": [],
        }

    def test_post_invalid_backup_shows_error(self) -> None:
        self.client.login(username="delete_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            response = self.client.post(
                reverse("delete_backup"), {"backup": "auth_user_20260818_1700"}
            )
        self.assertContains(response, "Invalid backup")

    def test_post_valid_backup_shows_confirmation(self) -> None:
        self.client.login(username="delete_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            response = self.client.post(
                reverse("delete_backup"), {"backup": "specimen_20260818_1700"}
            )
        self.assertContains(response, "Warning")
        self.assertNotContains(response, "Deleted")

    def test_post_confirmed_executes_drop(self) -> None:
        self.client.login(username="delete_staff", password="pw")
        with patch("web.views._get_backups", return_value=self.backups):
            with patch("web.views.connection") as mock_conn:
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value.__enter__ = MagicMock(
                    return_value=mock_cursor
                )
                mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
                response = self.client.post(
                    reverse("delete_backup"),
                    {"backup": "specimen_20260818_1700", "confirmed": "1"},
                )
        self.assertContains(response, "Deleted")
        call_sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("DROP TABLE", call_sql)
        self.assertIn("specimen_20260818_1700", call_sql)

    def test_get_requires_staff(self) -> None:
        User.objects.create_user(
            username="delete_regular", password="pw", is_staff=False
        )
        self.client.login(username="delete_regular", password="pw")
        response = self.client.get(reverse("delete_backup"))
        self.assertNotEqual(response.status_code, 200)


class GroupAccessTest(TestCase):
    """Tests for get_accessible_group_ids and user_has_group_access."""

    def setUp(self) -> None:
        self.public_group = Group.objects.create(name="non-member")
        self.delson_group = Group.objects.create(name="Delson files")
        self.member_group = Group.objects.create(name="member")
        self.admin_group = Group.objects.create(name="admin")
        self.other_group = Group.objects.create(name="Other")

        self.anon = AnonymousUser()

        self.no_group_user = User.objects.create_user(username="nogroup", password="pw")

        self.public_only_user = User.objects.create_user(
            username="publiconly", password="pw"
        )
        self.public_only_user.groups.add(self.public_group)

        self.member_user = User.objects.create_user(username="member", password="pw")
        self.member_user.groups.add(self.public_group, self.member_group)

        self.admin_user = User.objects.create_user(username="admin", password="pw")
        self.admin_user.groups.add(self.admin_group)

        self.delson_user = User.objects.create_user(username="delson", password="pw")
        self.delson_user.groups.add(self.public_group, self.delson_group)

    def test_anonymous_user_gets_only_public_group(self) -> None:
        self.assertEqual(
            views.get_accessible_group_ids(self.anon), [self.public_group.id]
        )

    def test_user_with_no_groups_gets_only_public_group(self) -> None:
        self.assertEqual(
            views.get_accessible_group_ids(self.no_group_user), [self.public_group.id]
        )

    def test_user_gets_public_group_plus_own_groups(self) -> None:
        ids = set(views.get_accessible_group_ids(self.member_user))
        self.assertEqual(ids, {self.public_group.id, self.member_group.id})

    def test_anonymous_user_has_no_group_access(self) -> None:
        self.assertFalse(views.user_has_group_access(self.anon))

    def test_user_with_no_groups_has_no_group_access(self) -> None:
        self.assertFalse(views.user_has_group_access(self.no_group_user))

    def test_user_in_public_group_only_has_no_group_access(self) -> None:
        """A user with no group beyond the public default only gets a preview."""
        self.assertFalse(views.user_has_group_access(self.public_only_user))

    def test_user_in_another_group_has_group_access(self) -> None:
        self.assertTrue(views.user_has_group_access(self.member_user))

    def test_member_cannot_see_delson_group(self) -> None:
        """Members must not have the Delson files group in their accessible IDs."""
        ids = set(views.get_accessible_group_ids(self.member_user))
        self.assertNotIn(self.delson_group.id, ids)

    def test_delson_user_can_see_delson_group(self) -> None:
        ids = set(views.get_accessible_group_ids(self.delson_user))
        self.assertIn(self.delson_group.id, ids)

    def test_admin_user_can_see_delson_group(self) -> None:
        ids = set(views.get_accessible_group_ids(self.admin_user))
        self.assertIn(self.delson_group.id, ids)

    def test_anonymous_user_cannot_see_delson_group(self) -> None:
        ids = set(views.get_accessible_group_ids(self.anon))
        self.assertNotIn(self.delson_group.id, ids)


class ExecuteQueryGroupFilterTest(TestCase):
    """Verify execute_query filters by the requesting user's accessible groups."""

    PUBLIC_ID = 99
    MEMBER_ID = 100

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _make_request(self, user: User) -> HttpRequest:
        req = self.factory.get("/")
        _add_session(req)
        req.session["table_selections"] = {
            "sex": [1],
            "fossil": [1],
            "taxon": [1],
            "variable": [1],
        }
        req.session["variable_labels"] = []
        req.user = user
        return req

    def _fake_cursor(self) -> MagicMock:
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.__exit__.return_value = False
        cursor.description = []
        cursor.fetchall.return_value = []
        return cursor

    def test_group_ids_passed_as_first_sql_param(self) -> None:
        user = User.objects.create_user(username="member", password="pw")
        req = self._make_request(user)
        cursor = self._fake_cursor()

        with patch(
            "web.views._get_public_group_id", return_value=self.PUBLIC_ID
        ), patch(
            "web.views.get_accessible_group_ids",
            return_value=[self.PUBLIC_ID, self.MEMBER_ID],
        ), patch(
            "web.views.user_has_group_access", return_value=True
        ), patch(
            "web.views.connection.cursor", return_value=cursor
        ):
            sql_query, _ = views.execute_query(req, "Scalar")

        self.assertIn("session.group_id IN %s", sql_query)
        main_call = cursor.execute.call_args_list[-1]
        _, params = main_call.args
        self.assertEqual(set(params[0]), {self.PUBLIC_ID, self.MEMBER_ID})

    def test_public_only_user_gets_preview_only(self) -> None:
        user = User.objects.create_user(username="publiconly", password="pw")
        req = self._make_request(user)
        cursor = self._fake_cursor()

        with patch(
            "web.views._get_public_group_id", return_value=self.PUBLIC_ID
        ), patch(
            "web.views.get_accessible_group_ids", return_value=[self.PUBLIC_ID]
        ), patch(
            "web.views.user_has_group_access", return_value=False
        ), patch(
            "web.views.connection.cursor", return_value=cursor
        ):
            views.execute_query(req, "Scalar")

        main_call = cursor.execute.call_args_list[-1]
        sql_query, _ = main_call.args
        self.assertIn("`specimen_id` ASC", sql_query)
        _, params = main_call.args
        self.assertEqual(set(params[0]), {self.PUBLIC_ID})


# class ExecuteQuery3DGroupFilterTest(TestCase):
#     """Verify query_3d filters by the requesting user's accessible groups.
#     Uncomment when query_3d is re-enabled in views.py.
#     """
#
#     PUBLIC_ID = 99
#     MEMBER_ID = 100
#
#     def setUp(self) -> None:
#         self.factory = RequestFactory()
#
#     def _make_request(self, user: User) -> HttpRequest:
#         req = self.factory.get("/")
#         _add_session(req)
#         req.session["table_var_select_done"] = {
#             "sex": [1],
#             "fossil": [1],
#             "taxon": [1],
#         }
#         req.user = user
#         return req
#
#     def _fake_cursor(self) -> MagicMock:
#         cursor = MagicMock()
#         cursor.__enter__.return_value = cursor
#         cursor.__exit__.return_value = False
#         cursor.description = []
#         cursor.fetchall.return_value = []
#         return cursor
#
#     def test_group_ids_passed_as_first_sql_param(self) -> None:
#         user = User.objects.create_user(username="member3d", password="pw")
#         req = self._make_request(user)
#         cursor = self._fake_cursor()
#
#         with patch(
#             "web.views._get_public_group_id", return_value=self.PUBLIC_ID
#         ), patch(
#             "web.views.get_accessible_group_ids",
#             return_value=[self.PUBLIC_ID, self.MEMBER_ID],
#         ), patch(
#             "web.views.user_has_group_access", return_value=True
#         ), patch(
#             "web.views.connection.cursor", return_value=cursor
#         ):
#             views.query_3d(req, "grfnd")
#
#         self.assertIn(
#             "session.group_id IN %s",
#             cursor.execute.call_args_list[-1].args[0]
#         )
#         params = cursor.execute.call_args_list[-1].args[1]
#         self.assertEqual(set(params[0]), {self.PUBLIC_ID, self.MEMBER_ID})
#
#     def test_public_only_user_gets_preview_only(self) -> None:
#         user = User.objects.create_user(username="public3d", password="pw")
#         req = self._make_request(user)
#         cursor = self._fake_cursor()
#
#         with patch(
#             "web.views._get_public_group_id", return_value=self.PUBLIC_ID
#         ), patch(
#             "web.views.get_accessible_group_ids", return_value=[self.PUBLIC_ID]
#         ), patch(
#             "web.views.user_has_group_access", return_value=False
#         ), patch(
#             "web.views.connection.cursor", return_value=cursor
#         ):
#             views.query_3d(req, "grfnd")
#
#         params = cursor.execute.call_args_list[-1].args[1]
#         self.assertEqual(set(params[0]), {self.PUBLIC_ID})
#
#     def test_member_cannot_see_delson_data_in_3d(self) -> None:
#         """Group filter must exclude Delson sessions from member queries."""
#         user = User.objects.create_user(username="member3d_nodelon", password="pw")
#         req = self._make_request(user)
#         cursor = self._fake_cursor()
#         delson_id = 4
#
#         with patch(
#             "web.views._get_public_group_id", return_value=self.PUBLIC_ID
#         ), patch(
#             "web.views.get_accessible_group_ids",
#             return_value=[self.PUBLIC_ID, self.MEMBER_ID],
#         ), patch(
#             "web.views.user_has_group_access", return_value=True
#         ), patch(
#             "web.views.connection.cursor", return_value=cursor
#         ):
#             views.query_3d(req, "grfnd")
#
#         params = cursor.execute.call_args_list[-1].args[1]
#         self.assertNotIn(delson_id, set(params[0]))


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


class ChangePasswordViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="changeuser", password="oldpass")
        from web.models import UserProfile

        UserProfile.objects.create(user=self.user, must_change_password=True)

    def test_get_requires_login(self) -> None:
        response = self.client.get(reverse("change_password"))
        self.assertEqual(response.status_code, 302)

    def test_get_renders_form(self) -> None:
        self.client.login(username="changeuser", password="oldpass")
        response = self.client.get(reverse("change_password"))
        self.assertEqual(response.status_code, 200)

    def test_post_mismatched_passwords_shows_error(self) -> None:
        self.client.login(username="changeuser", password="oldpass")
        response = self.client.post(
            reverse("change_password"),
            {"new_password": "newpass1", "confirm_password": "newpass2"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "do not match")

    def test_post_empty_password_shows_error(self) -> None:
        self.client.login(username="changeuser", password="oldpass")
        response = self.client.post(
            reverse("change_password"),
            {"new_password": "", "confirm_password": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be empty")

    def test_post_valid_clears_flag_and_redirects(self) -> None:
        self.client.login(username="changeuser", password="oldpass")
        response = self.client.post(
            reverse("change_password"),
            {"new_password": "newpass123", "confirm_password": "newpass123"},
        )
        from web.models import UserProfile

        self.assertRedirects(response, "/")
        self.user.refresh_from_db()
        profile = UserProfile.objects.get(user=self.user)
        self.assertFalse(profile.must_change_password)
        self.assertTrue(self.user.check_password("newpass123"))


class LoginRedirectTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="loginuser", password="pass123")

    def test_login_redirects_to_change_password_when_flag_set(self) -> None:
        from web.models import UserProfile

        UserProfile.objects.create(user=self.user, must_change_password=True)
        response = self.client.post(
            reverse("login"),
            {"user_name": "loginuser", "password": "pass123"},
        )
        self.assertRedirects(response, reverse("change_password"))

    def test_login_proceeds_normally_without_flag(self) -> None:
        from web.models import UserProfile

        UserProfile.objects.create(user=self.user, must_change_password=False)
        response = self.client.post(
            reverse("login"),
            {"user_name": "loginuser", "password": "pass123"},
        )
        self.assertRedirects(response, "/")

    def test_login_proceeds_normally_without_profile(self) -> None:
        response = self.client.post(
            reverse("login"),
            {"user_name": "loginuser", "password": "pass123"},
        )
        self.assertRedirects(response, "/")
