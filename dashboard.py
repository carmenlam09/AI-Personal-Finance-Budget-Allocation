import streamlit as st
import datetime
from groq import Groq
import os
from dotenv import load_dotenv
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import uuid
from utils import firebase
from allocator import predict_allocation_50_30_20

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialise groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Savings data
basic_retirement_saving=390000
adequate_retirement_saving=650000
enhanced_retirement_saving=1300000

income_growth_by_group = {
    "Below 20": 0,
    "20-24": 0.026,
    "25-29": 0.275,
    "30-34": 0.349,
    "35-39": 0.153,
    "40-44": 0.127,
    "45-49": -0.031,
    "50-54": -0.021,
    "50 and above": -0.064
}

# Investment data
INVESTMENT_OPTIONS = [
    {"Investment Type": "Employees Provident Fund (EPF)", "Expected Returns (Annual)": "5.0% – 6.1%", "Liquidity": "Low (Locked until withdrawal age)", "Risk Level": "Very Low: (Government-backed)","Interest Rate":0.0555},
    {"Investment Type": "Amanah Saham Bumiputera (ASB) / Amanah Saham Malaysia (ASM)", "Expected Returns (Annual)": "4.0% – 7.0%", "Liquidity": "Medium (ASM may have limited quota)", "Risk Level": "Low: (Government-backed)","Interest Rate":0.055},
    {"Investment Type": "High-Yield Savings Accounts", "Expected Returns (Annual)": "Up to 4.88%", "Liquidity": "High (Funds accessible anytime)", "Risk Level": "Very Low: (PIDM insured)","Interest Rate":0.0375},
    {"Investment Type": "Money Market / Cash Management Funds", "Expected Returns (Annual)": "2.5% – 3.0%", "Liquidity": "High (Funds accessible anytime)", "Risk Level": "Low","Interest Rate":0.0275},
    {"Investment Type": "Bonds and Sukuk", "Expected Returns (Annual)": "3.5% – 5.5%", "Liquidity": "Medium (Depends on bond tenure)", "Risk Level": "Low to Medium: (Corporate bonds have default risk)","Interest Rate":0.045},
    {"Investment Type": "Fixed Deposits", "Expected Returns (Annual)": "2.35% – 3.45%", "Liquidity": "Low (Penalty for early withdrawal)", "Risk Level": "Very Low: (PIDM insured)","Interest Rate":0.029},
    {"Investment Type": "Real Estate Investment Trusts (REITs)", "Expected Returns (Annual)": "4% – 6%", "Liquidity": "Medium (Traded on stock exchange)", "Risk Level": "Medium: (Stock market fluctuations)","Interest Rate":0.05},
    {"Investment Type": "Gold and Precious Metals", "Expected Returns (Annual)": "No fixed returns, value fluctuates", "Liquidity": "High (Gold can be sold anytime)", "Risk Level": "Low: (Inflation hedge, but no passive income)","Interest Rate":0}
]

def get_budget_allocation(age_group, income, housing, subscriptions, state, debt=0,):        
    allocations, group_targets, fig = predict_allocation_50_30_20(
    age_group=age_group,
    salary=income,
    housing=housing,
    subscriptions=subscriptions,
    state=state,
    debt=debt,
    )
    return allocations, group_targets, fig

def get_investment_recommendations(income, age, savings_percentage, risk_tolerance):
    savings_amount = income * (savings_percentage / 100)

    prompt = f"""
    You are a financial assistant for Malaysian individual investor.
    Based on {savings_percentage}% of RM{income:,.2f} income (RM{savings_amount:,.2f}), age {age}, and {risk_tolerance} risk tolerance, recommend the TOP 3 suitable investments from the following list:
    {json.dumps(INVESTMENT_OPTIONS, indent=2)}

    Consider the individual's income, age, savings percentage, risk capacity, and Malaysian investment landscape.
    
    Output ONLY a valid JSON object in this exact format:
    {{
        "instrument1": {{"name": "Investment Name", "amount": amount_number}},
        "instrument2": {{"name": "Investment Name", "amount": amount_number}},
        "instrument3": {{"name": "Investment Name", "amount": amount_number}}
    }}

    Make sure the 3 amounts is not more than RM{savings_amount:,.2f}.
    """

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful Malaysian financial advisor. Always respond with valid JSON format only."},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=500
        )

        # Parse the json response
        recommendations = json.loads(response.choices[0].message.content.strip())
        #print("Raw response:")
        #print(recommendations)

        return recommendations
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        # Return fallback recommendations
        fallback_amount = savings_amount / 3
        return {
            "instrument1": {"name": "High-Yield Savings Accounts", "amount": fallback_amount},
            "instrument2": {"name": "Amanah Saham Bumiputera (ASB) / Amanah Saham Malaysia (ASM)", "amount": fallback_amount},
            "instrument3": {"name": "Employees Provident Fund (EPF)", "amount": fallback_amount}
        }

