from teams.helper_function import Troops, Utils
import numpy as np
import math

team_name = "AggressiveHackstreet,4p"
troops = [Troops.wizard, Troops.minion, Troops.archer, Troops.valkyrie, Troops.dragon, Troops.skeleton, Troops.knight, Troops.musketeer]
deploy_list = Troops([])
team_signal = "[['', '', '', '', '', '', '', ''], ['', '', '', ''], 10, 0, ['']]"

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
    # Merged dictionary for troop properties (updated with new data)
    TROOP_PROPERTIES = {
        "Archer": {"attack_range": 5, "discovery_range": 8, "is_splash": False, "can_attack_air": True, "damage": 118, "health": 324},
        "Minion": {"attack_range": 2, "discovery_range": 4, "is_splash": False, "can_attack_air": True, "damage": 129, "health": 252},
        "Knight": {"attack_range": 0, "discovery_range": 7, "is_splash": False, "can_attack_air": False, "damage": 221, "health": 1938},
        "Skeleton": {"attack_range": 0, "discovery_range": 4, "is_splash": False, "can_attack_air": False, "damage": 89, "health": 89},
        "Dragon": {"attack_range": 3.5, "discovery_range": 5, "is_splash": True, "can_attack_air": True, "damage": 176, "health": 1267},
        "Valkyrie": {"attack_range": 0, "discovery_range": 7, "is_splash": True, "can_attack_air": False, "damage": 195, "health": 2097},
        "Musketeer": {"attack_range": 6, "discovery_range": 8, "is_splash": False, "can_attack_air": True, "damage": 239, "health": 792},
        "Giant": {"attack_range": 0, "discovery_range": 7, "is_splash": False, "can_attack_air": False, "damage": 337, "health": 5423},
        "Prince": {"attack_range": 0, "discovery_range": 5, "is_splash": False, "can_attack_air": False, "damage": 392, "health": 1920},
        "Barbarian": {"attack_range": 0, "discovery_range": 5, "is_splash": False, "can_attack_air": False, "damage": 161, "health": 736},
        "Balloon": {"attack_range": 0, "discovery_range": 5, "is_splash": True, "can_attack_air": False, "damage": 424, "health": 2226},
        "Wizard": {"attack_range": 5.5, "discovery_range": 8, "is_splash": True, "can_attack_air": True, "damage": 410, "health": 1100},
    }

    # Tower properties (updated with new data)
    TOWER_PROPERTIES = {
        "health": 7032,
        "damage": 158,
        "attack_range": 8,
        "splash_range": 0,
        "attack_speed": "Medium",
        "targets": ["Air", "Ground"]
    }

    counters = np.array([
    # Arch       Min        Knig     Skel     Drag     Valk       Musk     Gian     Prin     Barb     Ball     Wiz      (Defending Troops)
    [  0.000,  -35.592,  -8.277,  -14.952,  -13.544,   -1.038,  -11.787,    1.579,    4.874,   -8.820,  -12.933,   -6.564],  # Archer (Attacking)
    [ 35.592,    0.000,   20.490,    6.185,    8.137,   31.499,   18.788,   37.541,   60.668,   -0.350,   21.588,   -2.160],  # Minion
    [  8.277,  -20.490,    0.000,   -7.472,   -6.364,    5.875,   -3.091,    8.952,   15.043,   -3.910,   -3.230,   -1.074],  # Knight
    [ 14.952,   -6.185,    7.472,    0.000,  -50.000,   -50.090,    5.502,   15.411,   24.801,   -0.603,    0.000,    -50.000],  # Skeleton
    [ 13.544,   -8.137,    6.364,   -1.150,    0.000,   10.048,    3.744,   13.491,   21.346,   -0.186,    4.497,    1.513],  # Dragon
    [  1.038,  -31.499,   -5.875,  -12.090,  -10.048,    0.000,   -8.707,    2.890,    7.717,   -8.475,   -9.250,   -9.340],  # Valkyrie
    [ 11.787,  -18.788,    3.091,   -5.502,   -3.744,    8.707,    0.000,   12.633,   21.373,   -3.688,    0.450,   -2.975],  # Musketeer
    [ -1.579,  -37.541,   -8.952,  -15.411,  -13.491,   -2.890,  -12.633,    0.000,    2.892,   -9.225,  -13.714,   -8.085],  # Giant
    [ -4.874,  -60.669,  -15.043,  -24.801,  -21.346,   -7.717,  -21.373,   -2.892,    0.000,  -14.205,  -23.105,  -13.027],  # Prince
    [  8.820,    0.350,    3.910,    0.603,    0.186,    8.475,    3.688,    9.225,   14.205,    0.000,    3.964,    2.046],  # Barbarian
    [ 12.933,  -21.588,    3.230,   -6.470,   -4.497,    9.250,   -0.450,   13.714,   23.105,   -3.964,    0.000,   -2.787],  # Balloon
    [  6.564,    2.160,    1.074,    0.054,   -1.513,    9.340,    2.975,    8.085,   13.027,   12.046,    2.787,    0.000]   # Wizard
    ])

    # List of all troops in the same order as the matrix
    all_troops = ["Archer", "Minion", "Knight", "Skeleton", "Dragon", "Valkyrie", "Musketeer", "Giant", "Prince", "Barbarian", "Balloon", "Wizard"]
    troop_counts = [2, 3, 1, 10, 1, 1, 1, 1, 1, 3, 1, 1]

    # Get enemy troops and their positions
    enemy_troops = arena_data['OppTroops']



    def calculate_best_position(our_troop, enemy_troop, enemy_position):
        """
        Calculate the best position to deploy our troop based on enemy troop properties.
        Modified for aggressive positioning.
        """
        # Get properties from the merged dictionary
        our_props = TROOP_PROPERTIES.get(our_troop, {"attack_range": 0, "discovery_range": 0, "is_splash": False, "can_attack_air": False})
        enemy_props = TROOP_PROPERTIES.get(enemy_troop, {"attack_range": 0, "discovery_range": 0, "is_splash": False, "can_attack_air": False})

        our_range = our_props["attack_range"]*factor
        enemy_range = enemy_props["attack_range"]*factor
        is_our_troop_air = our_troop in {"Minion", "Dragon", "Balloon"}
        is_enemy_air = enemy_troop in {"Minion", "Dragon", "Balloon"}

        # AGGRESSIVE: Position troops ahead of enemy to intercept and push forward
        enemy_x, enemy_y = enemy_position

        # For air troops or troops that counter the enemy well, deploy more aggressively
        if is_our_troop_air or not enemy_props["can_attack_air"]:
            # Aggressive positioning - deploy directly on top of enemy for quick damage
            deploy_x = enemy_x
            deploy_y = min(50, enemy_y + 5)  # Push slightly ahead of enemy
        elif our_props["attack_range"] > 0:
            # For ranged troops, stay just within attack range but be aggressive
            deploy_x = enemy_x
            deploy_y = min(50, enemy_y + our_range/2)  # Position closer to enemy
        else:
            # For melee troops, deploy directly in enemy path but slightly ahead
            deploy_x = enemy_x
            deploy_y = min(50, enemy_y + 10)  # Position ahead to intercept
        
        # Ensure position is within arena bounds
        deploy_x = max(-25, min(25, deploy_x))
        deploy_y = max(0, min(50, deploy_y))
        
        return (deploy_x, deploy_y)

    def deploy_offensive_pair(frontline_troop, support_troop):
        """
        Deploy an aggressive troop pair on the offensive.
        """
        # Deploy troops toward the enemy side of the arena
        frontline_pos = (0, 50)  # Deploy at center of border 
        support_pos = (0, 45)    # Support slightly behind
        
        # For side attacks, choose a random side
        if np.random.random() > 0.5:
            frontline_pos = (15, 50)  # Right side attack
            support_pos = (10, 45)
        else:
            frontline_pos = (-15, 50)  # Left side attack
            support_pos = (-10, 45)
        
        deploy_list.list_.append((frontline_troop, frontline_pos))
        deploy_list.list_.append((support_troop, support_pos))

    
    # AGGRESSIVE: Always prioritize attacking over defending
    my_elixir = arena_data["MyTower"].total_elixir
    deployable_troops = arena_data['MyTower'].deployable_troops
    
    # Create a vector of enemy troop counts for calculating counters
    opp_troops = np.zeros(12)
    for troop in enemy_troops:
        opp_troops[all_troops.index(troop.name)] += 1 / troop_counts[all_troops.index(troop.name)]
    
    # Calculate counter scores
    troop_scores = counters @ opp_troops
    
    # AGGRESSIVE: Set up immediate offensive push if we have enough elixir
    if my_elixir >= 7:
        # Look for powerful offensive combinations first
        if "Wizard" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Wizard")
        elif "Dragon" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Dragon")
        elif "Valkyrie" in deployable_troops and "Wizard" in deployable_troops:
            deploy_offensive_pair("Valkyrie", "Wizard")
        elif "Valkyrie" in deployable_troops and "Dragon" in deployable_troops:
            deploy_offensive_pair("Valkyrie", "Dragon")
        elif "Musketeer" in deployable_troops and "Knight" in deployable_troops:
            deploy_offensive_pair("Knight", "Musketeer")
    
    # If we couldn't deploy offensive pairs but have enemy troops, deploy counters aggressively
    if not deploy_list.list_ and enemy_troops:
        # Find the best counter troop
        deployable_troop_scores = [troop_scores[all_troops.index(troop)] for troop in deployable_troops]
        best_counter_index = np.argmax(deployable_troop_scores)
        best_counter = deployable_troops[best_counter_index]
        
        # Find closest enemy to our border (lowest y)
        closest_enemy = min(enemy_troops, key=lambda x: x.position[1])
        
        # AGGRESSIVE: Deploy counter troop aggressively
        deploy_pos = calculate_best_position(best_counter, closest_enemy.name, closest_enemy.position)
        deploy_list.list_.append((best_counter, deploy_pos))
        
        # If we have enough elixir, deploy a second troop for support
        if my_elixir >= 6 and len(deployable_troops) > 1:
            second_best_index = np.argsort(deployable_troop_scores)[-2]
            second_best = deployable_troops[second_best_index]
            # Deploy second troop slightly offset
            deploy_pos_2 = (deploy_pos[0] + 5, deploy_pos[1] - 5)
            deploy_list.list_.append((second_best, deploy_pos_2))
    
    # AGGRESSIVE: If no enemies and no troops deployed yet, launch preemptive attack
    if not deploy_list.list_:
        # Choose between left, center, or right lane attack randomly
        lane = np.random.choice(["left", "center", "right"])
        
        if lane == "left":
            attack_x = -20
        elif lane == "right":
            attack_x = 20
        else:
            attack_x = 0
            
        # Deploy available troops in sequence at the border
        for i, troop in enumerate(deployable_troops):
            if my_elixir >= TROOP_PROPERTIES[troop]["health"] / 400:  # Rough elixir check
                offset_x = i * 5 - 10  # Spread troops horizontally
                deploy_list.list_.append((troop, (attack_x + offset_x, 50)))
                my_elixir -= TROOP_PROPERTIES[troop]["health"] / 400
                if my_elixir <= 0:
                    break
    
    team_signal = str(eval(team_signal)[:4] + [stored_data])
