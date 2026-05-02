import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

# --- Parameters (make interactive with Streamlit widgets) ---
current_age = st.number_input("Current Age", min_value=18, max_value=50, value=25)
retirement_age = st.number_input("Retirement Age", min_value=current_age+1, max_value=70, value=60)
starting_savings = st.number_input("Starting Savings (RM)", min_value=0, value=340)
starting_income = st.number_input("Starting Annual Income (RM)", min_value=0, value=30000)
# interest_rate = st.slider("Annual Return (Investment Rate)", 0.0, 0.15, 0.05)
    
def get_age_group(age):
    if age<20:
        return "Below 20"
    elif age<25:
        return "20-24"
    elif age<30:
        return"25-29"
    elif age<35:
        return "30-34"
    elif age<40:
        return "35-39"
    elif age<45:
        return "40-44"
    elif age<50:
        return "45-49"
    else:
        return "50 and above"
    
income_growth_by_group = {
    "Below 25": 0.026,
    "25-29": 0.275,
    "30-34": 0.349,
    "35-39": 0.153,
    "40-44": 0.127,
    "45-49": -0.031,
    "50-54": -0.021,
    "50 and above": -0.064
}

def saving_rate_by_age(age):
    base = 0.10
    increase = 0.0025 * max(0, age - current_age)
    return min(0.20, base + increase)

def simulate_fixed_savings(current_age, starting_income, starting_savings):
    ages = list(range(current_age, 61))
    income = starting_income
    today = datetime.today()
    months_left = 12 - today.month + 1
    balances = [starting_savings*months_left ]

    prev_group = get_age_group(current_age)

    for age in ages[1:]:
        current_group = get_age_group(age)

        # Only apply growth when moving to a new group
        if current_group != prev_group:
            income *= (1 + income_growth_by_group[current_group])
            prev_group = current_group  # update previous group

        print(str(age)+"-"+str(income))

        # Contribution: partial months for current age, full 12 months for later
        if age == current_age:
            contribution = income * 0.20 * months_left
        else:
            contribution = income * 0.20 * 12

        new_balance = balances[-1] + contribution 
        balances.append(new_balance)

    return ages, balances


# --- Extract ages when targets are reached ---
def age_when_target_reached(ages, balances, target):
    for age, balance in zip(ages, balances):
        if balance >= target:
            return age
    return None  # if never reached

# Benchmarks

st.title("Saving Growth Calculator")

# basic_retirement_saving=390000/1000000
# adequate_retirement_saving=650000/1000000
# enhanced_retirement_saving=1300000/1000000

basic_retirement_saving=390000
adequate_retirement_saving=650000
enhanced_retirement_saving=1300000
inflation_rate = 1.83    
years_to_retirement = 60 - current_age
future_basic_target = basic_retirement_saving * (inflation_rate) * years_to_retirement

# --- Scenario 2: Progressive savings rate ---
def saving_rate_by_age(age,current_age):
    base = 0.20
    increase = 0.005 * ((age - current_age) // 5)  # +0.5% every 5 years
    return min(0.40, base + increase)  # cap at 30%

# def simulate_progressive_savings(age,starting_income,starting_savings):
#     ages = list(range(current_age, 60 + 1))
#     balances = [starting_savings]
#     income = starting_income

#     for age in ages[1:]:
#         current_group = get_age_group(age)

#         # Only apply growth when moving to a new group
#         if current_group != prev_group:
#             income *= (1 + income_growth_by_group[current_group])
#             prev_group = current_group  # update previous group

#         # Contribution: partial months for current age, full 12 months for later
#         if age == current_age:
#             contribution = income * 0.20 * months_left
#         else:
#             contribution = income * 0.20 * 12
#         income *= (1 + income_growth_by_age(age - 1))
#         print(str(age)+"-"+str(income))
#         srate = saving_rate_by_age(age,current_age)
#         contribution = income * srate *12
#         new_balance = (balances[-1] + contribution)
#         balances.append(new_balance)

#     return ages, balances

# --- Run simulations ---
ages, fixed_balances = simulate_fixed_savings(current_age,starting_income,starting_savings)
# _, progressive_balances = simulate_progressive_savings(current_age,starting_income,starting_savings)
# fixed_balances_mil=[b/1000000 for b in fixed_balances]
# progressive_balances_mil=[b/1000000 for b in progressive_balances]

basic_age = age_when_target_reached(ages, fixed_balances , basic_retirement_saving)
adequate_age = age_when_target_reached(ages, fixed_balances, adequate_retirement_saving,)
enhanced_age = age_when_target_reached(ages, fixed_balances, enhanced_retirement_saving,)

st.write(f"At age 60, RM{fixed_balances[-1]:,.2f} will be saved")
st.write(f"🏦 Basic target (RM {basic_retirement_saving:,.0f}) reached at age: {basic_age}")
st.write(f"💰 Adequate target (RM {adequate_retirement_saving:,.0f}) reached at age: {adequate_age}")
st.write(f"🚀 Enhanced target (RM {enhanced_retirement_saving:,.0f}) reached at age: {enhanced_age}")
print(fixed_balances)

fig, ax = plt.subplots(figsize=(10, 6))

# Savings lines
ax.plot(ages, fixed_balances, marker='o', color='#1f77b4', label='Fixed 20% Savings', linewidth=2)
# ax.plot(ages, progressive_balances, marker='s', linestyle='--', color='#ff7f0e', label='Progressive Savings (20% → 40%)', linewidth=2)

# Benchmarks
ax.axhline(basic_retirement_saving, linestyle='--', color='red', label='Basic Target (Current)')
ax.axhline(adequate_retirement_saving, linestyle='--', color='green', label='Adequate Target')
ax.axhline(enhanced_retirement_saving, linestyle='--', color='blue', label='Enhanced Target')

# Labels & Title
ax.set_title(f'Savings Projection to Retirement (Age {retirement_age})', fontsize=16, fontweight='bold')
ax.set_xlabel('Age', fontsize=12)
ax.set_ylabel('Balance (RM)', fontsize=12)
ax.grid(alpha=0.3)
ax.legend(loc='upper left', fontsize=10)

# Optional: annotate final savings
ax.annotate(f'RM{fixed_balances[-1]:,.0f}', 
            xy=(ages[-1], fixed_balances[-1]), 
            xytext=(ages[-1]-5, fixed_balances[-1]+50_000),
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontsize=10)

fig.tight_layout()
st.pyplot(fig)


