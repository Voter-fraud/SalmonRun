"""
This module defines several functions for use in bait buying buttons.

It is a tertiary level module and imports of it should be handled with care.
"""

import balance
import inventory

def buy(cost, item):
    """Buys a bait item, used exclusively locally"""
    if balance.balance.bal - cost >= 0:
        balance.balance.use_money(cost)
        inventory.inventory.add_item(inventory.Item.items[item])
    inventory.inventory.draw((0, 0))
    balance.balance.draw()

def r_upd():
    """empty update function for bait buying buttons"""
    return 0

def worm_toggle():
    """button toggle function for buying worm bait"""
    buy(5, 'worms')

def plastic_bait_toggle():
    """button toggle function for buying plastic bait"""
    buy(2, 'plastic_bait')

def insect_bait_toggle():
    """button toggle function for buying insect bait"""
    buy(4, 'insect_bait')

def minnow_toggle():
    """button toggle function for buying minnow bait"""
    buy(12, 'minnow')