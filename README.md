# 📊 AI Personal Finance Assistant

This project was developed for the **Malaysia Data Innovation Talent x DOSM Datathon 2025**.

---

## 👥 Group Members
- Tang Yuen Yin  
- Wan Nur Syarina binti Wan Ja'afar  
- Aireen Elzahraa binti Ahmad Aljafri   
- Carmen Lam Kah Man

---

## 📌 Project Overview
This project focuses on delivering **data-driven financial planning solutions for Malaysian youth**, combining both macro-level insights and micro-level personalized recommendations.

The full solution consists of:
- 📊 **Power BI Dashboard** – Macro-level analysis and insights  
- 🌐 **Streamlit Application** – Micro-level personalized financial assistant  

> ⚠️ **Note:** This GitHub repository contains only the **Streamlit application** component.

---

## 🚀 Streamlit Application (Micro-Level Solution)

This interactive web application translates macroeconomic insights into **actionable, personalized financial guidance**.

🔗 **Live Demo:**  
https://ai-personal-finance-budget-allocation-dosm.streamlit.app/

---

## 💡 Key Features

### 1. 💰 Budget Allocation Engine
- Generates optimized monthly budget distribution  
- Based on user inputs (income, age, state, commitments)  
- Follows the **50/30/20 rule** for financial balance
  
**ML Enhancements:**
- 📊 Uses **XGBoost regression (multi-output model)** to predict spending distribution across categories
- 🔍 Learns spending patterns from synthetic financial data (income, demographics, cost of living)  
- ⚖️ Combines model predictions with rule-based constraints to ensure realistic allocations
  
---

### 2. 📈 Savings & Investment Projection
- Simulates **year-by-year financial growth**  
- Models:
  - Monthly savings accumulation  
  - Investment growth using compound interest  

- Benchmarks against Malaysian retirement targets:
  - Basic: RM390,000  
  - Adequate: RM650,000  
  - Enhanced: RM1,300,000  

- Provides estimated timeline to reach financial goals  

---

### 3. 🧠 Personalized Financial Guidance
- Recommends suitable investment options such as:
  - EPF (Employees Provident Fund)  
  - ASB (Amanah Saham Bumiputera)  
  - Unit Trusts  

- Provides:
  - Recommended allocation  
  - Expected returns  

**AI Assistant:**
- 🤖 Context-aware chatbot for real-time financial advice  
- 💬 Answers user-specific queries  
- 🎯 Delivers personalized financial tips  

---

## 🧠 Technical Highlights

### 📊 Data
- Synthetic dataset (2000 profiles) simulating Malaysian financial behavior  
- Includes:
  - Income distribution  
  - State-level cost of living  
  - Age-based income progression  
  - Spending patterns  

### 🤖 Machine Learning
- Model: **XGBoost Regressor (MultiOutputRegressor)**  
- Feature engineering:
  - Numerical scaling (income, expenses)  
  - Categorical encoding (age group, state)  
- Pipeline-based architecture for training and inference

### 📈 Analytics Approach
- Hybrid system:
  - **Predictive** → ML-based allocation  
  - **Prescriptive** → Financial rules (50/30/20)  
- Ensures both personalization and financial discipline  

### 🌐 Application
- Built with **Streamlit** for interactive user experience  
- Integrated with **LLM APIs** for chatbot recommendations  

---

## 🎯 Objectives

To empower Malaysian youth with:
- Better budgeting strategies  
- Long-term financial planning tools  
- Data-driven investment decisions  

---

## 📊 About the Full Solution
In addition to this application, the complete project includes a **Power BI interactive dashboard** built using real-world datasets from **OpenDOSM** and **eStatistik**.

The dashboard provides:
- Macro-level financial trends  
- Socioeconomic insights  
- Data storytelling for policy and decision-making  
