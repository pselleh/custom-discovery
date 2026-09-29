"""Exercise the loader with mocked CMS services; no production connection."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch


SCRIPT = Path(__file__).resolve().parents[1] / 'import_cba_studio_courses.py'


class LoaderTests(unittest.TestCase):
    def run_loader(self, defer=True, validate=False):
        modules = {}
        for name, attrs in {
            'django.contrib.auth': ['get_user_model'],
            'django.db.models': ['Q'],
            'opaque_keys.edx.keys': ['CourseKey'],
            'cms.djangoapps.contentstore.views.course': ['create_new_course'],
            'xmodule.contentstore.content': ['StaticContent'],
            'xmodule.contentstore.django': ['contentstore'],
            'xmodule.modulestore.django': ['modulestore'],
        }.items():
            module = types.ModuleType(name)
            for attr in attrs:
                setattr(module, attr, MagicMock())
            modules[name] = module
        modules['opaque_keys.edx.keys'].CourseKey.from_string.side_effect = lambda key: key
        store = modules['xmodule.modulestore.django'].modulestore.return_value
        store.has_course.return_value = True
        course = store.get_course.return_value
        course.course_image = 'existing.jpg'
        record = {
            'course_key': 'course-v1:CBA+ORF101M01C01+2027',
            'organization': 'CBA', 'course_number': 'ORF101M01C01',
            'course_run': '2027', 'title': 'Test course', 'pacing': 'self_paced',
            'catalog_status': 'waitlist_open', 'catalog_visibility': 'public',
            'access_scope': 'public',
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'catalog.json'
            path.write_text(json.dumps({'microcourses': [record]}))
            output = io.StringIO()
            env = {
                'CBA_CATALOG_FILE': str(path), 'CBA_STUDIO_USER': 'operator',
                'CBA_DEFER_IMAGES': str(defer), 'CBA_UPDATE_EXISTING': 'true',
                'CBA_VALIDATE_ONLY': str(validate),
            }
            with patch.dict(sys.modules, modules), patch.dict(os.environ, env), contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                runpy.run_path(str(SCRIPT))
        return json.loads(output.getvalue()), store, course, modules

    def test_deferred_update_preserves_image_and_uploads_nothing(self):
        summary, store, course, modules = self.run_loader()
        self.assertEqual(course.course_image, 'existing.jpg')
        store.update_item.assert_called_once()
        modules['xmodule.contentstore.django'].contentstore.assert_not_called()
        self.assertEqual(summary['uploaded_images'], [])
        self.assertTrue(summary['images_deferred'])

    def test_validate_only_writes_nothing(self):
        summary, store, course, modules = self.run_loader(validate=True)
        store.update_item.assert_not_called()
        self.assertEqual(len(summary['would_update']), 1)
        self.assertEqual(summary['would_upload_images'], [])
        modules['cms.djangoapps.contentstore.views.course'].create_new_course.assert_not_called()

    def test_normal_import_still_requires_images(self):
        with self.assertRaises(SystemExit) as result:
            self.run_loader(defer=False)
        self.assertEqual(result.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
