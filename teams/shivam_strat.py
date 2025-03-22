from teams.helper_function import Troops, Utils
import numpy as np

team_name = "TowerTactics"
troops = [Troops.wizard, Troops.minion, Troops.archer, Troops.valkyrie, Troops.dragon, Troops.skeleton, Troops.giant, Troops.musketeer]
deploy_list = Troops([])
team_signal = "[['', '', '', '', '', '', '', ''], ['', '', '', ''], 10, 0, {'elixir_advantage': 0, 'last_push_time': 0, 'strategy': 'adaptive', 'defending': False}]"

def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def update_signal(team_signal, arena_data):
    troop_names = {'A': 'Archer', 'm': 'Minion', 'K': 'Knight', 'S': 'Skeleton', 'D': 'Dragon', 'V': 'Valkyrie', 'M': 'Musketeer', 'G': 'Giant', 'P': 'Prince', 'b': 'Barbarian', 'B': 'Balloon', 'W': 'Wizard', '': ''}
    troop_codes = {t: c for (c, t) in troop_names.items()}
    troop_elixirs = {"Archer": 3, "Minion": 5, "Knight": 3, "Skeleton": 3, "Dragon": 4, "Valkyrie": 4, "Musketeer": 4, "Giant": 5, "Prince": 5, "Barbarian": 3, "Balloon": 5, "Wizard": 5}
    
    opp_data = eval(team_signal)
    memory = opp_data[4]  # Get our strategy memory
    
    # Track opponent troops
    for troop in arena_data['OppTroops']:
        if troop_codes[troop.name] not in opp_data[0]:
            for i in range(8):
                if opp_data[0][i] == '':
                    opp_data[0][i] = troop_codes[troop.name]
                    break       
        if (troop.uid > opp_data[3]) and (troop_codes[troop.name] not in opp_data[1]):
            opp_data[1] = [troop_codes[troop.name] if (i == 0) else opp_data[1][i-1] for i in range(4)]
            opp_data[2] -= troop_elixirs[troop.name]
    
    # Update opponent's last troop UID
    opp_data[3] = arena_data['OppTroops'][-1].uid if arena_data['OppTroops'] else 0
    
    # Calculate current cards
    curr_cards = [troop_names[troop] for troop in opp_data[0] if (troop not in opp_data[1] and troop != '')] + ([''] * (4 - len([troop_names[troop] for troop in opp_data[0] if (troop not in opp_data[1] and troop != '')])))
    
    # Update opponent's elixir (with the game timer-based regen)
    if(arena_data['MyTower'].game_timer % (20 - (10 * (arena_data['MyTower'].game_timer > 1200))) == 0):
        opp_data[2] = min(opp_data[2] + 1, 10)
    
    # Update our strategy memory
    my_elixir = arena_data['MyTower'].elixir
    memory['elixir_advantage'] = my_elixir - opp_data[2]
    
    # Adjust strategy based on game state
    if arena_data['MyTower'].game_timer > 1800:  # Last minute (double elixir)
        memory['strategy'] = 'aggressive'
    elif my_elixir > 8 and memory['elixir_advantage'] > 2:
        memory['strategy'] = 'push'
    elif len(arena_data['OppTroops']) > 3:
        memory['strategy'] = 'defensive'
    else:
        memory['strategy'] = 'adaptive'
        
    # Update memory in the team signal
    opp_data[4] = memory
    
    return str(opp_data), curr_cards

def get_counter_matrix():
    """
    Returns the counter matrix with scores for troop matchups.
    Positive numbers mean the row troop counters the column troop.
    Higher values mean stronger counters.
    """
    return np.array([
    #  Arch  Min  Knig Skel Drag Valk Musk Gian Prin Barb Ball Wiz  (Defending Troops)
    [  0,    1,  -1,   0,   0,  -1,  -1,   0,   0,   0,   1,  -1],  # Archer (Attacking)
    [ -1,    0,   1,   1,  -1,   1,  -1,   1,   1,   0,   1,  -1],  # Minion
    [  1,   -1,   0,  -1,   0,   0,   0,   0,   0,  -1,   0,   0],  # Knight
    [  0,   -1,   1,   0,  -1,  -1,   0,   1,   1,   0,   0,  -1],  # Skeleton
    [  1,    1,   0,   1,   0,   1,  -1,   0,   0,   1,   1,   0],  # Dragon
    [  1,   -1,   0,   1,  -1,   0,   0,   0,  -1,   1,   0,   1],  # Valkyrie
    [  1,    1,   0,   0,   1,   0,   0,   0,  -1,   0,   1,   0],  # Musketeer
    [  0,   -1,  -1,  -1,   0,   0,  -1,   0,  -1,  -1,  -1,   0],  # Giant
    [  1,   -1,   1,  -1,   0,   0,   1,   1,   0,  -1,   0,   0],  # Prince
    [  0,    0,   1,   0,  -1,  -1,   0,   1,   1,   0,   0,  -1],  # Barbarian
    [  0,   -1,   0,   0,  -1,   0,  -1,   0,   0,   0,   0,  -1],  # Balloon
    [  1,    1,   0,   1,   0,   0,   0,   1,   0,   1,   1,   0]   # Wizard
    ])

