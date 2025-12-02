from pydantic import GetCoreSchemaHandler

from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        # Accept string → convert to ObjectId
        # Validator may be called with an additional `info` argument by
        # pydantic-core; accept it to avoid a TypeError when two args are passed.
        def validate(value, _info=None):
            if isinstance(value, ObjectId):
                return value
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        # VALIDATOR MUST BE IN PYTHON BRANCH ONLY
                        core_schema.general_plain_validator_function(validate),
                    ]
                ),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # JSON schema MUST NOT include validator functions
        return {"type": "string", "example": "60ad8f02c45e88b6f8e4b6e2"}
