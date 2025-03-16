from game import Game
import inspect
from config import TEAM1, TEAM2
from multiprocessing import Process, Manager

# Number of matches to simulate
NUM_MATCHES = 100

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
    
    # Start the game and capture the result
    result = Game(
        TEAM1.troops, TEAM2.troops, TEAM1.team_name, TEAM2.team_name
    ).run()
    
    # Update the shared results
    if result == "WIN":
        results["win"] += 1
        print(f"Match {match_num} → ✅ WIN")
    elif result == "LOSS":
        results["loss"] += 1
        print(f"Match {match_num} → ❌ LOSS")
    elif result == "DRAW":
        results["draw"] += 1
        print(f"Match {match_num} → 🤝 DRAW")
    else:
        print(f"Match {match_num} → ❓ UNKNOWN RESULT: {result}")

def main():
    # Keep the original validation conditions unchanged
    team1_test_pass = validate_module(TEAM1, "TEAM 1")
    team2_test_pass = validate_module(TEAM2, "TEAM 2")

    if not (team1_test_pass and team2_test_pass):
        print("Failed validation. Exiting...")
        return

    with Manager() as manager:
        # Shared result dictionary to store match outcomes
        results = manager.dict({"win": 0, "loss": 0, "draw": 0})

        # Start multiple processes for parallel execution
        processes = []
        for i in range(NUM_MATCHES):
            p = Process(target=run_match, args=(i + 1, results))
            p.start()
            processes.append(p)

        # Wait for all processes to finish
        for p in processes:
            p.join()

        # Final result summary
        print("\n====== FINAL MATCH SUMMARY ======")
        print(f"✅ Wins: {results['win']}")
        print(f"❌ Losses: {results['loss']}")
        print(f"🤝 Draws: {results['draw']}")
        print("==============================")

if __name__ == "__main__":
    main()
