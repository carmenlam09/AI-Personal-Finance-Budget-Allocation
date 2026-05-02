import pandas as pd
import numpy as np
import random
from google.colab import files

# Example input data
# age_groups = {
#     'Below 24': {'Food': 0.25, 'Transport': 0.15, 'Housing': 0.2, 'Health':0.05, 'Subscription':0.15,
#               'Restaurants':0.05, 'Clothing':0.05, 'Fitness':0.05,'Others':0.05},
#     '25-34': {'Food': 0.25, 'Transport': 0.15, 'Housing': 0.2, 'Health':0.05, 'Subscription':0.15,
#               'Restaurants':0.05, 'Clothing':0.05, 'Fitness':0.05,'Others':0.05},
#     '35-44': {'Food': 0.25, 'Transport': 0.15, 'Housing': 0.2, 'Health':0.05, 'Subscription':0.15,
#               'Restaurants':0.05, 'Clothing':0.05, 'Fitness':0.05,'Others':0.05},
#     '45-64': {'Food': 0.25, 'Transport': 0.15, 'Housing': 0.2, 'Health':0.05, 'Subscription':0.15,
#               'Restaurants':0.05, 'Clothing':0.05, 'Fitness':0.05,'Others':0.05},
#     '65 and above': {'Food': 0.25, 'Transport': 0.15, 'Housing': 0.2, 'Health':0.05, 'Subscription':0.15,
#               'Restaurants':0.05, 'Clothing':0.05, 'Fitness':0.05,'Others':0.05},
# }

income_groups = {
    '1999 and below':{'Food': 0.2301, 'Transport': 0.069, 'Housing': 0.272, 'Health':0.025, 'Subscription':0.045,
                      'Restaurants':0.090, 'Clothing':0.021, 'Fitness':0.011,'Others':0.044},
    '2000-2999':{'Food': 0.238, 'Transport': 0.093, 'Housing': 0.277, 'Health':0.026, 'Subscription':0.056,
                      'Restaurants':0.116, 'Clothing':0.027, 'Fitness':0.014,'Others':0.063},
    '3000-3999':{'Food': 0.199, 'Transport': 0.091, 'Housing': 0.237, 'Health':0.024, 'Subscription':0.056,
                      'Restaurants':0.115, 'Clothing':0.027, 'Fitness':0.016,'Others':0.068},
    '4000-4999':{'Food': 0.169, 'Transport': 0.087, 'Housing': 0.216, 'Health':0.022, 'Subscription':0.057,
                      'Restaurants':0.117, 'Clothing':0.025, 'Fitness':0.016,'Others':0.068},
    '5000-5999':{'Food': 0.148, 'Transport': 0.080, 'Housing': 0.198, 'Health':0.021, 'Subscription':0.057,
                      'Restaurants':0.116, 'Clothing':0.023, 'Fitness':0.016,'Others':0.067},
    '6000-6999':{'Food': 0.133, 'Transport': 0.076, 'Housing': 0.188, 'Health':0.020, 'Subscription':0.056,
                      'Restaurants':0.113, 'Clothing':0.021, 'Fitness':0.017,'Others':0.065},
    '7000-7999':{'Food': 0.119, 'Transport': 0.075, 'Housing': 0.180, 'Health':0.019, 'Subscription':0.055,
                      'Restaurants':0.114, 'Clothing':0.020, 'Fitness':0.017,'Others':0.067},
    '8000-8999':{'Food': 0.111, 'Transport': 0.068, 'Housing': 0.173, 'Health':0.018, 'Subscription':0.053,
                      'Restaurants':0.107, 'Clothing':0.019, 'Fitness':0.017,'Others':0.066},
    '9000-9999':{'Food': 0.099, 'Transport': 0.069, 'Housing': 0.168, 'Health':0.017, 'Subscription':0.051,
                      'Restaurants':0.106, 'Clothing':0.018, 'Fitness':0.019,'Others':0.060},
    '10000-14999':{'Food': 0.078, 'Transport': 0.060, 'Housing': 0.153, 'Health':0.015, 'Subscription':0.049,
                      'Restaurants':0.099, 'Clothing':0.014, 'Fitness':0.019,'Others':0.060},
    '15000 and above':{'Food': 0.08, 'Transport': 0.10, 'Housing': 0.23, 'Health':0.02, 'Subscription':0.03,
                      'Restaurants':0.06, 'Clothing':0.02, 'Fitness':0.03,'Others':0.13},
}

