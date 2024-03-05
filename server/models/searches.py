from marshmallow import fields, post_load, EXCLUDE
from server.models.common import BaseSchema, jsonnamedlist


class SearchStateSchema(BaseSchema):
    """Schema for a free search"""
    search_extent = fields.Dict(allow_none=True)
    charges = fields.List(fields.Dict(), allow_none=True)
    address = fields.Str(allow_none=True)
    parent_search = fields.Int(allow_none=True)
    search_reference = fields.Str(allow_none=True)
    previously_completed = fields.Bool(allow_none=True)
    free_search_id = fields.Str(allow_none=True)

    @post_load
    def create_state(self, data, **kwargs):
        return SearchState(**data)


class PaymentStateSchema(BaseSchema):
    """Schema for a gov pay transaction"""
    payment_id = fields.Str()
    description = fields.Str()
    state = fields.Dict()
    reference = fields.Str()
    amount = fields.Int()
    payment_provider = fields.Str(allow_none=True)
    card_brand = fields.Str(allow_none=True)

    class Meta:
        # Using exclude here since govpay send back a lot of things we don't care about
        unknown = EXCLUDE

    @post_load
    def create_state(self, data, **kwargs):
        return PaymentState(**data)


class BasePaidSearchItemSchema(BaseSchema):
    """Schema for a paid search"""
    search_id = fields.Int()
    parent_search_id = fields.Int(allow_none=True)
    user_id = fields.UUID(allow_none=True)
    payment_id = fields.Str()
    charges = fields.List(fields.Dict(), allow_none=True)
    search_extent = fields.Dict()
    search_date = fields.DateTime()
    search_area_description = fields.Str(allow_none=True)
    document_url = fields.Str(allow_none=True)
    lapsed_date = fields.DateTime(allow_none=True)
    payment_provider = fields.Str(allow_none=True)
    card_brand = fields.Str(allow_none=True)
    amount = fields.Int(allow_none=True)
    reference = fields.Str(allow_none=True)

    @post_load
    def create_state(self, data, **kwargs):
        return PaidSearchItem(**data)


class PaidSearchItemSchema(BasePaidSearchItemSchema):
    """Schema for a paid search"""
    repeat_searches = fields.List(fields.Nested(BasePaidSearchItemSchema), allow_none=True)

    @post_load
    def create_state(self, data, **kwargs):
        return PaidSearchItem(**data)


search_state_class = jsonnamedlist(
    SearchStateSchema(),
    "SearchState",
    "search_extent, charges, address, parent_search, search_reference, previously_completed, free_search_id",
    default=None)


class SearchState(search_state_class):
    pass


payment_state_class = jsonnamedlist(
    PaymentStateSchema(), "PaymentState", "payment_id, description, state, reference, amount, \
                                           payment_provider, card_brand", default=None)


class PaymentState(payment_state_class):
    pass


paid_search_item_class = jsonnamedlist(
    PaidSearchItemSchema(),
    "PaidSearch", "search_id, parent_search_id, user_id, payment_id, charges, \
                    search_extent, search_area_description, search_date, document_url, lapsed_date, repeat_searches, \
                    payment_provider, card_brand, amount, reference",
    default=None)


class PaidSearchItem(paid_search_item_class):
    pass
