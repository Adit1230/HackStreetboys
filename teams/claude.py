from teams.helper_function import Troops, Utils
import numpy as np
import random

team_name = "TowerTactics"

troops = [Troops.wizard, Troops.minion, Troops.archer, Troops.valkyrie, Troops.dragon, Troops.skeleton, Troops.giant, Troops.musketeer]

deploy_list = Troops([])

team_signal = "[['', '', '', '', '', '', '', ''], ['', '', '', ''], 10, 0, {'elixir_advantage': 0, 'last_push_time': 0, 'strategy': 'adaptive', 'defending': False, 'pattern_memory': {}}]"

def deploy(arena_data: dict):
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def update_signal(team_signal, arena_data):
    troop_names = {'A': 'Archer', 'm': 'Minion', 'K': 'Knight', 'S': 'Skeleton', 'D': 'Dragon', 'V': 'Valkyrie', 'M': 'Musketeer', 'G': 'Giant', 'P': 'Prince', 'b': 'Barbarian', 'B': 'Balloon', 'W': 'Wizard', '': ''}
    troop_codes = {t: c for (c, t) in troop_names.items()}
    troop_elixirs = {"Archer": 3, "Minion": 3, "Knight": 3, "Skeleton": 3, "Dragon": 4, "Valkyrie": 4, "Musketeer": 4, "Giant": 5, "Prince": 5, "Barbarian": 3, "Balloon": 5, "Wizard": 5}
    
    opp_data = eval(team_signal)
    memory = opp_data[4]
    
    for troop in arena_data['OppTroops']:
        if troop_codes[troop.name] not in opp_data[0]:
            for i in range(8):
                if opp_data[0][i] == '':
                    opp_data[0][i] = troop_codes[troop.name]
                    break
        if (troop.uid > opp_data[3]) and (troop_codes[troop.name] not in opp_data[1]):
            opp_data[1] = [troop_codes[troop.name] if (i == 0) else opp_data[1][i-1] for i in range(4)]
            opp_data[2] -= troop_elixirs[troop.name]
    
    opp_data[3] = arena_data['OppTroops'][-1].uid if arena_data['OppTroops'] else 0
    
    curr_cards = [troop_names[troop] for troop in opp_data[0] if (troop not in opp_data[1] and troop != '')] + ([''] * (4 - len([troop_names[troop] for troop in opp_data[0] if (troop not in opp_data[1] and troop != '')])))
    
    if(arena_data['MyTower'].game_timer % (20 - (10 * (arena_data['MyTower'].game_timer > 1200))) == 0):
        opp_data[2] = min(opp_data[2] + 1, 10)
    
    my_elixir = arena_data['MyTower'].total_elixir
    memory['elixir_advantage'] = my_elixir - opp_data[2]
    
    if arena_data['MyTower'].game_timer > 1800:
        memory['strategy'] = 'aggressive'
    elif my_elixir > 8 and memory['elixir_advantage'] > 2:
        memory['strategy'] = 'push'
    elif len(arena_data['OppTroops']) > 3:
        memory['strategy'] = 'defensive'
    else:
        memory['strategy'] = 'adaptive'
    
    opp_data[4] = memory
    return str(opp_data), curr_cards

def get_counter_matrix():
    return np.array([
        [ 0, 1, -1, 0, 0, -1, -1, 0, 0, 0, 1, -1],
        [-1, 0, 1, 1, -1, 1, -1, 1, 1, 0, 1, -1],
        [ 1, -1, 0, -1, 0, 0, 0, 0, 0, -1, 0, 0],
        [ 0, -1, 1, 0, -1, -1, 0, 1, 1, 0, 0, -1],
        [ 1, 1, 0, 1, 0, 1, -1, 0, 0, 1, 1, 0],
        [ 1, -1, 0, 1, -1, 0, 0, 0, -1, 1, 0, 1],
        [ 1, 1, 0, 0, 1, 0, 0, 0, -1, 0, 1, 0],
        [ 0, -1, -1, -1, 0, 0, -1, 0, -1, -1, -1, 0],
        [ 1, -1, 1, -1, 0, 0, 1, 1, 0, -1, 0, 0],
        [ 0, 0, 1, 0, -1, -1, 0, 1, 1, 0, 0, -1],
        [ 0, -1, 0, 0, -1, 0, -1, 0, 0, 0, 0, -1],
        [ 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0]
    ])

def calculate_optimal_position(arena_data, troop_name):
    memory = eval(team_signal)[4]
    strategy = memory['strategy']
    
    if strategy == 'defensive' or len(arena_data['OppTroops']) > 2:
        if arena_data['OppTroops']:
            closest_enemy = min(arena_data['OppTroops'], key=lambda t: abs(t.position[0]) + abs(t.position[1]))
            return (min(closest_enemy.position[0] + 2, -5), closest_enemy.position[1])
        return (-10, 0)
    
    if troop_name == "Giant" and arena_data['MyTower'].total_elixir >= 7:
        return (-5, 0)
    
    my_tanks = [t for t in arena_data['MyTroops'] if t.name in ["Giant", "Valkyrie"]]
    if my_tanks and troop_name in ["Wizard", "Musketeer", "Archer"]:
        tank = my_tanks[0]
        return (tank.position[0] - 2, tank.position[1])
    
    if strategy == 'aggressive' or strategy == 'push':
        left_troops = len([t for t in arena_data['MyTroops'] if t.position[1] < 0])
        right_troops = len([t for t in arena_data['MyTroops'] if t.position[1] > 0])
        if left_troops > right_troops:
            return (15, 10)
        elif right_troops > left_troops:
            return (-15, 10)
        else:
            if troop_name in ["Giant", "Valkyrie", "Dragon"]:
                return (+15, 0)
            else:
                return (-15, 0)
    
    if troop_name in ["Giant", "Balloon"]:
        return (-8, 0)
    elif troop_name in ["Wizard", "Musketeer"]:
        return (-12, 3)
    elif troop_name in ["Skeleton"]:
        return (-10, 0)
    else:
        return (-8, 2)