def calculate_optimal_position(arena_data, troop_name):
    """
    Calculate the optimal position to deploy a troop based on the current game state.
    Returns (x, y) coordinates.
    """
    memory = eval(team_signal)[4]
    strategy = memory['strategy']
    
    # Defensive positioning (close to our tower)
    if strategy == 'defensive' or len(arena_data['OppTroops']) > 2:
        # Find the closest enemy troop to our tower
        if arena_data['OppTroops']:
            closest_enemy = min(arena_data['OppTroops'], key=lambda t: abs(t.position[0]) + abs(t.position[1]))
            # Deploy slightly ahead of our tower towards the enemy
            return (min(closest_enemy.position[0] + 2, -5), closest_enemy.position[1])
        return (-10, 0)  # Default defensive position
    
    # Tank-based pushes
    if troop_name == "Giant" and arena_data['MyTower'].elixir >= 7:
        # Launch giant directly down the middle lane
        return (-5, 0)
    
    # Support troops behind tanks
    my_tanks = [t for t in arena_data['MyTroops'] if t.name in ["Giant", "Valkyrie"]]
    if my_tanks and troop_name in ["Wizard", "Musketeer", "Archer"]:
        tank = my_tanks[0]
        # Position ranged units behind the tank
        return (tank.position[0] - 2, tank.position[1])
    
    # Aggressive positioning (close to enemy tower)
    if strategy == 'aggressive' or strategy == 'push':
        # Focus on one lane (left or right) based on existing troop concentration
        left_troops = len([t for t in arena_data['MyTroops'] if t.position[1] < 0])
        right_troops = len([t for t in arena_data['MyTroops'] if t.position[1] > 0])
        
        if left_troops > right_troops:
            return (-5, -5)  # Left lane push
        elif right_troops > left_troops:
            return (-5, 5)   # Right lane push
        else:
            # If equal, choose based on troop type
            if troop_name in ["Giant", "Valkyrie", "Dragon"]:
                return (-5, -5)  # Tanks go left
            else:
                return (-5, 5)   # Support goes right (split lane pressure)
    
    # Default: adaptive positioning based on troop type
    if troop_name in ["Giant", "Balloon"]:
        return (-8, 0)  # Tanks down the middle
    elif troop_name in ["Wizard", "Musketeer"]:
        return (-12, 3)  # Ranged support slightly back
    elif troop_name in ["Skeleton"]:
        return (-10, -3)  # Swarm units to distract
    else:
        return (-8, 2)  # Default position

