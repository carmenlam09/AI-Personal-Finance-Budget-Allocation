import streamlit as st
import datetime
import uuid
from utils import firebase
from allocator import predict_allocation_50_30_20
import matplotlib.pyplot as plt
import plotly.express as px
from categorizer import categorize_expense

st.set_page_config(page_title="AI Personal Finance Model", layout="wide")

# ----------------- AUTH -----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.user_id is None:
    st.title("🔐 Login / Register")

    choice = st.radio("Select an option:", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            uid = str(uuid.uuid4())
            firebase.add_user(uid, username, password)
            st.success("✅ Account created! Please login.")

    if choice == "Login":
        if st.button("Login"):
            uid, user = firebase.get_user(username, password)
            if user:
                st.session_state.user_id = uid
                st.session_state.username = user["username"]
                # st.switch_page("pages/dashboard.py") 
                # st.rerun()
            else:
                st.error("❌ Invalid login.")

# ----------------- MAIN APP -----------------
else:
    # st.switch_page("pages/dashboard.py") 
    st.write("Hello")

    # with st.sidebar:
    #     st.title(":iphone: AI Personal Finance Budget Allocation Model")
    #     st.divider()

    #     st.subheader("Month to be Scheduled")
    #     year = st.date_input("Date", value=datetime.date.today())

    #     st.subheader("Monthly Income")
    #     income = st.number_input("Income (RM)", min_value=0.0, step=100.0)

    #     st.subheader("Age")
    #     age = st.number_input("Age", min_value=0, max_value=100, step=1, format="%d")

    #     st.subheader("State")
    #     state = st.selectbox(
    #         "Select State",
    #         (
    #             "W.P. Kuala Lumpur", "W.P. Putrajaya", "W.P. Labuan", "Perlis", "Kedah", "Kelantan",
    #             "Terengganu", "Perak", "Penang", "Pahang", "Selangor", "Melaka", 
    #             "Negeri Sembilan", "Johor", "Sabah", "Sarawak"
    #         ),
    #         index=None,
    #         placeholder="Select state"
    #     )

    #     st.subheader("Commitments")
    #     rent = st.number_input("Rent (RM)", min_value=0.0, step=50.0)
    #     debt = st.number_input("Debt (RM)", min_value=0.0, step=50.0)
    #     education = st.radio("Education Expenses", ["Yes", "No"], horizontal=True)
    #     subscription_services = st.number_input("Subscription Services (RM)", min_value=0.0, step=10.0)
        
    #     st.subheader("Additional Requirements")
    #     requirements = st.text_area("Please list additional requirements (optional)")

    #     submit = st.button("Generate Budget Allocation", type="primary")

    #     # Footer
    #     st.divider()
    #     if st.button("🚪 Logout", type="secondary", use_container_width=True):
    #         st.session_state.user_id = None
    #         st.session_state.username = None
    #         st.success("You have been logged out.")
    #         st.rerun()
            
    #     st.write("Made by:")
    #     st.image("logo.png", width=120)

    # # -------------------- MAIN LAYOUT -------------------- #
    # st.title("📊 AI Personal Finance Dashboard")

    # with st.expander("🤖💬 Chat with FinanceBot about the Budget Allocation"):
    #     st.write(f"🤖  Ask me anything about your budget: ")
    #     prompt = st.chat_input("Say something ...")
    #     if prompt:
    #         st.write(f"🤖 User has sent the following prompt: {prompt}")
    #         st.write("🤖 (AI Response coming soon...)")

    # row1_col1, row1_col2 = st.columns(2, border=True)
    # row2_col1, row2_col2 = st.columns(2, border=True)

    # # Budget Allocation 
    # with row1_col1:
    #     st.subheader("Personal Finance Budget Allocation")

    #     if submit:
    #         allocations, group_targets, fig1 = predict_allocation_50_30_20(
    #             age=age,
    #             salary=income,
    #             rent=rent,
    #             subscriptions=subscription_services,
    #             debt=debt,
    #             education=(education == "Yes")
    #         )

    #         st.success("✅ Budget Allocation Generated!")

    #         # Show allocations
    #         st.write("### 📌 Detailed Allocation")
    #         st.dataframe(allocations)

    #         st.write("### 📌 Group Allocation (50/30/20 Rule)")
    #         st.json(group_targets)

    #         # Show both pie charts
    #         st.write("### 📊 Allocation Chart")
    #         st.plotly_chart(fig1, use_container_width=True)

    # # Summary/Notes
    # with row1_col2:
    #     st.subheader("Summary / Notes")
    #     st.info("Your budget summary will appear here after allocation.")

    # # Savings Projection
    # with row2_col1:
    #     st.subheader("Saving Projection Growth")
    #     st.line_chart({"savings": [1000, 1200, 1300, 1400]})

    # # Investments Projection
    # with row2_col2:
    #     st.subheader("Investment Projection Growth")
    #     st.line_chart({"investments": [500, 700, 900, 1200]})

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