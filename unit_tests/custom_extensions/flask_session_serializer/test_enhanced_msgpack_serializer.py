from unittest import TestCase
from unittest.mock import MagicMock

from jwt_validation.models import JWTPayload, SearchPrinciple
from landregistry.exceptions import ApplicationError
from server.custom_extensions.flask_session_serializer.enhanced_msgpack_serializer import EnhancedMsgpackSerializer

from server import main
from server.models.searches import SearchState
from unit_tests.utilities_tests import super_test_context


class TestEnhancedMsgpackSerializer(TestCase):
    def setUp(self):
        main.app.config["TESTING"] = True
        main.app.config["WTF_CSRF_ENABLED"] = False
        main.app.testing = True
        self.maxDiff = None

    def test_dictify_dict(self):
        with super_test_context(main.app):
            state = SearchState()
            principle = SearchPrinciple("id", "first_name", "surname", "Active", "an@email.com")
            jwtpayload = JWTPayload("iss", "aud", 1, 2, "sub", "source", principle)
            result = EnhancedMsgpackSerializer(main.app)._dictify({"a": "dict", "b": state, "c": [jwtpayload]})

            self.assertEqual(result, {
                'a': 'dict',
                'b': {
                    '_$module': 'server.models.searches',
                    '_$type': 'SearchState',
                    'address': None,
                    'charges': None,
                    'free-search-id': None,
                    'parent-search': None,
                    'previously-completed': None,
                    'search-extent': None,
                    'search-reference': None},
                'c': [{
                    '_$module': 'jwt_validation.models',
                    '_$type': 'JWTPayload',
                    'aud': 'aud',
                    'exp': 1,
                    'iat': 2,
                    'iss': 'iss',
                    'principle': {
                        '$type': 'xri://landregistry.gov.uk/search/user',
                        'email': 'an@email.com',
                        'first_name': 'first_name',
                        'id': 'id',
                        'status': 'Active',
                        'surname': 'surname'},
                    'source': 'source',
                    'sub': 'sub'
                }]
            })

    def test_objify(self):
        input_json = {
            'a': 'dict',
            'b': {
                '_$module': 'server.models.searches',
                '_$type': 'SearchState',
                'address': None,
                'charges': None,
                'free-search-id': None,
                'parent-search': None,
                'previously-completed': None,
                'search-extent': None,
                'search-reference': None},
            'c': [{
                '_$module': 'jwt_validation.models',
                '_$type': 'JWTPayload',
                'aud': 'aud',
                'exp': 1,
                'iat': 2,
                'iss': 'iss',
                'principle': {
                    '$type': 'xri://landregistry.gov.uk/search/user',
                    'email': 'an@email.com',
                    'first_name': 'first_name',
                    'id': 'id',
                    'status': 'Active',
                    'surname': 'surname'},
                'source': 'source',
                'sub': 'sub'
            }]
        }
        result = EnhancedMsgpackSerializer(main.app)._objify(input_json)

        self.assertEqual(result['a'], 'dict')
        self.assertEqual(type(result['b']).__module__, 'server.models.searches')
        self.assertEqual(type(result['b']).__name__, 'SearchState')
        self.assertEqual(type(result['c'][0]).__module__, 'jwt_validation.models')
        self.assertEqual(type(result['c'][0]).__name__, 'JWTPayload')

    def test_objify_not_allowed(self):
        input_json = {
            'a': {
                '_$module': 'server.main',
                '_$type': 'Aardvark'
            }
        }
        with self.assertRaises(ApplicationError) as exc:
            EnhancedMsgpackSerializer(main.app)._objify(input_json)
        self.assertEqual(exc.exception.message, "Deserialization of module 'server.main' not allowed")

    def test_encode_ok(self):
        serializer = EnhancedMsgpackSerializer(main.app)
        serializer.encoder = MagicMock()
        serializer.encoder.encode.return_value = "encoded thing"
        result = serializer.encode("something")
        self.assertEqual(result, "encoded thing")

    def test_encode_exc(self):
        serializer = EnhancedMsgpackSerializer(main.app)
        serializer.encoder = MagicMock()
        serializer.encoder.encode.side_effect = ApplicationError("Aardvark")
        with self.assertRaises(Exception) as exc:
            serializer.encode("something")
        self.assertEqual(exc.exception.message, "Aardvark")

    def test_decode_ok(self):
        serializer = EnhancedMsgpackSerializer(main.app)
        serializer.decoder = MagicMock()
        serializer.decoder.decode.return_value = "unencoded thing"
        result = serializer.decode("something")
        self.assertEqual(result, "unencoded thing")

    def test_decode_exc(self):
        serializer = EnhancedMsgpackSerializer(main.app)
        serializer.decoder = MagicMock()
        serializer.decoder.decode.side_effect = ApplicationError("Aardvark")
        with self.assertRaises(Exception) as exc:
            serializer.decode("something")
        self.assertEqual(exc.exception.message, "Aardvark")