# Compared to Malaysia average expenditure
# DONE COLUMNS FOR ALL STATES - FOOD, TRANSPORT, FITNESS, clothing, HEALTH,RESTAURANT,SUBSCRIPTION,HOUSING, OTHERS
# Others include insurans, personal care, miscellaneous goods
#Comapre to overall
states_adjustment = {
    'Johor':{'Food': 1.1061, 'Transport': 1.0654, 'Housing': 0.9983, 'Health':1.467, 'Subscription':1.0395,
              'Restaurants':0.8799, 'Clothing':1.026, 'Fitness':1.1026,'Others':1.1130},
    'Kedah':{'Food': 1.0132, 'Transport': 0.9229, 'Housing': 0.5688, 'Health':0.76, 'Subscription':0.7309,
              'Restaurants':0.5724, 'Clothing':1.1802, 'Fitness':0.5695,'Others':0.6475},
    'Kelantan':{'Food': 1.0048, 'Transport': 0.752, 'Housing': 0.5182, 'Health':0.38, 'Subscription':0.6272,
              'Restaurants':0.747, 'Clothing':0.6542, 'Fitness':0.3951,'Others':0.6284},
    'Melaka':{'Food': 1.078, 'Transport': 1.3851, 'Housing': 0.8239, 'Health':1.5118, 'Subscription':1.0914,
              'Restaurants':0.977, 'Clothing':1.6266, 'Fitness':1.6184,'Others':1.1935},
    'Negeri Sembilan':{'Food': 1.033, 'Transport': 0.9189, 'Housing': 0.7697, 'Health':1.0365, 'Subscription':0.9877,
              'Restaurants':0.7644, 'Clothing':0.8905, 'Fitness':1.3671,'Others':0.9943},
    'Pahang':{'Food': 0.973, 'Transport': 0.8223, 'Housing': 0.6644, 'Health':0.8199, 'Subscription':0.9111,
              'Restaurants':0.6873, 'Clothing':0.8412, 'Fitness':0.9332,'Others':0.7739},
    'Pulau Pinang':{'Food': 0.851, 'Transport': 0.7949, 'Housing': 1.105, 'Health':0.9967, 'Subscription':0.9877,
              'Restaurants':1.3122, 'Clothing':1.1037, 'Fitness':0.9515,'Others':1.0632},
    'Perak':{'Food': 1.008, 'Transport': 0.7257, 'Housing': 0.6631, 'Health':0.8511, 'Subscription':0.7259,
              'Restaurants':0.6788, 'Clothing':0.911, 'Fitness':0.6320,'Others':0.7548},
    'Perlis':{'Food': 0.999, 'Transport': 0.9247, 'Housing': 0.5743, 'Health':0.6975, 'Subscription':0.8173,
              'Restaurants':0.6628, 'Clothing':0.741, 'Fitness':0.5885,'Others':0.7261},
    'Selangor':{'Food': 0.945, 'Transport': 1.2713, 'Housing': 1.3547, 'Health':1.1681, 'Subscription':1.3852,
              'Restaurants':1.58, 'Clothing':1.189, 'Fitness':1.3935,'Others':1.3812},
    'Terengganu':{'Food': 1.227, 'Transport': 0.8520, 'Housing': 0.7221, 'Health':0.9017, 'Subscription':0.8815,
              'Restaurants':1.0133, 'Clothing':1.252, 'Fitness':0.7686,'Others':0.8448},
    'Sabah': {'Food': 0.846, 'Transport': 0.6829, 'Housing': 0.7634, 'Health':0.5081, 'Subscription':0.6222,
              'Restaurants':0.4454, 'Clothing':0.643, 'Fitness':0.3409,'Others':0.5402},
    'Sarawak':{'Food': 1.045, 'Transport': 0.7978, 'Housing': 0.753, 'Health':0.7249, 'Subscription':0.7086,
              'Restaurants':0.5043, 'Clothing':0.777, 'Fitness':0.7952,'Others':0.7069},
    'W.P. Kuala Lumpur': {'Food': 1.101, 'Transport': 1.3939, 'Housing': 2.0082, 'Health':1.2541, 'Subscription':1.3383,
              'Restaurants':1.6623, 'Clothing':0.885, 'Fitness':1.5294,'Others':1.4521},
    'W.P. Labuan':{'Food': 1.019, 'Transport': 0.7557, 'Housing': 1.0032, 'Health':0.5186, 'Subscription':0.9728,
              'Restaurants':0.5822, 'Clothing':0.628, 'Fitness':0.5663,'Others':0.5996},
    'W.P. Putrajaya':{'Food': 0.937, 'Transport': 0.19406, 'Housing': 2.24, 'Health':1.4738, 'Subscription':2.0617,
              'Restaurants':1.5681, 'Clothing':1.549, 'Fitness':2.6622,'Others':1.4981},
}

#Done
poverty_line = {
    'Johor':2589,
    'Kedah':2627,
    'Kelantan':2271,
    'Melaka':2670,
    'Negeri Sembilan':2402,
    'Pahang':2480,
    'Pulau Pinang':2250,
    'Perak':2297,
    'Perlis':2140,
    'Selangor':2830,
    'Terengganu':2751,
    'Sabah': 2742,
    'Sarawak':2618,
    'W.P. Kuala Lumpur': 2816,
    'W.P. Labuan':2816,
    'W.P. Putrajaya':2450

}

#cost of food based on the age group for each group I think we just take the bandar data for the cost of food and start from 15
# food_baseline = {
#     '18-25': 600,
#     '26-35': 800
# }
#Future direction

