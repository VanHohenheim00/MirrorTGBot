from tortoise.models import Model
from tortoise import fields


class Token(Model):
    address = fields.CharField(max_length=100, null=True)
    name = fields.CharField(max_length=50)
    symbol = fields.CharField(max_length=50)
    decimals = fields.IntField(default=0)


class UniSwaps(Model):
    uni_id = fields.CharField(max_length=100, unique=True)
    tx_id = fields.CharField(max_length=66)
    buy = fields.BooleanField(default=False)
    pair = fields.CharField(max_length=100, default="")
    timestamp = fields.BigIntField(default=0)
    from_user = fields.CharField(max_length=42)
    token0 = fields.ForeignKeyField("models.Token", related_name="uni_0")
    token0amount = fields.FloatField()
    token1 = fields.ForeignKeyField("models.Token", related_name="uni_1")
    token1amount = fields.FloatField()
    amount_usd = fields.FloatField()
    price_usd = fields.FloatField()


class UniLiq(Model):
    uni_id = fields.CharField(max_length=100, unique=True)
    tx_id = fields.CharField(max_length=66)
    add = fields.BooleanField()
    pair = fields.CharField(max_length=100, default="")
    timestamp = fields.BigIntField(default=0)
    from_user = fields.CharField(max_length=42)
    token0 = fields.ForeignKeyField("models.Token", related_name="lq_0")
    token0amount = fields.FloatField()
    token1 = fields.ForeignKeyField("models.Token", related_name="lq_1")
    token1amount = fields.FloatField()
    amount_usd = fields.FloatField()
    price_usd = fields.FloatField()



