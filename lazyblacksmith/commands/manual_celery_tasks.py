# -*- encoding: utf-8 -*-
from flask.ext.script import Command
from flask.ext.script import Option

from lazyblacksmith.tasks.adjusted_price import update_adjusted_price
from lazyblacksmith.tasks.market_order import update_market_price


class ManualCeleryTasks(Command):
    """
    Manually trigger tasks.
    """

    option_list = (
        Option('--action', '-a', dest='action', default=None, help='Action. update_adjusted_price, update_market_price'),
    )

    def run(self, action):
        if action is None:
            print "Error: You must specify at least an action"
            return
        if action == 'update_adjusted_price':
            update_adjusted_price()
        if action == 'update_market_price':
            update_market_price()
