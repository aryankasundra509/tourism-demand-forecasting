import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

df = pd.read_csv("travel_data.csv")
print("Shape: ", df.shape)


# ── FEATURE SELECTION ────────────────────────────────
features = [
            "Month",           
            "Year",            
            "Is_Weekend",      
            "Season",          
            "Weather_Type",    
            "Zone",            
            "Place_Type",      
            "Tourist_Type",    
            "Ticket_Price",    
            "Google_Rating",
            "Review_Count_Lakhs"]

target = "Visitors_Count"

# ── DATA PREPARE ──────────────────────────────────────

X = df[features].copy()
y = df[target].copy()

print("X shape:", X.shape)
print("y shape:", y.shape)
print("\nX sample")
print(X.head(3))

# ── IS_WEEKEND CONVERT ────────────────────────────────

X["Is_Weekend"] = X["Is_Weekend"].map({"Yes": 1, "No": 0})
print("Weekend Unique Value:", X["Is_Weekend"].unique())


# ── LABEL ENCODING ────────────────────────────────────

cat_columns = ["Month", "Season", "Weather_Type", "Zone", "Place_Type", "Tourist_Type"]

encoders = {}

# All are encoded in alphabetics order (A=0, B=1, ...)
for col in cat_columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le
    print(f"{col}: {list(le.classes_)}")


# ── OUTLIER CAPPING ───────────────────────────────────
# 99th percentile se upar sab cap kar do

cap_value = y.quantile(0.99)
print(f"99th percentile: {cap_value:.0f}")

# Cap apply karo
y_capped = y.clip(upper=cap_value)

print(f"Before cap - Max: {y.max():.0f}")
print(f"After cap  - Max: {y_capped.max():.0f}")
print(f"Rows affected    : {(y > cap_value).sum()}")

# y ki jagah y_capped use karo
X_train, X_test, y_train, y_test = train_test_split(
    X, y_capped,        # ← y_capped use karo
    test_size=0.2,
    random_state=42
)

# Model same rahega
model = RandomForestRegressor(
    n_estimators=50,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_pred = np.clip(y_pred, 0, None)

mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print("=" * 40)
print(f"MAE      : {mae:.2f}")
print(f"R² Score : {r2:.4f}")
print("=" * 40)

# 10 rows check
test_sample = X_test.iloc[0:10]
predictions = model.predict(test_sample)
predictions = np.clip(predictions, 0, None)
actuals     = y_test.iloc[0:10].values

print(f"\n{'Predicted':>12} {'Actual':>10} {'Difference':>12}")
print("-" * 38)
for p, a in zip(predictions, actuals):
    diff = abs(p - a)
    print(f"{p:>12.0f} {a:>10.0f} {diff:>12.0f}")

# ── FINAL SAVE ────────────────────────────────────────
joblib.dump(model,    "model.pkl")
joblib.dump(encoders, "encoders.pkl")

# Cap value bhi save karo
# Page 5 mein visitor range dikhane ke liye
model_info = {
    "cap_value"   : cap_value,        # 2064
    "mae"         : mae,              # 109.36
    "r2"          : r2,               # 0.8065
    "features"    : features,         # feature list
    "risk_ranges" : {
        "Low"    : (8,   299),
        "Medium" : (300, 700),
        "High"   : (700, int(cap_value))
    }
}
joblib.dump(model_info, "model_info.pkl")

print("✅ model.pkl saved!")
print("✅ encoders.pkl saved!")
print("✅ model_info.pkl saved!")
print(f"\n📊 Final Model Summary:")
print(f"   R² Score : {r2:.4f}")
print(f"   MAE      : {mae:.2f} visitors")
print(f"   Cap Value: {cap_value:.0f} visitors")