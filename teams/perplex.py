from teams.helper_function import Troops, Utils
import numpy as np
import math

team_name = "perplex"
troops = [Troops.wizard, Troops.minion, Troops.archer, Troops.valkyrie, Troops.dragon, Troops.skeleton, Troops.giant, Troops.musketeer]
deploy_list = Troops([])
team_signal = "[['', '', '', '', '', '', '', ''], ['', '', '', ''], 10, 0, ['']]"

def deploy(arena_data:dict):
    """
    DON'T TEMPER DEPLOY FUCNTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def update_signal(team_signal, arena_data):
    troop_names = {'A': 'Archer', 'm': 'Minion', 'K': 'Knight', 'S': 'Skeleton', 'D': 'Dragon', 'V': 'Valkyrie', 'M': 'Musketeer', 'G': 'Giant', 'P': 'Prince', 'b': 'Barbarian', 'B': 'Balloon', 'W': 'Wizard', '': ''}
    troop_codes = {c: t for (t, c) in troop_names.items()}
    troop_elixirs = {"Archer": 3, "Minion": 3, "Knight": 3, "Skeleton": 3, "Dragon": 4, "Valkyrie": 4, "Musketeer": 4, "Giant": 5, "Prince": 5, "Barbarian": 3, "Balloon": 5, "Wizard": 5}
    opp_data = eval(team_signal)
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
        opp_data[2] = opp_data[2] + (opp_data[2] < 10)
    return str(opp_data), curr_cards

def get_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def determine_range_index(distance, attack_range):
    """Determine which range index to use based on distance and troop's attack range"""
    if attack_range == 0:  # Melee troops always use short range
        return 0
    
    if distance <= attack_range:  # Short range: within attack range
        return 0
    elif distance <= attack_range * 2:  # Medium range: within 2x attack range
        return 1
    else:  # Long range: beyond 2x attack range
        return 2

def get_troop_stats():
    """Get stats for all troops from the image data"""
    stats = {
        "Archer": {"attack_range": 5, "splash": 0, "targets": ["Air", "Ground", "Building"], "health": 334, "damage": 118, "velocity": "Medium", "elixir": 3},
        "Minion": {"attack_range": 2, "splash": 0, "targets": ["Air", "Ground", "Building"], "health": 252, "damage": 129, "velocity": "Fast", "elixir": 3},
        "Knight": {"attack_range": 0, "splash": 0, "targets": ["Ground", "Building"], "health": 1938, "damage": 221, "velocity": "Medium", "elixir": 3},
        "Skeleton": {"attack_range": 0, "splash": 0, "targets": ["Ground", "Building"], "health": 89, "damage": 89, "velocity": "Fast", "elixir": 3},
        "Dragon": {"attack_range": 3.5, "splash": 1, "targets": ["Air", "Ground", "Building"], "health": 1267, "damage": 176, "velocity": "Fast", "elixir": 4},
        "Valkyrie": {"attack_range": 0, "splash": 1, "targets": ["Ground", "Building"], "health": 2097, "damage": 195, "velocity": "Medium", "elixir": 4},
        "Musketeer": {"attack_range": 6, "splash": 0, "targets": ["Air", "Ground", "Building"], "health": 792, "damage": 239, "velocity": "Medium", "elixir": 4},
        "Giant": {"attack_range": 0, "splash": 0, "targets": ["Building"], "health": 5423, "damage": 337, "velocity": "Slow", "elixir": 5},
        "Prince": {"attack_range": 0, "splash": 0, "targets": ["Ground", "Building"], "health": 1920, "damage": 392, "velocity": "Fast", "elixir": 5},
        "Barbarian": {"attack_range": 0, "splash": 0, "targets": ["Ground", "Building"], "health": 736, "damage": 161, "velocity": "Medium", "elixir": 3},
        "Balloon": {"attack_range": 0, "splash": 1, "targets": ["Building"], "health": 2226, "damage": 424, "velocity": "Medium", "elixir": 5},
        "Wizard": {"attack_range": 5.5, "splash": 1, "targets": ["Air", "Ground", "Building"], "health": 1100, "damage": 410, "velocity": "Medium", "elixir": 5},
    }
    return stats

