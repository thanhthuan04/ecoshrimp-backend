import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor

DATA_PATH = "archive/Aquaponds Dataset.csv"
MODEL_DIR = Path(__file__).resolve().parent.parent / "app" / "ai" / "models"

FEATURE_COLS = ["DO", "TEMP", "PH", "TURBIDITY"]
TARGET_COLS = ["future_DO", "future_TEMP", "future_PH", "future_TURBIDITY"]

def load_dataset() -> pd.DataFrame:
    print(f"Đang đọc dữ liệu từ {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["datetime"])
    return df.sort_values(["station", "datetime"])

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    print("Đang tính 4 chỉ số tương lai theo từng trạm...")
    for col in ["DO", "TEMP", "PH", "TURBIDITY"]:
        df[f"future_{col}"] = df.groupby("station")[col].shift(-1)
    return df.dropna(subset=FEATURE_COLS + TARGET_COLS)

def train_model(X_train, y_train) -> MultiOutputRegressor:
    base_estimator = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
    )
    model = MultiOutputRegressor(base_estimator)
    model.fit(X_train, y_train)
    return model

def evaluate(model, X_test, y_test) -> None:
    predictions = model.predict(X_test)
    for i, col in enumerate(TARGET_COLS):
        mae = mean_absolute_error(y_test.iloc[:, i], predictions[:, i])
        print(f"MAE {col}: {mae:.4f}")

def save_model(model: MultiOutputRegressor) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    version = datetime.now().strftime("%Y%m%d_%H%M")
    versioned_path = MODEL_DIR / f"pond_forecaster_xgb_{version}.pkl"
    latest_path = MODEL_DIR / "pond_forecaster_xgb_latest.pkl"

    for path in (versioned_path, latest_path):
        with open(path, "wb") as f:
            pickle.dump(model, f)

    print(f"Đã lưu model: {versioned_path.name} (và cập nhật bản latest dùng cho app)")
    return versioned_path

def main() -> None:
    df = build_features(load_dataset())

    X = df[FEATURE_COLS]
    y = df[TARGET_COLS]
    print(f"Tổng số mẫu huấn luyện: {len(X)} dòng.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Đang huấn luyện MultiOutputRegressor + XGBoost...")
    model = train_model(X_train, y_train)

    print("Đánh giá model trên tập test:")
    evaluate(model, X_test, y_test)

    save_model(model)

if __name__ == "__main__":
    main()