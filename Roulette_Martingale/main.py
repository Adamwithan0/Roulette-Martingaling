import random
import pandas as pd
import pickle
import matplotlib.pyplot as plt



def roulette_spin():
    return random.randint(0, 37)  # 0 represents green (usually), 1-36 are red and black numbers


def roulette_bet( bet_color, bet_amount):
    outcome = roulette_spin()
    if outcome == 0 or outcome == 37:  # Green
        return -bet_amount
    elif (outcome % 2 == 0 and bet_color == "black") or (outcome % 2 != 0 and bet_color == "red"):
        return bet_amount
    else:
        return -bet_amount


def create_strategy_summary(starting_bet, max_spins, cash_out_point, num_trials):
    strategies = {
        "martingale": {"bet_func": martingale_bet, "params": {"starting_bet": starting_bet, "max_spins": max_spins,
                                                              "cash_out_point": cash_out_point}},
        "reverse_martingale": {"bet_func": reverse_martingale_bet,
                               "params": {"starting_bet": starting_bet, "max_spins": max_spins,
                                          "cash_out_point": cash_out_point}},
        "fibonacci": {"bet_func": fibonacci_bet, "params": {"starting_bet": starting_bet, "max_spins": max_spins,
                                                            "cash_out_point": cash_out_point}}
    }

    summary = []
    for strategy, info in strategies.items():
        total_won = 0
        total_lost = 0
        for _ in range(num_trials):
            balances, final_balance, turns_to_broke = info["bet_func"](**info["params"])
            if final_balance > 1000:
                total_won += 1
            else:
                total_lost += 1
        summary.append({"Strategy": strategy, "Trials": num_trials, "Total Won": total_won, "Total Lost": total_lost})

    df = pd.DataFrame(summary)
    return df


def martingale_bet(starting_bet, max_spins, cash_out_point):
    balance = 1000  # starting balance
    bet = starting_bet
    balances = []
    turns_to_broke = None

    for turns in range(max_spins):
        outcome = roulette_spin()

        if outcome % 2 == 0:  # Even numbers are considered "winning"
            balance += bet
            bet = starting_bet  # Reset bet to initial value on win
        else:
            balance -= bet
            bet *= 2  # Double the bet on loss

        if balance <= 0 or balance >= cash_out_point:
            turns_to_broke = turns + 1
            break

        balances.append(balance)

    return balances, balance, turns_to_broke


def reverse_martingale_bet(starting_bet, max_spins, cash_out_point):
    balance = 1000  # starting balance
    bet = starting_bet
    balances = []
    turns_to_broke = None

    for turns in range(max_spins):
        outcome = roulette_spin()

        if outcome % 2 == 0:  # Even numbers are considered "winning"
            balance += bet
            bet *= 2  # Double the bet on win
        else:
            balance -= bet
            bet = starting_bet  # Reset bet to initial value on loss

        if balance <= 0 or balance >= cash_out_point:
            turns_to_broke = turns + 1
            break

        balances.append(balance)

    return balances, balance, turns_to_broke


def fibonacci_bet(starting_bet, max_spins, cash_out_point):
    balance = 1000  # starting balance
    bet = starting_bet
    prev_bet = 0

    balances = []
    turns_to_broke = None

    for turns in range(max_spins):
        outcome = roulette_spin()

        if outcome % 2 == 0:  # Even numbers are considered "winning"
            balance += bet
            prev_prev_bet = prev_bet
            prev_bet = bet
            bet = prev_bet + prev_prev_bet  # Fibonacci sequence betting
        else:
            balance -= bet
            prev_prev_bet = prev_bet
            prev_bet = bet
            bet = prev_bet + prev_prev_bet  # Fibonacci sequence betting

        if balance <= 0 or balance >= cash_out_point:
            turns_to_broke = turns + 1
            break

        balances.append(balance)

    return balances, balance, turns_to_broke