def logic(arena_data:dict):
    global team_signal
    team_signal, curr_cards = update_signal(team_signal, arena_data)
    stored_data = eval(team_signal)[4]
    
    # Define 3D counters matrix
    counters_3d = np.array([
        # Arch  Min  Knig Skel Drag Valk Musk Gian Prin Barb Ball Wiz  (Defending Troops)
        [[-1, 1, 2], [0, 1, 2], [-2, -1, 0], [0, 1, 2], [-2, -1, 0], [-2, -1, 0], [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], [0, 1, 2], [1, 2, 3], [-1, 0, 1]],  # Archer (Attacking)
        [[-2, -1, 0], [0, 1, 2], [1, 2, 3], [1, 2, 3], [-1, 0, 1], [1, 2, 3], [-1, 0, 1], [1, 2, 3], [1, 2, 3], [0, 1, 2], [1, 2, 3], [-1, 0, 1]],  # Minion
        [[1, 2, 3], [-1, 0, 1], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [0, 1, 2]],  # Knight
        [[0, 1, 2], [-1, 0, 1], [1, 2, 3], [0, 1, 2], [-2, -1, 0], [-1, 0, 1], [0, 1, 2], [1, 2, 3], [1, 2, 3], [0, 1, 2], [0, 1, 2], [-1, 0, 1]],  # Skeleton
        [[1, 2, 3], [1, 2, 3], [0, 1, 2], [1, 2, 3], [0, 1, 2], [1, 2, 3], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [1, 2, 3], [1, 2, 3], [0, 1, 2]],  # Dragon
        [[1, 2, 3], [-1, 0, 1], [0, 1, 2], [1, 2, 3], [-2, -1, 0], [0, 1, 2], [0, 1, 2], [-1, 0, 1], [-1, 0, 1], [1, 2, 3], [0, 1, 2], [1, 2, 3]],  # Valkyrie
        [[1, 2, 3], [1, 2, 3], [0, 1, 2], [0, 1, 2], [1, 2, 3], [0, 1, 2], [0, 1, 2], [-1, 0, 1], [-1, 0, 1], [0, 1, 2], [1, 2, 3], [0, 1, 2]],  # Musketeer
        [[-1, 0, 1], [-1, 0, 1], [-2, -1, 0], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], [0, 1, 2]],  # Giant
        [[1, 2, 3], [-1, 0, 1], [1, 2, 3], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [1, 2, 3], [1, 2, 3], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [0, 1, 2]],  # Prince
        [[0, 1, 2], [0, 1, 2], [1, 2, 3], [0, 1, 2], [-1, 0, 1], [-1, 0, 1], [0, 1, 2], [1, 2, 3], [1, 2, 3], [0, 1, 2], [0, 1, 2], [-1, 0, 1]],  # Barbarian
        [[0, 1, 2], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [-2, -1, 0], [0, 1, 2], [-1, 0, 1], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [-1, 0, 1]],  # Balloon
        [[1, 2, 3], [1, 2, 3], [0, 1, 2], [1, 2, 3], [0, 1, 2], [0, 1, 2], [0, 1, 2], [1, 2, 3], [0, 1, 2], [1, 2, 3], [1, 2, 3], [0, 1, 2]]   # Wizard
    ])

    all_troops = ["Archer", "Minion", "Knight", "Skeleton", "Dragon", "Valkyrie", "Musketeer", "Giant", "Prince", "Barbarian", "Balloon", "Wizard"]
    troop_counts = [2, 3, 1, 10, 1, 1, 1, 1, 1, 3, 1, 1]
    troop_stats = get_troop_stats()
    
    # Define grid of possible deployment positions
    grid_x = list(range(-25, 26, 5))  # X coordinates from -25 to 25 with step 5
    grid_y = list(range(0, 51, 5))    # Y coordinates from 0 to 50 with step 5
    
    # Get details of opponent troops
    opp_troops_details = []
    for troop in arena_data['OppTroops']:
        opp_troops_details.append({
            'name': troop.name,
            'position': (troop.position[0], troop.position[1]),
            'index': all_troops.index(troop.name),
            'health': troop.health
        })
    
    # Best positions for each deployable troop
    best_positions = {}
    
    # Current elixir
    current_elixir = arena_data['MyTower'].total_elixir
    
    # Check deployable troops
    for deployable_troop in arena_data['MyTower'].deployable_troops:
        attacking_idx = all_troops.index(deployable_troop)
        stats = troop_stats[deployable_troop]
        attack_range = stats["attack_range"]
        splash = stats["splash"]
        targets = stats["targets"]
        elixir_cost = stats["elixir"]
        
        # Skip if not enough elixir
        if elixir_cost > current_elixir:
            continue
        
        best_score = -float('inf')
        best_position = (0, 0)
        
        # Check each position in the grid
        for x in grid_x:
            for y in grid_y:
                position_score = 0
                
                # Check if there are opponent troops that this troop can counter
                for opp_troop in opp_troops_details:
                    opp_name = opp_troop['name']
                    opp_idx = opp_troop['index']
                    opp_stats = troop_stats[opp_name]
                    opp_position = opp_troop['position']
                    
                    # Check if the troop can target this opponent (air/ground)
                    can_target = True
                    if "Air" in opp_stats["targets"] and "Air" not in targets:
                        can_target = False
                    
                    if can_target:
                        distance = get_distance((x, y), opp_position)
                        
                        # Determine range index based on distance and attack range
                        range_idx = determine_range_index(distance, attack_range)
                        
                        # Get advantage score for this matchup at this range
                        advantage = counters_3d[attacking_idx][opp_idx][range_idx]
                        
                        # Calculate effectiveness score
                        health_weight = opp_troop['health'] / 1000  # Normalize health
                        
                        # Splash damage bonus against grouped enemies
                        splash_bonus = 1.0
                        if splash > 0:
                            # Check if there are multiple enemies nearby
                            nearby_count = 0
                            for other_troop in opp_troops_details:
                                if get_distance(opp_position, other_troop['position']) < splash + 3:
                                    nearby_count += 1
                            splash_bonus = 1.0 + (nearby_count * 0.25)  # 25% bonus per nearby enemy
                        
                        # Distance penalty (prefer closer engagements for better reaction time)
                        distance_penalty = max(0.5, 1.0 - (distance / 50))
                        
                        # Add to position score
                        position_score += advantage * health_weight * splash_bonus * distance_penalty
                
                # Defensive positioning (prefer positions that protect your tower)
                tower_distance = get_distance((x, y), (0, 0))
                if tower_distance < 10:  # Too close to tower
                    defensive_bonus = 0.7  # Penalty for being too close (crowding)
                elif tower_distance > 40:  # Too far from tower
                    defensive_bonus = 0.8  # Penalty for being too far (vulnerable)
                else:
                    defensive_bonus = 1.0  # Optimal defensive distance
                
                position_score *= defensive_bonus
                
                # Update best position if this position has a higher score
                if position_score > best_score:
                    best_score = position_score
                    best_position = (x, y)
        
        # Factor in elixir cost for final score (elixir efficiency)
        elixir_efficiency = best_score / elixir_cost
        best_positions[deployable_troop] = (best_position, elixir_efficiency)
    
    # Sort deployable troops by their elixir-adjusted scores
    sorted_troops = sorted(best_positions.items(), key=lambda x: x[1][1], reverse=True)
    
    # Deploy troops at their optimal positions, considering elixir constraints
    remaining_elixir = current_elixir
    
    for troop, (position, _) in sorted_troops:
        elixir_cost = troop_stats[troop]["elixir"]
        if elixir_cost <= remaining_elixir:
            deploy_list.list_.append((troop, position))
            remaining_elixir -= elixir_cost
    
    team_signal = str(eval(team_signal)[:4] + [stored_data])
