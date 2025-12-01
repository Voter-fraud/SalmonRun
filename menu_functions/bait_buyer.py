import balance
import inventory

def r_toggle(cost, item):
    if balance.balance.bal - cost >= 0:
        balance.balance.use_money(cost)
        inventory.inventory.add_item(inventory.Item.items[item])
    inventory.inventory.draw((0, 0))
    balance.balance.draw()

def r_upd():
    return 0

def worm_toggle():
    r_toggle(5, 'worms')