from game import Game
import inspect
import time
from config import TEAM1, TEAM2
from multiprocessing import Process, Manager

# Number of matches per batch and number of batches
MATCHES_PER_BATCH = 10
NUM_BATCHES = 10


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

def run_match(match_num, results, batch_num):
    print(f"Starting match {match_num}...")
    
    result = Game(
        TEAM1.troops, TEAM2.troops, TEAM1.team_name, TEAM2.team_name
    ).run()

    if "won" in result:
        winner = result.split(" ")[0]  # Extract winner's name
        reason = result.split()[-3]  # Extract tie breaker reason (1 or 2 or 0)
        duration = float(result.split("(")[-1].split()[0])  # Extract duration

        if winner == TEAM1.team_name:
            results["win"] += 1
            results[f"batch_{batch_num}_win"] += 1
            if int(reason) == 1:
                results["tb1wins"] += 1
            elif int(reason) == 2:
                results["tb2wins"] += 1
        else:
            results["loss"] += 1
            results[f"batch_{batch_num}_loss"] += 1
            if int(reason) == 1:
                results["tb1losses"] += 1
            elif int(reason) == 2:
                results["tb2losses"] += 1

        results["total_time"] += duration
        print(f"Match {match_num} → 🏆 {result}")

    elif "Match Draw" in result:
        duration = float(result.split("(")[-1].split()[0])
        results["draw"] += 1
        results[f"batch_{batch_num}_draw"] += 1
        results["total_time"] += duration
        print(f"Match {match_num} → 🤝 DRAW ({duration} secs)")

    else:
        print(f"Match {match_num} → ❓ UNKNOWN RESULT: {result}")

def run_batch(batch_num, results):
    print(f"\nStarting batch {batch_num}...")
    processes = []
    
    for i in range(MATCHES_PER_BATCH):
        match_num = (batch_num - 1) * MATCHES_PER_BATCH + i + 1
        p = Process(target=run_match, args=(match_num, results, batch_num))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

def main():
    team1_test_pass = validate_module(TEAM1, "TEAM 1")
    team2_test_pass = validate_module(TEAM2, "TEAM 2")

    if not (team1_test_pass and team2_test_pass):
        print("Failed validation. Exiting...")
        return

    with Manager() as manager:
        # Initialize results dictionary with batch-specific counters
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
        
        # Add batch-specific counters
        for batch in range(1, NUM_BATCHES + 1):
            results[f"batch_{batch}_win"] = 0
            results[f"batch_{batch}_loss"] = 0
            results[f"batch_{batch}_draw"] = 0

        # Run multiple batches
        for batch in range(1, NUM_BATCHES + 1):
            run_batch(batch, results)
            
            # Print intermediate results after each batch
            print(f"\n====== BATCH {batch} SUMMARY ======")
            print(f"✅ Wins in this batch: {results[f'batch_{batch}_win']}")
            print(f"❌ Losses in this batch: {results[f'batch_{batch}_loss']}")
            print(f"🤝 Draws in this batch: {results[f'batch_{batch}_draw']}")
            print("================================")

        print("\n====== FINAL MATCH SUMMARY ======")
        print(f"Total Matches Played: {NUM_BATCHES * MATCHES_PER_BATCH}")
        print(f"✅ Total Wins: {results['win']}")
        print(f"❌ Total Losses: {results['loss']}")
        print(f"🤝 Total Draws: {results['draw']}")
        print("==============================")
        print(f"✅ Total Tie Breaker 1 wins: {results['tb1wins']}")
        print(f"✅ Total Tie Breaker 2 wins: {results['tb2wins']}")
        print("==============================")
        print(f"❌ Total Tie Breaker 1 losses: {results['tb1losses']}")
        print(f"❌ Total Tie Breaker 2 losses: {results['tb2losses']}")
        print("==============================")
        print(f"⏱️ Average match duration: {results['total_time'] / (NUM_BATCHES * MATCHES_PER_BATCH):.2f} seconds")

if __name__ == "__main__":
    main()
