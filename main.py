from game import Game
import inspect
import time
from config import TEAM1, TEAM2
from multiprocessing import Process, Manager

# Number of matches to simulate
NUM_MATCHES = 20


def validate_module(module, name):
    attributes = dir(module)
    
    # Expected variables and classes
    expected_variables = {"team_name", "troops", "deploy_list", "team_signal"}
    expected_classes = {"Troops", "Utils"}
    
    # Extract variables (excluding functions, classes, and modules)
    variables = {
        attr for attr in attributes
        if not callable(getattr(module, attr))
        and not attr.startswith("__")
        and not inspect.ismodule(getattr(module, attr))
        and not inspect.isclass(getattr(module, attr))
    }
    
    # Extract classes
    classes = {
        attr for attr in attributes
        if inspect.isclass(getattr(module, attr))
    }
    
    # Condition 1: Check for exact variables and classes
    if variables != expected_variables:
        print(f"Fail: Variables do not match. Found: {variables} for {name}")
        return False
    
    if classes != expected_classes:
        print(f"Fail: Classes do not match. Found: {classes} for {name}")
        return False
    
    # Condition 3: Check len(set(troops)) == 8
    if len(set(module.troops)) != 8 or len(module.troops) != 8:
        print(f"Fail: troops does not contain exactly 8 unique elements for {name}")
        return False
    
    print(f"Pass: All conditions met for {name} : {module.team_name}!")
    return True

def run_match(match_num, results):
    print(f"Starting match {match_num}...")
    
    result = Game(
        TEAM1.troops, TEAM2.troops, TEAM1.team_name, TEAM2.team_name
    ).run()

    if "won" in result:
        winner = result.split(" ")[0]  # Extract winner's name
        reason = result.split()[-3]  # Extract tie breaker reason (1 or 2)
        duration = float(result.split("(")[-1].split()[0])  # Extract duration

        if winner == TEAM1.team_name:
            results["win"] += 1
            if int(reason) == 1:
                results["tb1wins"] += 1
            elif int(reason) == 2:  # ✅ Fixed from 1 to 2
                results["tb2wins"] += 1
        else:
            results["loss"] += 1
            if int(reason) == 1:
                results["tb1losses"] += 1
            elif int(reason) == 2:
                results["tb2losses"] += 1

        results["total_time"] += duration  # ✅ Track game time
        print(f"Match {match_num} → 🏆 {result}")

    elif "Match Draw" in result:
        duration = float(result.split("(")[-1].split()[0])
        results["draw"] += 1
        results["total_time"] += duration
        print(f"Match {match_num} → 🤝 DRAW ({duration} secs)")

    else:
        print(f"Match {match_num} → ❓ UNKNOWN RESULT: {result}")



def main():
    team1_test_pass = validate_module(TEAM1, "TEAM 1")
    team2_test_pass = validate_module(TEAM2, "TEAM 2")

    if not (team1_test_pass and team2_test_pass):
        print("Failed validation. Exiting...")
        return

    with Manager() as manager:
        results = manager.dict({
            "win": 0, 
            "loss": 0, 
            "draw": 0,
            "tb1wins": 0,
            "tb2wins": 0,
            "tb1losses": 0,
            "tb2losses": 0,
            "total_time": 0
        })

        processes = []
        for i in range(NUM_MATCHES):
            p = Process(target=run_match, args=(i + 1, results))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("\n====== FINAL MATCH SUMMARY ======")
        print(f"✅ Totals Wins: {results['win']}")
        print(f"❌ Total Losses: {results['loss']}")
        print(f"🤝 Draws: {results['draw']}")
        print("==============================")
        print(f"✅ Tie Breaker 1 wins: {results['tb1wins']}")
        print(f"✅ Tie Breaker 2 wins: {results['tb2wins']}")
        print("==============================")
        print(f"❌ Tie Breaker 1 losses: {results['tb1losses']}")
        print(f"❌ Tie Breaker 2 losses: {results['tb2losses']}")
        print("==============================")



if __name__ == "__main__":
    main()
