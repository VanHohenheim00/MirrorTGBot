from tortoise import Model, fields
from enum import IntEnum


class TypeOfChains(IntEnum):
    uniswap = 0
    pancakeswap = 1


class LiveGate(Model):
    chat_id = fields.BigIntField()
    pair = fields.CharField(max_length=100, default="")
    alert_type = fields.IntEnumField(TypeOfChains, default=TypeOfChains.uniswap)
    active = fields.BooleanField(default=False)

