# from teams.helper_function import Troops, Utils

# team_name = "DELHI"
# troops = [Troops.dragon,Troops.skeleton,Troops.wizard,Troops.minion,Troops.archer,Troops.giant,Troops.balloon,Troops.barbarian]
# deploy_list = Troops([])
# team_signal = ""

# def deploy(arena_data:dict):
#     """
#     DON'T TEMPER DEPLOY FUCNTION
#     """
#     deploy_list.list_ = []
#     logic(arena_data)
#     return deploy_list.list_, team_signal

# def logic(arena_data:dict):
#     global team_signal
#     deploy_list.deploy_dragon((-16,0))

from teams.helper_function import Troops, Utils

team_name = "Adit"
troops = [Troops.wizard,Troops.minion,Troops.archer,Troops.valkyrie,Troops.dragon,Troops.skeleton,Troops.giant,Troops.musketeer]
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
    troop_names = {'A' : 'Archer', 'm' : 'Minion', 'K' : 'Knight', 'S' : 'Skeleton', 'D' : 'Dragon', 'V' : 'Valkyrie', 'M' : 'Musketeer', 'G' : 'Giant', 'P' : 'Prince', 'b' : 'Barbarian', 'B' : 'Balloon', 'W' : 'Wizard', '' : ''}
    troop_codes = {c : t for (t, c) in troop_names.items()}
    troop_elixirs = {"Archer": 3, "Minion": 3, "Knight": 3, "Skeleton": 3, "Dragon": 4, "Va"
    "lkyrie": 4, "Musketeer": 4, "Giant": 5, "Prince": 5, "Barbarian": 3, "Balloon": 5, "Wizard": 5}
    opp_data = eval(team_signal)
    for troop in arena_data['OppTroops']:
        # # print(troop.uid)
        if troop_codes[troop.name] not in opp_data[0]:
            for i in range(8):
                if opp_data[0][i] == '':
                    # # print("found new troop")
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

def logic(arena_data:dict):
    global team_signal
    team_signal, curr_cards = update_signal(team_signal, arena_data)
    stored_data = eval(team_signal)[4]
    # print(team_signal, curr_cards)
    '''deploy_list.list_.append((arena_data["MyTower"].deployable_troops[0],(0,0)))
    deploy_list.list_.append((arena_data["MyTower"].deployable_troops[1],(0,0)))'''


    wanted_troops = ["Giant", "Wizard", "Skeleton"]
    troop_elixirs = [5, 5, 3]
    positions = [50, 25, 20]
    deployable_troops = arena_data["MyTower"].deployable_troops
    if(wanted_troops[0] in deployable_troops and wanted_troops[1] in deployable_troops and wanted_troops[2] in deployable_troops) or stored_data[0]:
        if stored_data[0] == '2' and arena_data['MyTower'].total_elixir > troop_elixirs[2]:
            deploy_list.list_.append((wanted_troops[2], (25, positions[2])))
            stored_data[0] = ''
        elif stored_data[0] == '1' and arena_data['MyTower'].total_elixir > troop_elixirs[1]:
            deploy_list.list_.append((wanted_troops[1], (25, positions[1])))
            stored_data[0] = '2'
        elif arena_data['MyTower'].total_elixir >= 9:
            deploy_list.list_.append((wanted_troops[0], (25, positions[0])))
            stored_data[0] = '1'
    else:
        for troop in deployable_troops:
            if troop not in wanted_troops:
                deploy_list.list_.append((troop, (0, 0)))
                break

    team_signal = str(eval(team_signal)[:4] + [stored_data])