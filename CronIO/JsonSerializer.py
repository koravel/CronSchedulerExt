import json


class JSONSerializer:
    @staticmethod
    def encode(obj, extended_encoder=None):
        return json.dumps(obj=obj, sort_keys=True, indent=4, cls=extended_encoder)

    @staticmethod
    def decode(obj, extended_decoder=None):
        try:
            return json.loads(s=obj, cls=extended_decoder)
        except json.JSONDecodeError:
            return None
