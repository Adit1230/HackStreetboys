from teams.helper_function import Troops, Utils
import numpy as np
import math

team_name = "ConstAggression,12p"
troops = [Troops.wizard, Troops.minion, Troops.archer, Troops.valkyrie, Troops.dragon, Troops.skeleton, Troops.knight, Troops.musketeer]
deploy_list = Troops([])
team_signal = "[['', '', '', '', '', '', '', ''], ['', '', '', ''], 10, 0, ['']]"

def can_launch_push(arena_data):
    """Check if we can launch a push based on elixir advantage and enemy state"""
    my_elixir = arena_data["MyTower"].total_elixir
    # More aggressive push conditions - push whenever we have enough elixir
    return my_elixir >= 6  # Reduced from 8 to 6 to push more frequently

def deploy_push_combination(tank, support1, support2=None, arena_data=None):
    """Deploy a tank-based push combination"""
    # Choose attack lane based on existing troops
    existing_troops = arena_data["MyTroops"]
    if existing_troops:
        # If we have existing troops, reinforce their lane
        lane_x = existing_troops[0].position[0]
        attack_x = lane_x
    else:
        # Otherwise choose a random lane
        lane = np.random.choice(["left", "center", "right"])
        attack_x = -10 if lane == "left" else (10 if lane == "right" else 0)
    
    # Deploy troops closer together for more aggressive pushes
    deploy_list.list_.append((tank, (attack_x, 50)))
    deploy_list.list_.append((support1, (attack_x, 48)))  # Closer spacing
    if support2:
        deploy_list.list_.append((support2, (attack_x, 46)))

def update_signal(team_signal, arena_data):
    troop_names = {'A' : 'Archer', 'm' : 'Minion', 'K' : 'Knight', 'S' : 'Skeleton', 'D' : 'Dragon', 'V' : 'Valkyrie', 'M' : 'Musketeer', 'G' : 'Giant', 'P' : 'Prince', 'b' : 'Barbarian', 'B' : 'Balloon', 'W' : 'Wizard', '' : ''}
    troop_codes = {c : t for (t, c) in troop_names.items()}
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

