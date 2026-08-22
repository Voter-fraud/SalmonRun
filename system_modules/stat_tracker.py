from ui_modules import inventory
from system_modules.fishing_quests import QuestSystem

class StatTracker:
    def __init__(self):
        self.fish_caught = inventory.Item.ret_items('is_fish')
        self.fish_sold = inventory.Item.ret_items('is_fish')
        self.npcs_talked_to = {  # add a npc comprehension type thing later
            'old_man': 0,
            'total': 0
        }

    def catch_fish(self, fish_name):
        self.fish_caught[fish_name] += 1
        self.fish_caught['total'] += 1
        if QuestSystem.cur_quest().quest_type == 'catch_fish':
            QuestSystem.cur_quest().update(player_tracker.fish_caught)

    def sell_fish(self, fish_name):
        self.fish_sold[fish_name] += 1
        self.fish_sold['total'] += 1
        if QuestSystem.cur_quest().quest_type == 'sell':
            QuestSystem.cur_quest().update(player_tracker.fish_sold)

    def talk_to(self, npc_name):
        self.npcs_talked_to[npc_name] += 1
        self.npcs_talked_to['total'] += 1
        if QuestSystem.cur_quest().quest_type == 'talk_to':
            print(self.npcs_talked_to)
            QuestSystem.cur_quest().update(self.npcs_talked_to)

player_tracker = StatTracker()