def save_summary_to_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_summary_from_pickle(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


max_spins = 10000000000
cash_out_point = 4000
starting_bet = 10
num_trials = 10000000000
summary_filename = 'roulette_strategy_summary.pkl'



try:
    strategy_summary = load_summary_from_pickle(summary_filename)
except FileNotFoundError:
    strategy_summary = create_strategy_summary(starting_bet, max_spins, cash_out_point, num_trials)
    save_summary_to_pickle(strategy_summary, summary_filename)

num_simulations = 1000  # Number of simulations
strategy_balances = {
    "martingale": [],
    "reverse_martingale": [],
    "fibonacci": []
}
positive_cashflow_counts = {
    "martingale": 0,
    "reverse_martingale": 0,
    "fibonacci": 0
}  # Initialize the counts for each strategy
martingale_cashout_steps = []
reverse_martingale_cashout_steps = []
fibonacci_cashout_steps = []

for _ in range(num_simulations):
    martingale_balances, martingale_cashout_count, martingale_turns = martingale_bet(starting_bet, max_spins, cash_out_point)
    reverse_martingale_balances, reverse_martingale_cashout_count, rev_martingale_turns = reverse_martingale_bet(starting_bet, max_spins,
                                                                                              cash_out_point)
    fibonacci_balances, fibonacci_cashout_count, fib_turns = fibonacci_bet(starting_bet, max_spins, cash_out_point)


    martingale_cashout_steps.append(martingale_turns)
    reverse_martingale_cashout_steps.append(rev_martingale_turns)
    fibonacci_cashout_steps.append(fib_turns)


    if martingale_cashout_count > 0:
        positive_cashflow_counts["martingale"] += 1



    if reverse_martingale_cashout_count > 0:
        positive_cashflow_counts["reverse_martingale"] += 1


    if fibonacci_cashout_count > 0:
        positive_cashflow_counts["fibonacci"] += 1


    strategy_balances["martingale"].append(martingale_balances)
    strategy_balances["reverse_martingale"].append(reverse_martingale_balances)
    strategy_balances["fibonacci"].append(fibonacci_balances)

plt.style.use('ggplot')
plt.figure(figsize=(20, 6))
plt.title("Roulette Betting Strategies Simulation (100 Trials)")
plt.xlabel("Number of Spins")
plt.ylabel("Balance")

for strategy, balances_list in strategy_balances.items():
    color = 'red' if strategy == 'martingale' else 'green' if strategy == 'reverse_martingale' else 'blue'
    for i, balances in enumerate(balances_list):
        if i % 100 == 0:  # Plot every 10th path
            plt.plot(balances, color=color, alpha=0.5)

plt.savefig("Roulette_Strategies_Grouped_Balances.png")


for strategy, count in positive_cashflow_counts.items():
    print(f"{strategy.capitalize()} cashed out with positive cashflow {count} times.")



data = {
    "Strategy": ["Martingale", "Reverse Martingale", "Fibonacci"],
    "Cashouts": [
        positive_cashflow_counts["martingale"]/num_simulations,
        positive_cashflow_counts["reverse_martingale"]/num_simulations,
        positive_cashflow_counts["fibonacci"]/num_simulations
    ],
    "Average Spins per play": [
        sum(martingale_cashout_steps) / len(martingale_cashout_steps),
        sum(reverse_martingale_cashout_steps) / len(reverse_martingale_cashout_steps),
        sum(fibonacci_cashout_steps) / len(fibonacci_cashout_steps)
    ],
    "Average Winnings":[
        (positive_cashflow_counts["martingale"]*(cash_out_point - 1000) - (1000 * (num_simulations - positive_cashflow_counts["martingale"])))/num_simulations,
        (positive_cashflow_counts["reverse_martingale"]*(cash_out_point - 1000) - (1000 * (num_simulations - positive_cashflow_counts["reverse_martingale"])))/num_simulations,
        (positive_cashflow_counts["fibonacci"]*(cash_out_point - 1000) - (1000 * (num_simulations - positive_cashflow_counts["fibonacci"])))/num_simulations
    ]

}

# Create a DataFrame
df = pd.DataFrame(data)

fig, ax = plt.subplots(figsize=(8, 2))  # Adjust figsize for a larger table
ax.axis('off')
the_table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
the_table.auto_set_font_size(True)
plt.title("Results from 1000 simulations with a cashout point of 4000")
plt.savefig("Table")