def chat_with_financebot(prompt, user_data):
    context = f"""User Profile:
    - Monthly Income: RM{user_data.get('income', 0):,.2f}
    - Age: {user_data.get('age', 0)}
    - State: {user_data.get('state', 'Not specified')}
    - Rent: RM{user_data.get('rent', 0):,.2f}
    - Debt: RM{user_data.get('debt', 0):,.2f}
    - Subscription Services: RM{user_data.get('subscription_services', 0):,.2f}
    - Additional Requirements: {user_data.get('requirements', 'None')}
    
    User Question: {prompt}

    Provide personalised and CONCISE financial advice based on the user's profile and question. Ensure your response is exactly 400 words or less.
    """

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are FinanceBot, a Malaysian personal finance advisor. Provide personalised and concise advice. CRITICAL REQUIREMENT: Your response must be EXACTLY 400 words or less. This is non-negotiable."},
                {"role": "user", "content": context}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.5,
            max_tokens=4096,
            top_p=0.9
        )
        #print("==========Financebot raw response==========")
        #print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

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
    
def simulate_fixed_savings(current_age, starting_income, starting_savings,date_selected):
    ages = list(range(current_age, 61))
    income = starting_income
    today = date_selected
    months_left = 12 - today.month + 1
    balances = [starting_savings*months_left ]

    prev_group = get_age_group(current_age)

    for age in ages[1:]:
        current_group = get_age_group(age)

        # Only apply growth when moving to a new group
        if current_group != prev_group:
            income *= (1 + income_growth_by_group[current_group])
            prev_group = current_group  # update previous group

        #print(str(age)+"-"+str(income))

        # Contribution: partial months for current age, full 12 months for later
        if age == current_age:
            contribution = income * 0.20 * months_left
        else:
            contribution = income * 0.20 * 12

        new_balance = balances[-1] + contribution
        balances.append(new_balance)

    return ages, balances

def simulate_investment_growth_selection(investment_name, expected_return, recommended_investment, years):
    fv_per_year = {}
    fv_per_year[investment_name] = []
    fv_per_year[investment_name] .append(recommended_investment)
    amount = recommended_investment
    for year in range(1, years + 1):
        amount *= (1 + expected_return)
        #print(f"{year}-{amount}")
        fv_per_year[investment_name].append(amount)
    return fv_per_year

# Extract ages when targets are reached
def age_when_target_reached(ages, balances, target):
    for age, balance in zip(ages, balances):
        if balance >= target:
            return age
    return None  # if never reached

# --------------- STREAMLIT APP CONFIGURATION ---------------
st.set_page_config(page_title="AI Personal Finance Model", layout="wide")

# Initialise session state
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------- SIDE BAR -------------------------
with st.sidebar:
    # Side bar styling
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #01B8AA;
                color: white;
                display: flex;
                flex-direction: column;
                justify-content: space-between; 
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Side bar input
    st.title(":iphone: AI Personal Finance Model")
    st.divider()
    
    with st.form("user_input_form"):
        st.subheader("Month to be Scheduled")
        date_selected = st.date_input("Date", value=datetime.date.today())

        st.subheader("Monthly Income")
        income = st.number_input("Income (RM)", min_value=0.0, step=100.0)

        st.subheader("Age")
        age = st.number_input("Age", min_value=18, max_value=100, step=1, format="%d")

        st.subheader("State")
        state = st.selectbox(
            "Select State",
            (
                "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan",
                "Pahang", "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak",
                "Selangor", "Terengganu", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"
            ),
            index=None,
            placeholder="Select state"
        )

        st.subheader("Commitments")
        rent = st.number_input("Rent (RM)", min_value=0.0, step=50.0)
        debt = st.number_input("Debt (RM)", min_value=0.0, step=50.0)
        subscription_services = st.number_input("Subscription Services (RM)", min_value=0.0, step=10.0)
        
        st.subheader("Investment Preferences")
        risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])

        st.write("")
        st.write("")
        st.write("")
        submit = st.form_submit_button("Generate Financial Plan", type="primary", width="stretch")

    # --- Footer ---
    st.divider()
    st.write("Made by:")
    st.image("logo.png", width="stretch")