def deploy(arena_data: dict):
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def logic(arena_data: dict):
    global team_signal
    # Update team signal and get current cards
    team_signal, curr_cards = update_signal(team_signal, arena_data)
    stored_data = eval(team_signal)[4]
    factor = 1.875
    # Get enemy elixir from team signal
    enemy_elixir = eval(team_signal)[2]
    
    # Merged dictionary for troop properties (updated with new data)
    TROOP_PROPERTIES = {
        "Archer": {"attack_range": 5, "discovery_range": 8, "is_splash": False, "can_attack_air": True, "damage": 118, "health": 324, "elixir": 3},
        "Minion": {"attack_range": 2, "discovery_range": 4, "is_splash": False, "can_attack_air": True, "damage": 129, "health": 252, "elixir": 3},
        "Knight": {"attack_range": 0, "discovery_range": 7, "is_splash": False, "can_attack_air": False, "damage": 221, "health": 1938, "elixir": 3},
        "Skeleton": {"attack_range": 0, "discovery_range": 4, "is_splash": False, "can_attack_air": False, "damage": 89, "health": 89, "elixir": 3},
        "Dragon": {"attack_range": 3.5, "discovery_range": 5, "is_splash": True, "can_attack_air": True, "damage": 176, "health": 1267, "elixir": 4},
        "Valkyrie": {"attack_range": 0, "discovery_range": 7, "is_splash": True, "can_attack_air": False, "damage": 195, "health": 2097, "elixir": 4},
        "Musketeer": {"attack_range": 6, "discovery_range": 8, "is_splash": False, "can_attack_air": True, "damage": 239, "health": 792, "elixir": 4},
        "Giant": {"attack_range": 0, "discovery_range": 7, "is_splash": False, "can_attack_air": False, "damage": 337, "health": 5423, "elixir": 5},
        "Prince": {"attack_range": 0, "discovery_range": 5, "is_splash": False, "can_attack_air": False, "damage": 392, "health": 1920, "elixir": 5},
        "Barbarian": {"attack_range": 0, "discovery_range": 5, "is_splash": False, "can_attack_air": False, "damage": 161, "health": 736, "elixir": 3},
        "Balloon": {"attack_range": 0, "discovery_range": 5, "is_splash": True, "can_attack_air": False, "damage": 424, "health": 2226, "elixir": 5},
        "Wizard": {"attack_range": 5.5, "discovery_range": 8, "is_splash": True, "can_attack_air": True, "damage": 410, "health": 1100, "elixir": 5},
    }

    # Define powerful push combinations using only available troops
    PUSH_COMBINATIONS = [
        # (tank, support1, support2, min_elixir_needed)
        ("Knight", "Wizard", "Dragon", 10),     # Knight + Wizard + Dragon
        ("Knight", "Wizard", "Archer", 9),      # Knight + Wizard + Archer
        ("Knight", "Dragon", "Archer", 9),      # Knight + Dragon + Archer
        ("Knight", "Wizard", None, 8),          # Knight + Wizard
        ("Knight", "Dragon", None, 7),          # Knight + Dragon
        ("Valkyrie", "Wizard", "Dragon", 10),   # Valkyrie + Wizard + Dragon
        ("Valkyrie", "Wizard", "Archer", 9),    # Valkyrie + Wizard + Archer
        ("Valkyrie", "Dragon", "Archer", 9),    # Valkyrie + Dragon + Archer
        ("Valkyrie", "Wizard", None, 9),        # Valkyrie + Wizard
        ("Valkyrie", "Dragon", None, 8)         # Valkyrie + Dragon
    ]

    counters = np.array([
    # Archer    Balloon    Barbarian  Dragon     Giant      Knight     Minion     Musketeer  Prince     Skeleton   Valkyrie   Wizard     (Defending)
    [ 0.000,     0.105,    -0.045,    -0.208,    0.043,     -0.023,    -0.098,     0.117,    -0.140,    -0.174,    -0.084,    -0.812],  # Archer
    [-0.105,     0.000,     0.000,    -0.077,    0.000,      0.000,    -0.167,    -0.050,     0.000,     0.000,     0.000,    -0.167],  # Balloon
    [ 0.045,     0.000,     0.000,    -0.200,    0.044,      0.032,    -0.167,     0.100,    -0.042,    -0.220,    -0.143,    -0.377],  # Barbarian
    [ 0.208,     0.077,     0.200,     0.000,    0.032,      0.083,     0.243,     0.085,     0.091,     1.000,     0.083,    -0.121],  # Dragon
    [-0.043,     0.000,    -0.044,    -0.032,    0.000,     -0.040,    -0.070,    -0.022,    -0.071,    -0.164,    -0.036,    -0.071],  # Giant
    [ 0.023,     0.000,    -0.032,    -0.083,    0.040,      0.000,    -0.188,     0.073,    -0.089,    -0.355,     0.000,    -0.081],  # Knight
    [ 0.098,     0.167,     0.167,    -0.243,    0.070,      0.188,     0.000,     0.178,     0.200,     0.300,     0.176,    -0.768],  # Minion
    [-0.117,     0.050,    -0.100,    -0.085,    0.022,     -0.073,    -0.178,     0.000,    -0.135,    -0.267,    -0.059,    -0.332],  # Musketeer
    [ 0.140,     0.000,     0.042,    -0.091,    0.071,      0.089,    -0.200,     0.135,     0.000,    -0.355,     0.067,    -0.002],  # Prince
    [ 0.174,     0.000,     0.220,    -1.000,    0.164,      0.355,    -0.300,     0.267,     0.355,     0.000,    -0.583,    -0.703],  # Skeleton
    [ 0.084,     0.000,     0.143,    -0.083,    0.036,      0.000,    -0.176,     0.059,    -0.067,     0.583,     0.000,    -0.061],  # Valkyrie
    [ 0.812,     0.167,     0.377,     0.121,    0.071,      0.081,     0.768,     0.332,     0.002,     0.703,     0.061,     0.000]   # Wizard
    ])

    # List of all troops in the same order as the matrix
    all_troops = [
        "Archer",
        "Balloon",
        "Barbarian",
        "Dragon",
        "Giant",
        "Knight",
        "Minion",
        "Musketeer",
        "Prince",
        "Skeleton",
        "Valkyrie",
        "Wizard"
    ]
    troop_counts = [2, 1, 3, 1, 1, 1, 3, 1, 1, 10, 1, 1]

    def calculate_best_position(our_troop, enemy_troop, enemy_position):
        """
        Calculate the best position to deploy our troop based on enemy troop properties.
        """
        # Get properties from the merged dictionary
        our_props = TROOP_PROPERTIES.get(our_troop, {"attack_range": 0, "discovery_range": 0, "is_splash": False, "can_attack_air": False})
        enemy_props = TROOP_PROPERTIES.get(enemy_troop, {"attack_range": 0, "discovery_range": 0, "is_splash": False, "can_attack_air": False})

        our_range = our_props["attack_range"]*factor
        enemy_range = enemy_props["attack_range"]*factor
        enemy_discovery = enemy_props["discovery_range"]*factor
        is_enemy_splash = enemy_props["is_splash"]
        can_enemy_attack_air = enemy_props["can_attack_air"]

        # Determine if our troop is air or ground
        is_our_troop_air = our_troop in {"Minion", "Dragon", "Balloon"}

        # Check if the enemy can counter our troop
        if (is_our_troop_air and not can_enemy_attack_air) or (not is_our_troop_air):
            # Enemy cannot counter our troop (e.g., our troop is air and enemy cannot attack air)
            # Deploy as close as possible to the enemy to minimize travel time
            deploy_y = enemy_position[1] - our_range
            deploy_x = enemy_position[0]
        else:
            # Enemy can counter our troop
            # Calculate safe distance
            safe_distance = enemy_discovery # Stay outside enemy range

            # Calculate optimal position
            enemy_x, enemy_y = enemy_position
            if our_range > enemy_range:
                # Deploy within our attack range but outside enemy range
                deploy_x = enemy_x 
                deploy_y = enemy_y - safe_distance
            else:
                # Deploy at a safe distance and flank the enemy
                deploy_x = enemy_x + safe_distance if enemy_x < 0 else enemy_x - safe_distance
                deploy_y = enemy_y + 5  # Offset vertically to avoid splash damage

        # Ensure position is within arena bounds
        deploy_x = max(-25, min(25, deploy_x))
        deploy_y = max(0, min(50, deploy_y))
        
        return (deploy_x, deploy_y)

    def deploy_offensive_pair(frontline_troop, support_troop):
        """
        Deploy a pair of troops with the frontline troop in front and the backline troop slightly behind.
        """
        # Get enemy troops and their positions
        enemy_troops = arena_data['OppTroops']
        
        if enemy_troops:
            # If there are enemy troops, deploy near the closest one
            closest_enemy = min(enemy_troops, key=lambda x: x.position[1])
            deploy_pos = calculate_best_position(frontline_troop, closest_enemy.name, closest_enemy.position)
            
            # Deploy the frontline troop
            deploy_list.list_.append((frontline_troop, deploy_pos))
            
            # Deploy the backline troop slightly behind
            backline_pos = (deploy_pos[0], deploy_pos[1] - 5)  # 5 units behind
            deploy_list.list_.append((support_troop, backline_pos))
        else:
            # If no enemies, deploy at the border
            # Choose between left, center, or right lane attack
            lane = np.random.choice(["left", "center", "right"])
            
            if lane == "left":
                attack_x = -10
            elif lane == "right":
                attack_x = 10
            else:
                attack_x = 0
                
            # Deploy frontline troop at the border
            deploy_list.list_.append((frontline_troop, (attack_x, 50)))
            # Deploy support troop slightly behind
            deploy_list.list_.append((support_troop, (attack_x, 45)))

    # Get enemy troops and their positions
    enemy_troops = arena_data['OppTroops']
    my_elixir = arena_data["MyTower"].total_elixir
    deployable_troops = arena_data['MyTower'].deployable_troops
    
    # Create a vector of enemy troop counts for calculating counters
    opp_troops = np.zeros(12)
    for troop in enemy_troops:
        opp_troops[all_troops.index(troop.name)] += 1 / troop_counts[all_troops.index(troop.name)]
    
    # Calculate counter scores
    troop_scores = counters @ opp_troops
    
    # First priority: Defend tower if enemies are very close
    tower_position = (0, 0)  # Our tower position
    for enemy in enemy_troops:
        enemy_distance_to_tower = Utils.calculate_distance(enemy, arena_data['MyTower'], type_troop=True)
        if enemy_distance_to_tower < 15*factor:  # Reduced from 20 to 15 for more aggressive defense
            # Deploy best counter troops to defend the tower
            deployable_troop_scores = [troop_scores[all_troops.index(troop)] for troop in deployable_troops]
            best_counter = deployable_troops[np.argmax(deployable_troop_scores)]
            deploy_pos = calculate_best_position(best_counter, enemy.name, enemy.position)
            deploy_list.list_.append((best_counter, deploy_pos))
            break
    
    # Second priority: Launch powerful push if conditions are right
    if not deploy_list.list_ and can_launch_push(arena_data):
        # Try to find a valid push combination from deployable troops
        for tank, support1, support2, min_elixir in PUSH_COMBINATIONS:
            if (tank in deployable_troops and support1 in deployable_troops and 
                (support2 is None or support2 in deployable_troops) and 
                my_elixir >= min_elixir):
                deploy_push_combination(tank, support1, support2, arena_data)
                break

    # Third priority: Deploy offensive pairs if no immediate threats
    if not deploy_list.list_ and my_elixir >= 5:  # Reduced from 6 to 5 for more frequent deployments
        # Look for powerful offensive combinations using available troops
        if "Wizard" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Wizard")
        elif "Dragon" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Dragon")
        elif "Valkyrie" in deployable_troops and "Wizard" in deployable_troops:
            deploy_offensive_pair("Valkyrie", "Wizard")
        elif "Valkyrie" in deployable_troops and "Dragon" in deployable_troops:
            deploy_offensive_pair("Valkyrie", "Dragon")
        elif "Archer" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Archer")
    
    # Fourth priority: Deploy single counter troops if needed
    if not deploy_list.list_ and enemy_troops:
        deployable_troop_scores = [troop_scores[all_troops.index(troop)] for troop in deployable_troops]
        best_counter = deployable_troops[np.argmax(deployable_troop_scores)]
        closest_enemy = min(enemy_troops, key=lambda x: x.position[1])
        deploy_pos = calculate_best_position(best_counter, closest_enemy.name, closest_enemy.position)
        deploy_list.list_.append((best_counter, deploy_pos))
    
    # Last priority: Launch preemptive attack if no enemies and no troops deployed
    if not deploy_list.list_ and not enemy_troops and my_elixir >= 5:  # Reduced from 6 to 5
        # Choose between left, center, or right lane attack
        lane = np.random.choice(["left", "center", "right"])
        
        if lane == "left":
            attack_x = -10
        elif lane == "right":
            attack_x = 10
        else:
            attack_x = 0
            
        # Deploy available troops in sequence at the border
        for i, troop in enumerate(deployable_troops):
            if my_elixir >= TROOP_PROPERTIES[troop]["elixir"]:
                offset_x = i * 3 - 6  # Reduced spacing between troops
                deploy_list.list_.append((troop, (attack_x + offset_x, 50)))
                my_elixir -= TROOP_PROPERTIES[troop]["elixir"]
                if my_elixir <= 0:
                    break
    
    team_signal = str(eval(team_signal)[:4] + [stored_data])