def select_best_troop(arena_data, curr_cards, counter_matrix):
    """
    Select the best troop to deploy based on current game state and counters.
    Returns the index of the best deployable troop.
    """
    memory = eval(team_signal)[4]
    strategy = memory['strategy']
    all_troops = ["Archer", "Minion", "Knight", "Skeleton", "Dragon", "Valkyrie", "Musketeer", "Giant", "Prince", "Barbarian", "Balloon", "Wizard"]
    troop_counts = [2, 3, 1, 10, 1, 1, 1, 1, 1, 3, 1, 1]
    
    # Calculate how many of each enemy troop type is present (normalized by their count)
    opp_troops = np.zeros(12)
    for troop in arena_data['OppTroops']:
        opp_troops[all_troops.index(troop.name)] += 1/troop_counts[all_troops.index(troop.name)]
    
    # Calculate counter scores for all troops
    troop_scores = counter_matrix @ opp_troops
    
    # Get scores for our deployable troops
    deployable_troops = arena_data['MyTower'].deployable_troops
    deployable_troop_scores = []
    
    for i, troop in enumerate(deployable_troops):
        base_score = troop_scores[all_troops.index(troop)]
        
        # Apply strategy modifiers
        if strategy == 'defensive':
            # Boost defensive troops when on defense
            if troop in ["Valkyrie", "Wizard", "Skeleton"]:
                base_score += 2
        elif strategy == 'push' or strategy == 'aggressive':
            # Boost offensive troops when pushing
            if troop in ["Giant", "Balloon", "Dragon"]:
                base_score += 2
        elif strategy == 'adaptive':
            # Balanced approach
            if memory['elixir_advantage'] > 2 and troop in ["Giant", "Wizard", "Minion"]:
                base_score += 1
        
        # Consider current elixir - avoid deploying expensive troops when low on elixir
        if arena_data['MyTower'].elixir < 6 and troop in ["Giant", "Balloon", "Minion", "Wizard"]:
            base_score -= 1
        
        deployable_troop_scores.append(base_score)
    
    # Return the index of the troop with the highest score
    return deployable_troop_scores.index(max(deployable_troop_scores))

def logic(arena_data: dict):
    global team_signal
    team_signal, curr_cards = update_signal(team_signal, arena_data)
    memory = eval(team_signal)[4]
    
    # Get counter matrix
    counter_matrix = get_counter_matrix()
    
    # Get current game state info
    my_elixir = arena_data['MyTower'].elixir
    opp_elixir = eval(team_signal)[2]
    enemy_troops_count = len(arena_data['OppTroops'])
    my_troops_count = len(arena_data['MyTroops'])
    
    # Decision making based on game state
    should_deploy = False
    
    if enemy_troops_count > 0 and my_elixir >= 3:
        # Defensive deployment - respond to enemy troops
        should_deploy = True
        memory['defending'] = True
    elif my_elixir >= 8:
        # Built up enough elixir for a strong push
        should_deploy = True
        memory['defending'] = False
    elif my_elixir - opp_elixir >= 3:
        # We have an elixir advantage, apply pressure
        should_deploy = True
        memory['defending'] = False
    elif arena_data['MyTower'].game_timer > 1800:
        # Last minute - more aggressive
        if my_elixir >= 5:
            should_deploy = True
            memory['defending'] = False
    elif memory['strategy'] == 'aggressive' and my_elixir >= 6:
        should_deploy = True
        memory['defending'] = False
    
    # If we should deploy, select the best troop
    if should_deploy:
        best_troop_idx = select_best_troop(arena_data, curr_cards, counter_matrix)
        best_troop = arena_data['MyTower'].deployable_troops[best_troop_idx]
        optimal_position = calculate_optimal_position(arena_data, best_troop)
        
        # Add to deploy list
        deploy_list.list_.append((best_troop, optimal_position))
        
        # If we're pushing and have enough elixir, deploy a second troop for support
        if not memory['defending'] and my_elixir >= 7:
            # Calculate scores again excluding the first choice
            deployable_troops = arena_data['MyTower'].deployable_troops
            troop_scores = []
            
            for i, troop in enumerate(deployable_troops):
                if i != best_troop_idx:  # Skip the already selected troop
                    # For support troops, prefer combinations that work well together
                    if (best_troop == "Giant" and troop in ["Wizard", "Musketeer"]) or \
                       (best_troop == "Valkyrie" and troop in ["Archer", "Musketeer"]):
                        score = 5  # Good combo
                    else:
                        score = 2  # Default score
                    troop_scores.append((i, score))
                else:
                    troop_scores.append((i, -10))  # Very low score to avoid selecting again
            
            # Find second best troop
            second_best_idx = max(troop_scores, key=lambda x: x[1])[0]
            second_troop = arena_data['MyTower'].deployable_troops[second_best_idx]
            
            # Position the second troop appropriately (slightly offset from the first)
            if best_troop in ["Giant", "Valkyrie"]:
                # Position support troops behind tanks
                second_position = (optimal_position[0] - 2, optimal_position[1] + 1)
            else:
                # Position alongside
                second_position = (optimal_position[0], optimal_position[1] + 3)
            
            deploy_list.list_.append((second_troop, second_position))
    
    # Update memory in team_signal
    signal_data = eval(team_signal)
    signal_data[4] = memory
    team_signal = str(signal_data)