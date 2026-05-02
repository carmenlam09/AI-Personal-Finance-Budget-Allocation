import streamlit as st
import matplotlib.pyplot as plt

# --- Inputs ---
recommended_investment = st.number_input("Recommended Investment (RM)", value=10000)
expected_return = st.slider("Expected Annual Return (%)", 0.0, 0.20, 0.06)
years = st.number_input("Investment Horizon (Years)", min_value=1, max_value=50, value=10)

# --- Calculate Future Value Year by Year ---
fv_per_year = []
amount = recommended_investment
for year in range(1, years + 1):
    amount *= (1 + expected_return)
    fv_per_year.append(amount)

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(1, years + 1), fv_per_year, marker='o', linestyle='-')
ax.set_title("Investment Growth Over Time")
ax.set_xlabel("Years")
ax.set_ylabel("Future Value (RM)")
ax.grid(True)

# Show chart in Streamlit
st.pyplot(fig)

# Show final future value and extra earned
st.write(f"💰 Future Value after {years} years: RM{fv_per_year[-1]:,.2f}")
st.write(f"📈 Extra money earned from investment: RM{fv_per_year[-1]-recommended_investment:,.2f}")