def select_best_troop(arena_data, curr_cards, counter_matrix):
    memory = eval(team_signal)[4]
    strategy = memory['strategy']
    all_troops = ["Archer", "Minion", "Knight", "Skeleton", "Dragon", "Valkyrie", "Musketeer", "Giant", "Prince", "Barbarian", "Balloon", "Wizard"]
    troop_counts = [2, 3, 1, 10, 1, 1, 1, 1, 1, 3, 1, 1]
    
    opp_troops = np.zeros(12)
    for troop in arena_data['OppTroops']:
        opp_troops[all_troops.index(troop.name)] += 1/troop_counts[all_troops.index(troop.name)]
    
    troop_scores = counter_matrix @ opp_troops
    
    deployable_troops = arena_data['MyTower'].deployable_troops
    deployable_troop_scores = []
    for i, troop in enumerate(deployable_troops):
        base_score = troop_scores[all_troops.index(troop)]
        
        if strategy == 'defensive':
            if troop in ["Valkyrie", "Wizard", "Skeleton"]:
                base_score += 2
        elif strategy == 'push' or strategy == 'aggressive':
            if troop in ["Giant", "Balloon", "Dragon"]:
                base_score += 2
        elif strategy == 'adaptive':
            if memory['elixir_advantage'] > 2 and troop in ["Giant", "Wizard", "Minion"]:
                base_score += 1
        
        if arena_data['MyTower'].total_elixir < 6 and troop in ["Giant", "Balloon", "Minion", "Wizard"]:
            base_score -= 1
        
        deployable_troop_scores.append(base_score)
    
    return deployable_troop_scores.index(max(deployable_troop_scores))

def quick_defense_check(arena_data):
    enemy_troops_count = len(arena_data['OppTroops'])
    my_elixir = arena_data['MyTower'].total_elixir
    if enemy_troops_count > 0 and my_elixir >= 3:
        closest_enemy = min(arena_data['OppTroops'], key=lambda t: t.position[1])
        if closest_enemy.position[1] < 30:
            best_counter = get_quick_counter(closest_enemy.name)
            deploy_list.list_.append((best_counter, (-10, closest_enemy.position[1])))
            return True
    return False

def get_quick_counter(enemy_troop):
    counters = {
        "Giant": Troops.skeleton,
        "Balloon": Troops.archer,
        "Prince": Troops.skeleton,
        "Wizard": Troops.valkyrie,
        "Dragon": Troops.archer
    }
    return counters.get(enemy_troop, Troops.archer)

def defend_bridge_spam(arena_data):
    bridge_troops = [t for t in arena_data['OppTroops'] if 40 < t.position[1] < 60]
    if bridge_troops and arena_data['MyTower'].total_elixir >= 4:
        splash_troops = [Troops.valkyrie, Troops.wizard]
        for troop in splash_troops:
            if troop in arena_data['MyTower'].deployable_troops:
                deploy_list.list_.append((troop, (-15, 45)))
                return True
    return False

def logic(arena_data: dict):
    global team_signal
    team_signal, curr_cards = update_signal(team_signal, arena_data)
    memory = eval(team_signal)[4]
    
    counter_matrix = get_counter_matrix()
    my_elixir = arena_data['MyTower'].total_elixir
    opp_elixir = eval(team_signal)[2]
    
    if quick_defense_check(arena_data):
        return
    
    if defend_bridge_spam(arena_data):
        return
    
    should_deploy = False
    if len(arena_data['OppTroops']) > 0 and my_elixir >= 3:
        should_deploy = True
        memory['defending'] = True
    elif my_elixir >= 8:
        should_deploy = True
        memory['defending'] = False
    elif my_elixir - opp_elixir >= 3:
        should_deploy = True
        memory['defending'] = False
    elif arena_data['MyTower'].game_timer > 1800:
        if my_elixir >= 5:
            should_deploy = True
            memory['defending'] = False
    elif memory['strategy'] == 'aggressive' and my_elixir >= 6:
        should_deploy = True
        memory['defending'] = False
    
    if should_deploy:
        best_troop_idx = select_best_troop(arena_data, curr_cards, counter_matrix)
        best_troop = arena_data['MyTower'].deployable_troops[best_troop_idx]
        optimal_position = calculate_optimal_position(arena_data, best_troop)
        deploy_list.list_.append((best_troop, optimal_position))
        
        if not memory['defending'] and my_elixir >= 7:
            deployable_troops = arena_data['MyTower'].deployable_troops
            troop_scores = []
            for i, troop in enumerate(deployable_troops):
                if i != best_troop_idx:
                    if (best_troop == "Giant" and troop in ["Wizard", "Musketeer"]) or \
                       (best_troop == "Valkyrie" and troop in ["Archer", "Musketeer"]):
                        score = 5
                    else:
                        score = 2
                    troop_scores.append((i, score))
                else:
                    troop_scores.append((i, -10))
            
            second_best_idx = max(troop_scores, key=lambda x: x[1])[0]
            second_troop = arena_data['MyTower'].deployable_troops[second_best_idx]
            
            if best_troop in ["Giant", "Valkyrie"]:
                second_position = (optimal_position[0] - 2, optimal_position[1] - 5)
            else:
                second_position = (optimal_position[0], optimal_position[1] - 3)
            
            deploy_list.list_.append((second_troop, second_position))
    
    signal_data = eval(team_signal)
    signal_data[4] = memory
    team_signal = str(signal_data)
