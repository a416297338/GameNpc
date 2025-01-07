ACTION_LIST_2 = (
    'idle', 'stop', 'forward', 'backward', 'move_hero', 'move_soldier', 'move_grass',
    'right', 'upright', 'up', 'upleft', 'left', 'downleft', 'down', 'downright',
    'atk_hero', 'atk_soldier', 'atk_matser', 'atk_boss', 'atk_tower', 'spl1', 'spl2',
    'spl3', 'spl4', 'spl1_soldier', 'spl2_soldier', 'spl3_soldier', 'common10000',
    'cancel_common10000', 'summoner1_pur', 'summoner1_esc', 'summoner2', 'combo1',
    'combo2'
)

action_id_mapping = {action: index for index, action in enumerate(ACTION_LIST_2)}

for action, id in action_id_mapping.items():
    print(f"{action.upper()} = {id}")