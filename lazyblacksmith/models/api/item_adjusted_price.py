# -*- encoding: utf-8 -*-
from . import db


class ItemAdjustedPrice(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    price = db.Column(
        db.Numeric(
            precision=17,
            scale=2,
            decimal_return_scale=2,
            asdecimal=False
        ),
        nullable=True
    )