#mean income of each age group #DOne
average_income_age ={
    '15-19':1879,
    '20-24':2061,
    '25-29':2746,
    '30-34':2702,
    '35-39':3119,
    '40-44':3381,
    '45-49':4237,
    '50-54':4161,
    '55-59':4098,
    '60-64':3182
}

average_income_state ={
    'Johor':3212,
    'Kedah':2859,
    'Kelantan':2882,
    'Melaka':3311,
    'Negeri Sembilan':3375,
    'Pahang':3124,
    'Pulau Pinang':3557,
    'Perak':2973,
    'Perlis':2968,
    'Selangor':3885,
    'Terengganu':2898,
    'Sabah': 3127,
    'Sarawak':3158,
    'W.P. Kuala Lumpur': 4521,
    'W.P. Labuan':3636,
    'W.P. Putrajaya':4858
}

def saving_rate(state, income):
    pli = poverty_line[state]
    avg = average_income_state[state]

    # Case 1: Income below PLI
    if income < pli:
        division = pli / 6
        if pli - division < income <= pli:
            return np.random.uniform(0.04, 0.05)
        elif pli - 2*division < income <= pli - division:
            return np.random.uniform(0.03, 0.04)
        elif pli - 3*division < income <= pli - 2*division:
            return np.random.uniform(0.02, 0.03)
        elif pli - 4*division < income <= pli - 3*division:
            return np.random.uniform(0.01, 0.02)
        elif pli - 5*division < income <= pli - 4*division:
            return np.random.uniform(0, 0.01)
        else:
            return 0

    # Case 2: Between PLI and Average Income
    elif income < avg:
        division = (avg - pli) / 7
        if pli + division < income <= pli + 2*division:
            return np.random.uniform(0.06, 0.07)
        elif pli + 2*division < income <= pli + 3*division:
            return np.random.uniform(0.07, 0.08)
        elif pli + 3*division < income <= pli + 4*division:
            return np.random.uniform(0.08, 0.09)
        elif pli + 4*division < income <= pli + 5*division:
            return np.random.uniform(0.09, 0.10)
        elif pli + 5*division < income <= pli + 6*division:
            return np.random.uniform(0.10, 0.11)
        elif pli + 6*division < income <= pli + 7*division:
            return np.random.uniform(0.11, 0.12)
        else:
            return np.random.uniform(0.12, 0.13)

    # Case 3: Above Average Income
    else:
        division = (avg) / 6  # or could base on avg_income gap (tunable)
        if avg + division < income <= avg + 2*division:
            return np.random.uniform(0.14, 0.15)
        elif avg + 2*division < income <= avg + 3*division:
            return np.random.uniform(0.15, 0.16)
        elif avg + 3*division < income <= avg + 4*division:
            return np.random.uniform(0.16, 0.17)
        elif avg + 4*division < income <= avg + 5*division:
            return np.random.uniform(0.17, 0.18)
        elif avg + 5*division < income <= avg + 6*division:
            return np.random.uniform(0.18, 0.19)
        else:
            return np.random.uniform(0.19, 0.20)


def generate_synthetic_data(n_samples=1000):
    data = []

    states = list(poverty_line.keys())
    age_groups = list(average_income_age.keys())
    income_brackets = list(income_groups.keys())

    for _ in range(n_samples):
        # Pick random state, age group, and income bracket
        state = random.choice(states)
        age_group = random.choice(age_groups)
        bracket = random.choice(income_brackets)

        # Estimate base income from average + noise
        base_income = average_income_state[state]
        age_income = average_income_age[age_group]
        bracket_mid = np.mean([int(s) for s in bracket.replace(" and above","").split('-') if s.isdigit()] or [age_income])

        # Randomized income influenced by all three
        income = np.mean([base_income, age_income, bracket_mid])
        income = income + np.random.normal(0, income*0.1)  # ±10% variation
        income = max(500, income)  # avoid negative or too small values

        # Savings
        savings_rate = saving_rate(state, income)
        savings = income * savings_rate

        # Expenditure distribution
        proportions = income_groups[bracket].copy()
        state_adj = states_adjustment[state]

        # Apply state adjustment + ± noise
        adjusted = {k: v * state_adj[k] * (1 + np.random.uniform(-0.05, 0.05))
                    for k, v in proportions.items()}

        # Normalize to sum=1 (after adjustment)
        total = sum(adjusted.values())
        adjusted = {k: v/total for k, v in adjusted.items()}

        # Calculate actual expenditure per category
        expenditures = {k: v * (income - savings) for k, v in adjusted.items()}

        # Append to dataset
        record = {
            "State": state,
            "AgeGroup": age_group,
            "Income": round(income,2),
            "SavingsRate": round(savings_rate,4),
            "Savings": round(savings,2),
            "PLI": poverty_line[state],
        }
        record.update({cat: round(val,2) for cat, val in expenditures.items()})

        data.append(record)

    return pd.DataFrame(data)

# Example
df = generate_synthetic_data(2000)
print(df.head(10))

df.to_csv("synthetic_data.csv", index=False)
files.download("synthetic_data.csv")