# Collect user input into dictionary
if submit and income > 0:
    savings_percentage = 20
    age_group=get_age_group(age)
    st.session_state.user_data = {
        "date": date_selected ,
        "income": income,
        "age":age,
        "age_group": age_group,
        "state": state,
        "rent": rent,
        # "debt": debt,
        "subscription_services": subscription_services,
        # "requirements": requirements,
        "risk_tolerance": risk_tolerance,
        "savings_percentage": savings_percentage
    }

    # Debugging: Print user_data to terminal
    print("===== st.session_state.user_data =====")
    print(json.dumps(st.session_state.user_data, indent=2, default=str))
    print("======================")

# ---------------------- MAIN DASHBOARD ----------------------
st.title("📊 AI Personal Finance Dashboard")

# Dashboard layout
if st.session_state.user_data:
    user_data = st.session_state.user_data

    with st.container(border=True):
        st.subheader("💰 Personalised Budget Plan")
        with st.spinner("Generating budget plan..."):
            allocations, group_targets, fig = get_budget_allocation(
                age_group=get_age_group(age),
                income=income,
                housing=rent,
                subscriptions=subscription_services, 
                state=state,
                debt=debt
            )

            st.write("### 📊 Allocation Chart")
            st.plotly_chart(fig, use_container_width=True)

            budget_col1, budget_col2 = st.columns([1, 1])

            with budget_col1:
                st.write("### 📌 Group Allocation (50/30/20 Rule)")
                st.json(group_targets)
                

            with budget_col2:
                st.write("### 📌 Detailed Allocation")
                st.dataframe(allocations, width="stretch")
                

    with st.container(border=True):
        st.subheader("📈 Saving Projection Growth")
        
        ages, fixed_balances = simulate_fixed_savings(age,income,income*0.2,date_selected )
        
        basic_age = age_when_target_reached(ages, fixed_balances , basic_retirement_saving)
        adequate_age = age_when_target_reached(ages, fixed_balances, adequate_retirement_saving,)
        enhanced_age = age_when_target_reached(ages, fixed_balances, enhanced_retirement_saving,)

        savings_col1, savings_col2 = st.columns([2, 1])

        with savings_col1:
            fig, ax = plt.subplots(figsize=(10, 8))

            # Savings lines
            ax.plot(ages, fixed_balances, marker='o', color='#1f77b4', label='Fixed 20% Savings', linewidth=2)
            # ax.plot(ages, progressive_balances, marker='s', linestyle='--', color='#ff7f0e', label='Progressive Savings (20% → 40%)', linewidth=2)

            # Benchmarks
            ax.axhline(basic_retirement_saving, linestyle='--', color='red', label='Basic Target (Current)')
            ax.axhline(adequate_retirement_saving, linestyle='--', color='green', label='Adequate Target')
            ax.axhline(enhanced_retirement_saving, linestyle='--', color='blue', label='Enhanced Target')

            # Labels & Title
            ax.set_title(f'Savings Projection to Retirement (Age 60)', fontsize=16, fontweight='bold')
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
        
        with savings_col2:
            st.write(f"**📌 Initial Saving: RM {income*0.2:,.2f}**")
            # st.write(f"At age 60, RM{fixed_balances[-1]:,.2f} will be saved")
            # st.write(f"🏦 Basic target (RM {basic_retirement_saving:,.0f}) reached at age: {basic_age}")
            # st.write(f"💰 Adequate target (RM {adequate_retirement_saving:,.0f}) reached at age: {adequate_age}")
            # st.write(f"🚀 Enhanced target (RM {enhanced_retirement_saving:,.0f}) reached at age: {enhanced_age}")
            st.metric("Total at Age 60", f"RM {fixed_balances[-1]:,.2f}")
            st.write(f"🏦 **Basic target** (RM {basic_retirement_saving:,.0f})")
            st.write(f"✅ Reached at age: {basic_age}" if basic_age else "❌ Not reached by 60")
            st.write(f"💰 **Adequate target** (RM {adequate_retirement_saving:,.0f})")
            st.write(f"✅ Reached at age: {adequate_age}" if adequate_age else "❌ Not reached by 60")
            st.write(f"🚀 **Enhanced target** (RM {enhanced_retirement_saving:,.0f})")
            st.write(f"✅ Reached at age: {enhanced_age}" if enhanced_age else "❌ Not reached by 60")

    all_investments = {}

    with st.container(border=True):
        st.subheader("🎯 Investment Recommedations")
        with st.spinner("Getting investment recommendations..."):
            investment_recommendations = get_investment_recommendations(
               user_data["income"],
               user_data["age"],
               user_data["savings_percentage"],
               user_data["risk_tolerance"]
            )
            # investment_recommendations = {
            #     "instrument1": {"name": "High-Yield Savings Accounts", "amount": 60},
            #     "instrument2": {"name": "Amanah Saham Bumiputera (ASB) / Amanah Saham Malaysia (ASM)", "amount": 60},
            #     "instrument3": {"name": "Employees Provident Fund (EPF)", "amount": 60}
            # }
            st.write(f"Recommended investment instruments and corresponding amount")
            
            inv_col1, inv_col2, inv_col3 = st.columns(3, gap="small", border=True)

            total_amount = 0
            investment_items = list(investment_recommendations.items())

            risk_colors = {
                "Very Low": "#28a745",
                "Low": "#28a745",
                "Low to Medium": "#28a745",
                "Medium": "#ffc107",
                "High": "#dc3545"
            }
            
            for i, (key, investment) in enumerate(investment_items):
                investment_details = next(
                    (inv for inv in INVESTMENT_OPTIONS if inv["Investment Type"] == investment["name"]),
                    None
                )
                
                if investment_details and investment_details["Interest Rate"] != 0:
                    all_investments.update(
                        simulate_investment_growth_selection(investment['name'], investment_details["Interest Rate"], investment["amount"], 10)
                    )
                
                # Get the appropriate column
                col = [inv_col1, inv_col2, inv_col3][i % 3]
                
                with col:
                    # Create card-like container
                    with st.container():
                        # Card header with icon and risk badge
                        if investment_details:
                            risk_level = investment_details['Risk Level'].split(':')[0]  # Get first word (Very/Low/Medium/High)
                            risk_color = risk_colors.get(risk_level, "#6c757d")
                            
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                <div style="display: flex; align-items: center;">
                                    <span style="font-size: 24px; margin-right: 16px;">🪙</span>
                                    <h4 style="margin: 0; font-size: 16px; font-weight: bold;">{investment['name']}</h4>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: flex-start;">
                                <span style="background-color: {risk_color}; color: white; padding: 4px 6px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                                    {risk_level} Risk
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Investment description
                        if "ASB" in investment['name'] or "ASM" in investment['name']:
                            st.markdown("<p style='color: #6c757d; font-size: 14px; margin: 8px 0;'>Stable government-backed funds</p>", unsafe_allow_html=True)
                        elif "EPF" in investment['name']:
                            st.markdown("<p style='color: #6c757d; font-size: 14px; margin: 8px 0;'>Mandatory retirement savings fund</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='color: #6c757d; font-size: 14px; margin: 8px 0;'>Diversified investment option</p>", unsafe_allow_html=True)
                        
                        # Expected Return
                        with st.container(border=False):
                            if investment_details:
                                st.markdown(f"<p style='margin: 1px 0;'><strong>Expected Return</strong><br><span style='color: #28a745; font-size: 16px; font-weight: bold;'>{investment_details['Expected Returns (Annual)']}</span></p>", unsafe_allow_html=True)
                        
                        with st.container(border=False):
                            st.markdown(f"<p style='margin: 1px 0;'><strong>Recommended Amount</strong><br><span style='color: #000; font-size: 18px; font-weight: bold;'>RM{investment['amount']:,.0f}</span></p>", unsafe_allow_html=True)
                        
                        # Portfolio allocation bar
                        total_savings = sum(inv['amount'] for inv in investment_recommendations.values())
                        allocation_percent = (investment['amount'] / total_savings) * 100
                        
                        st.markdown(f"<p style='margin: 10px 0 4px 0; font-weight: bold;'>Portfolio Allocation</p>", unsafe_allow_html=True)
                        st.progress(allocation_percent / 100)
                        st.markdown(f"<p style='text-align: right; margin: 0; font-weight: bold; font-size: 16px;'>{allocation_percent:.0f}%</p>", unsafe_allow_html=True)
                
                total_amount += investment['amount']
            
            st.markdown(f"<h3 style='text-align: center;'>💰 Total Investment Amount: RM {total_amount:,.2f}</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("📈 Investment Growth Projection")
        investment_col1, investment_col2 = st.columns([2, 1])

        with investment_col1:
            years = len(next(iter(all_investments.values())))

            fig, ax = plt.subplots(figsize=(10, 10))

            for inv_name, fv_list in all_investments.items():
                ax.plot(range(1, years + 1), fv_list, marker='o', label=inv_name)

            ax.set_title("Investment Growth Over Time")
            ax.set_xlabel("Years")
            ax.set_ylabel("Future Value (RM)")
            ax.grid(True)
            ax.legend()

            st.pyplot(fig)

        with investment_col2:
            for inv_name, fv_list in all_investments.items():
                st.write(f"**📌 {inv_name}: RM {fv_list[0]:,.2f}**")
                st.write(f"💰 Future Value after {years} years: RM{fv_list[-1]:,.2f}")
                st.write(f"📈 Extra money earned from investment: RM{fv_list[-1]-fv_list[0]:,.2f}")
                st.write("")
                st.write("")
                st.write("")

else:
    st.info("👈 Please fill out the form in the sidebar to get started with your personalised financial plan!")

    with st.container(border=True):
        st.subheader("💰 Personalized Budget Plan")
        st.info("Complete the form to see your personalised budget allocation")
    
    with st.container(border=True):
        st.subheader("📈 Savings Projection Growth")
        st.info("Complete the form to see the savings growth projection")
    
    with st.container(border=True):
        st.subheader("🎯 Investment Recommendations")
        st.info("Complete the form to get personalised investment recommendations")
    
    with st.container(border=True):
        st.subheader("📈 Investment Growth Projection")
        st.info("Complete the form to see the investment growth projection")

# Chatbot
with st.expander("🤖💬 Chat with FinanceBot for Financial Advice"):
    st.markdown(
        """
        <style>
        /* Target the whole expander container */
        [data-testid="stExpander"] {
            border: 2px solid #01B8AA;
            border-radius: 8px;
            overflow: hidden;
        }

        /* Target the header (the part you click to expand/collapse) */
        [data-testid="stExpander"] > div:first-child {
            background-color: #01B8AA;
            color: white !important;
            font-weight: bold;
            padding: 8px 12px;
        }

        /* Target the content area inside the expander */
        [data-testid="stExpander"] div[data-testid="stExpanderContent"] {
            background-color: #f9f9f9;
            color: black;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write(f"🤖  Ask me anything about your budget or investment questions...")
    
    # Display chat history
    for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
        st.write(f"👤 **You:** {user_msg}")
        st.write(f"🤖 **FinanceBot:** {bot_msg}")
        st.divider()

    prompt = st.chat_input("Say something...")
    if prompt and st.session_state.user_data:
        with st.spinner("Thinking..."):
            bot_response = chat_with_financebot(prompt, st.session_state.user_data)
            st.session_state.chat_history.append((prompt, bot_response))
            
            # # Debugging: Print chat_history to terminal after append
            # print("=== st.session_state.chat_history ===")
            # for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
            #    print(f"Message {i+1}: User: {user_msg} | Bot: {bot_msg[:100]}...")  # Truncate bot response for brevity
            # print("==========================")

            st.rerun()
    elif prompt and not st.session_state.user_data:
        st.warning("Please fill out the form in the sidebar and submit first 😊")

# st.divider()

# # Expense Tracker 
# st.subheader("💸 Expense Tracker")

# # Add expense 
# with st.popover("➕ Add Expense", use_container_width=False):
#     with st.form("add_expense_form"):
#         date = st.date_input("Date", value=datetime.date.today())
#         description = st.text_input("Description")
#         amount = st.number_input("Amount (RM)", min_value=0.0, step=1.0)

#         submitted = st.form_submit_button("Save")
#         if submitted:
#             from categorizer import categorize_expense
#             category = categorize_expense(description)
#             firebase.add_expense(
#                 st.session_state.user_id,
#                 str(date),
#                 description,
#                 amount,
#                 category
#             )
#             st.success(f"✅ Expense added under **{category}**")
#             st.rerun()

# # Show expenses
# expenses = firebase.get_expenses(st.session_state.user_id)
# if expenses:
#     st.dataframe(expenses, use_container_width=True)
# else:
#     st.info("No expenses added yet. Use the ➕ Add Expense button to start.")