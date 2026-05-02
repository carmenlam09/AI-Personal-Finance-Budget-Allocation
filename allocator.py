import os
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import joblib

CSV_PATH = "synthetic_data.csv" 
MODEL_PATH = "allocator_pipeline.joblib"

df = pd.read_csv(CSV_PATH)
print("allocator.py: dataset columns =", list(df.columns))

# Features & targets
numeric_features = ["Income", "Housing", "Subscription"]
categorical_features = ["AgeGroup", "State"]

exclude = set(numeric_features + categorical_features + ["PLI", "SavingsRate"])
target_columns = [c for c in df.columns if c not in exclude]

print("allocator.py: target columns =", target_columns)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
    ],
    remainder="drop",
)

xgb = XGBRegressor(
    objective="reg:squarederror",
    n_estimators=500,   
    max_depth=6,       
    learning_rate=0.05, 
    subsample=0.8,      
    colsample_bytree=0.8, 
    n_jobs=-1,
    random_state=42
)

pipeline = Pipeline([
    ("pre", preprocessor),
    ("model", MultiOutputRegressor(xgb))
])

if os.path.exists(MODEL_PATH):
    print("Loading saved pipeline from", MODEL_PATH)
    pipeline = joblib.load(MODEL_PATH)
else:
    print("Training pipeline on dataset...")
    X = df[numeric_features + categorical_features]
    y = df[target_columns].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)
    joblib.dump(pipeline, MODEL_PATH)
    print("Training complete — pipeline saved to", MODEL_PATH)


def predict_allocation_50_30_20(age_group, salary, housing, subscriptions, state, debt=0, education=True):
    """
    Predicts budget allocation given user inputs.
    """

    # input row
    input_row = pd.DataFrame([{
        "AgeGroup": age_group,
        "Income": salary,
        "Housing": housing,
        "Subscription": subscriptions,
        "State": state
    }])

    # Predict
    preds = pipeline.predict(input_row)[0]
    alloc_series = pd.Series(preds, index=target_columns).clip(lower=0)

    # Groups
    groups = {
        "Needs": ["Housing", "Food", "Transport", "Health"],
        "Wants": ["Subscription", "Restaurants", "Clothing", "Fitness", "Others"],
        "Financial Future": ["Savings"]
    }

    # Group targets (50/30/20 rule)
    group_targets = {
        "Needs": 0.5 * salary,
        "Wants": 0.3 * salary,
        "Financial Future": 0.2 * salary
    }

    # Final allocation (distribute within each group)
    final_alloc = {}
    for group, items in groups.items():
        group_budget = group_targets[group]
        preds_for_items = [alloc_series.get(item, 0.0) for item in items]

        if sum(preds_for_items) > 0:
            distrib = (np.array(preds_for_items) / sum(preds_for_items)) * group_budget
        else:
            distrib = np.zeros(len(items))

        for item, val in zip(items, distrib):
            final_alloc[item] = round(float(val), 2)

    final_alloc["Housing"] = housing
    final_alloc["Subscription"] = subscriptions

    allocation_df = pd.DataFrame({
    "Category": list(final_alloc.keys()),
    "Amount": list(final_alloc.values())
    })
    allocation_df["Pct"] = (allocation_df["Amount"] / salary * 100).round(2)

    # pie chart
    fig = px.pie(
        allocation_df,
        names="Category",
        values="Amount",
        title="",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo="percent+label", pull=[0.02]*len(allocation_df))

    return allocation_df, group_targets, fig