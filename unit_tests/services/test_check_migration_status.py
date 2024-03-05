from unittest import TestCase, mock

from server.services.check_migration_status import CheckMigrationStatus
from server.main import app
from flask import g


class TestCheckMigrationStatus(TestCase):
    CHECK_MIGRATION_STATUS_PATH = 'server.services.check_migration_status'

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_in_minus_buffer(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": ['Another authority'],
                "includes_scotland": False,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": ['Another authority'],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "fail")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_in_minus_buffer_scotland(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "fail_scotland")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_maintenance_plus(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": ["Another authority"]
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "fail_maintenance_contact")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_maintenance_minus(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": ["Another authority"]
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": ["Another authority"]
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "fail_maintenance")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_no_authorities(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": [],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "fail_no_authority")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_in_plus_buffer(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": ['Another authority'],
                "includes_scotland": False,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "warning")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_in_plus_buffer_scotland(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": True,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "warning")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_not_in_buffer(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": [],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000]
                            ]
                        ]
                    },
                    "properties": {"id": 1519313947379}
                }
            ]
        }

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertEqual(response['flag'], "pass")

    @mock.patch("{}.LocalAuthorityAPIService".format(CHECK_MIGRATION_STATUS_PATH))
    def test_extent_no_box(self, mock_local_authority_api_service):

        mock_local_authority_api_service.plus_minus_buffer.return_value = {
            "migrated_list": ["An authority"],
            "plus_buffer": {
                "non_migrated_list": ["Another authority"],
                "includes_scotland": False,
                "maintenance_list": []
            },
            "minus_buffer": {
                "non_migrated_list": ["Another authority"],
                "includes_scotland": False,
                "maintenance_list": []
            }
        }

        bounding_box = {}

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                response = CheckMigrationStatus.process(bounding_box)

        self.assertIsNone(response)
