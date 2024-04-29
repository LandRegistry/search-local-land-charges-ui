import importlib
from msgspec.msgpack import Encoder, Decoder
from flask_babel.speaklater import LazyString
from flask_session.base import Serializer, ServerSideSession
from jwt_validation.models import JWTPayload, JWTPayloadSchema
from flask import Flask
from landregistry.exceptions import ApplicationError

# Restrict classes from within the following modules to prevent nefarious object creation
ALLOWED_MODULES = [
    "server.models.charges",
    "server.models.searches",
    "jwt_validation.models",
]


class EnhancedMsgpackSerializer(Serializer):
    """Customized Serializer for flask-session using msgpack since the built-in one doesn't put things back into
    objects"""

    def __init__(self, app: Flask):
        self.app: Flask = app
        self.encoder = Encoder()
        self.decoder = Decoder()

    def _dictify(self, obj):
        """Convert any recognised objects to dicts ready to encode with msgpack"""
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                new_dict[key] = self._dictify(value)
            return new_dict
        if hasattr(obj, "to_json"):
            obj_dict = obj.to_json()
            # Add type and module to dict so we can pull them out and reconstitute the object
            obj_dict["_$type"] = type(obj).__name__
            obj_dict["_$module"] = type(obj).__module__
            return obj_dict
        if isinstance(obj, JWTPayload):
            obj_dict = JWTPayloadSchema().dump(obj)
            # Add type and module to dict so we can pull them out and reconstitute the object
            obj_dict["_$type"] = type(obj).__name__
            obj_dict["_$module"] = type(obj).__module__
            return obj_dict
        if isinstance(obj, LazyString):
            return str(obj)
        if hasattr(obj, "__iter__") and not isinstance(obj, str):
            new_list = []
            for sub_obj in obj:
                new_list.append(self._dictify(sub_obj))
            return new_list

        # Otherwise just let msgpack encoder try and serialize it
        return obj

    def _objify(self, un_obj):
        """Run through the deserialized dict and reconstitute any recognised objects"""
        if isinstance(un_obj, dict):
            obj_type = un_obj.pop("_$type", None)
            obj_module = un_obj.pop("_$module", None)
            if obj_type and obj_module:
                if obj_module not in ALLOWED_MODULES:
                    raise ApplicationError(
                        f"Deserialization of module '{obj_module}' not allowed"
                    )
                module = importlib.import_module(obj_module)
                obj_class = getattr(module, obj_type)
                if obj_type == "JWTPayload":
                    return JWTPayloadSchema().load(un_obj)
                else:
                    return obj_class.from_json(un_obj)
            new_dict = {}
            for key, value in un_obj.items():
                new_dict[key] = self._objify(value)
            return new_dict
        elif hasattr(un_obj, "__iter__") and not isinstance(un_obj, str):
            new_list = []
            for sub_un_obj in un_obj:
                new_list.append(self._objify(sub_un_obj))
            return new_list
        return un_obj

    def encode(self, session: ServerSideSession) -> bytes:
        """Serialize the session data."""
        try:
            dicted = self._dictify(session)
            return self.encoder.encode(dicted)
        except Exception as e:
            self.app.logger.error(f"Failed to serialize session data: {e}")
            raise

    def decode(self, serialized_data: bytes) -> dict:
        """Deserialize the session data."""
        try:
            plain_dict = self.decoder.decode(serialized_data)
            return self._objify(plain_dict)
        except Exception as e:
            self.app.logger.error(f"Failed to deserialize session data: {e}")
            raise
