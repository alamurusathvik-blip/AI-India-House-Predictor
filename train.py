"""
India House Price Prediction — ML Training Pipeline
=====================================================
End-to-end pipeline: data loading, cleaning, feature engineering,
model training with hyperparameter tuning, evaluation, and artifact export.

Author : AI Assistant
Created: 2026-06-25
"""

from __future__ import annotations

import logging
import os
import time
import warnings
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import (
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_PATH: str = "data/India_House_Prices_ML_Ready_No_Blanks.xlsx"
SHEET_NAME: str = "ML_Ready"
MODEL_DIR: str = "models"
RANDOM_STATE: int = 42

# India geographic bounds
LAT_MIN, LAT_MAX = 6.0, 37.0
LON_MIN, LON_MAX = 68.0, 98.0


# ============================= DATA LOADING =================================
def load_data(path: str, sheet: str) -> pd.DataFrame:
    """Load the Excel dataset and return a DataFrame."""
    logger.info("Loading dataset from '%s' (sheet='%s') …", path, sheet)
    try:
        df: pd.DataFrame = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    except FileNotFoundError:
        logger.error("Dataset not found at '%s'.", path)
        raise
    logger.info("Loaded %d rows × %d columns.", len(df), len(df.columns))
    return df


# ============================= DATA CLEANING ================================
def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Execute the full cleaning pipeline and return the cleaned DataFrame
    together with a statistics dictionary.
    """
    stats: Dict[str, int] = {"original_rows": len(df)}
    logger.info("=" * 60)
    logger.info("DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    # 1. Remove exact duplicate rows ----------------------------------------
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    stats["duplicates_removed"] = removed
    logger.info("Step 1 — Duplicates removed: %d  |  Remaining: %d", removed, len(df))

    # 2. Standardize city names ----------------------------------------------
    df["city"] = df["city"].astype(str).str.strip().str.title()
    df["city"] = df["city"].replace({"Banglore": "Bangalore"})
    logger.info("Step 2 — City names standardized (Banglore → Bangalore).")

    # 3. Standardize location_name -------------------------------------------
    df["location_name"] = df["location_name"].astype(str).str.strip().str.title()
    logger.info("Step 3 — Location names standardized.")

    # 4. Fix coordinates -----------------------------------------------------
    #    Swap lat/lon when they look reversed, then drop out-of-India rows.
    swap_mask = (
        df["latitude"].between(LON_MIN, LON_MAX)
        & df["longitude"].between(LAT_MIN, LAT_MAX)
    )
    n_swapped = swap_mask.sum()
    df.loc[swap_mask, ["latitude", "longitude"]] = df.loc[
        swap_mask, ["longitude", "latitude"]
    ].values
    logger.info("Step 4a — Swapped reversed coordinates for %d rows.", n_swapped)

    before = len(df)
    valid_coords = df["latitude"].between(LAT_MIN, LAT_MAX) & df["longitude"].between(
        LON_MIN, LON_MAX
    )
    df = df[valid_coords].reset_index(drop=True)
    removed = before - len(df)
    stats["invalid_coordinates_removed"] = removed
    logger.info(
        "Step 4b — Invalid coordinates removed: %d  |  Remaining: %d", removed, len(df)
    )

    # 5. Remove extreme area outliers ----------------------------------------
    before = len(df)
    df = df[(df["area_sqft"] >= 100) & (df["area_sqft"] <= 50_000)].reset_index(
        drop=True
    )
    removed = before - len(df)
    stats["invalid_area_removed"] = removed
    logger.info(
        "Step 5 — Invalid area (<100 or >50000 sqft) removed: %d  |  Remaining: %d",
        removed,
        len(df),
    )

    # 6. Remove extreme bedrooms ---------------------------------------------
    before = len(df)
    df = df[df["bedrooms"] <= 10].reset_index(drop=True)
    removed = before - len(df)
    stats["extreme_bedrooms_removed"] = removed
    logger.info(
        "Step 6 — Extreme bedrooms (>10) removed: %d  |  Remaining: %d",
        removed,
        len(df),
    )

    # 7. Remove price outliers (1st–99th percentile) -------------------------
    before = len(df)
    p1 = df["price_value"].quantile(0.01)
    p99 = df["price_value"].quantile(0.99)
    df = df[df["price_value"].between(p1, p99)].reset_index(drop=True)
    removed = before - len(df)
    stats["price_outliers_removed"] = removed
    logger.info(
        "Step 7 — Price outliers removed (%.2f–%.2f): %d  |  Remaining: %d",
        p1,
        p99,
        removed,
        len(df),
    )

    stats["cleaned_rows"] = len(df)
    logger.info("-" * 60)
    logger.info(
        "Cleaning complete: %d → %d rows  (removed %d total)",
        stats["original_rows"],
        stats["cleaned_rows"],
        stats["original_rows"] - stats["cleaned_rows"],
    )
    logger.info("=" * 60)
    return df, stats


# ========================== FEATURE ENGINEERING =============================
def engineer_features(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, KMeans, Dict[str, float]]:
    """
    Create engineered features and return the enriched DataFrame,
    the fitted KMeans clusterer, and the premium-location-score map.
    """
    logger.info("FEATURE ENGINEERING")
    logger.info("-" * 60)

    # 1. bedroom_density -----------------------------------------------------
    df["bedroom_density"] = df["area_sqft"] / df["bedrooms"]
    logger.info("Created 'bedroom_density'.")

    # 2. geo_cluster (KMeans on lat/lon) -------------------------------------
    kmeans = KMeans(n_clusters=15, random_state=RANDOM_STATE, n_init=10)
    df["geo_cluster"] = kmeans.fit_predict(df[["latitude", "longitude"]]).astype(str)
    logger.info("Created 'geo_cluster' (KMeans, k=15).")

    # 3. area_category -------------------------------------------------------
    df["area_category"] = pd.cut(
        df["area_sqft"],
        bins=[0, 800, 1500, 2500, float("inf")],
        labels=["Small", "Medium", "Large", "Luxury"],
    )
    logger.info("Created 'area_category'.")

    # 4. premium_location_score ----------------------------------------------
    #    Mean price_per_sqft per location, MinMax-normalised to [0, 1].
    #    For locations with <3 samples, use the city-level mean instead.
    loc_counts = df.groupby("location_name")["price_per_sqft"].transform("count")
    city_means = df.groupby("city")["price_per_sqft"].transform("mean")

    loc_means = df.groupby("location_name")["price_per_sqft"].transform("mean")
    raw_score = np.where(loc_counts >= 3, loc_means, city_means)

    scaler = MinMaxScaler()
    df["premium_location_score"] = scaler.fit_transform(
        raw_score.reshape(-1, 1)
    ).ravel()

    # Build a lookup map (location_name → score) from the dataframe
    premium_score_map: Dict[str, float] = (
        df.groupby("location_name")["premium_location_score"].mean().to_dict()
    )
    logger.info("Created 'premium_location_score'.")
    logger.info("Feature engineering complete.\n")

    return df, kmeans, premium_score_map


# ====================== GROUP RARE LOCATIONS ================================
def group_rare_locations(df: pd.DataFrame, min_count: int = 5) -> pd.DataFrame:
    """Replace locations with fewer than *min_count* occurrences with 'Other'."""
    counts = df["location_name"].value_counts()
    rare = counts[counts < min_count].index
    n_rare = len(rare)
    df["location_name"] = df["location_name"].where(
        ~df["location_name"].isin(rare), other="Other"
    )
    logger.info(
        "Grouped %d rare locations (<%d samples) into 'Other'.", n_rare, min_count
    )
    return df


# ======================= BUILD PREPROCESSOR =================================
def build_preprocessor() -> ColumnTransformer:
    """Return an (unfitted) sklearn ColumnTransformer."""
    numeric_features: List[str] = [
        "latitude",
        "longitude",
        "bedrooms",
        "area_sqft",
        "bedroom_density",
        "premium_location_score",
    ]
    categorical_features: List[str] = ["city", "location_name", "area_category"]
    geo_feature: List[str] = ["geo_cluster"]

    numeric_transformer = Pipeline([("scaler", StandardScaler())])
    categorical_transformer = Pipeline(
        [("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True))]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features + geo_feature),
        ]
    )
    return preprocessor


# ======================= MODEL TRAINING =====================================
def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    preprocessor: ColumnTransformer,
) -> Tuple[Any, str, Dict[str, Dict[str, float]], Dict[str, dict]]:
    """
    Train four regressors, evaluate each, and return:
      (best_model, best_model_name, metrics_dict, hyperparams_dict)
    """
    logger.info("=" * 60)
    logger.info("MODEL TRAINING & EVALUATION")
    logger.info("=" * 60)

    # Fit the preprocessor on training data and transform
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # ------ Define models ---------------------------------------------------
    rf_param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [10, 15, 20, 25, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
    }

    xgb_param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [3, 5, 7, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "reg_alpha": [0, 0.1, 1],
        "reg_lambda": [1, 5, 10],
    }

    models: Dict[str, Any] = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomizedSearchCV(
            RandomForestRegressor(random_state=RANDOM_STATE),
            param_distributions=rf_param_dist,
            n_iter=20,
            cv=3,
            scoring="r2",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
        ),
        "XGBoost": RandomizedSearchCV(
            XGBRegressor(random_state=RANDOM_STATE, verbosity=0),
            param_distributions=xgb_param_dist,
            n_iter=20,
            cv=3,
            scoring="r2",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    metrics: Dict[str, Dict[str, float]] = {}
    hyperparams: Dict[str, dict] = {}
    best_r2: float = -np.inf
    best_model: Any = None
    best_model_name: str = ""

    for name, model in models.items():
        logger.info("Training %s …", name)
        t0 = time.time()
        model.fit(X_train_transformed, y_train)
        elapsed = time.time() - t0

        # If RandomizedSearchCV, unwrap best estimator
        fitted = model.best_estimator_ if hasattr(model, "best_estimator_") else model
        if hasattr(model, "best_params_"):
            hyperparams[name] = model.best_params_
            logger.info("  Best params: %s", model.best_params_)

        # Cross-validation on TRAINING set with fitted estimator
        cv_scores = cross_val_score(
            fitted, X_train_transformed, y_train, cv=5, scoring="r2", n_jobs=-1
        )

        # Test-set predictions
        y_pred = fitted.predict(X_test_transformed)
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))

        metrics[name] = {
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "cv_r2_mean": float(cv_scores.mean()),
            "cv_r2_std": float(cv_scores.std()),
        }

        logger.info(
            "  %s  —  MAE: %.2f | RMSE: %.2f | R²: %.4f | CV-R²: %.4f ± %.4f  (%.1fs)",
            name,
            mae,
            rmse,
            r2,
            cv_scores.mean(),
            cv_scores.std(),
            elapsed,
        )

        if r2 > best_r2:
            best_r2 = r2
            best_model = fitted
            best_model_name = name

    logger.info("-" * 60)
    logger.info("🏆 Best model: %s  (Test R² = %.4f)", best_model_name, best_r2)
    logger.info("=" * 60)

    return best_model, best_model_name, metrics, hyperparams


# ====================== FEATURE IMPORTANCE ==================================
def extract_feature_importance(
    model: Any, preprocessor: ColumnTransformer, top_n: int = 20
) -> List[Tuple[str, float]]:
    """
    Extract feature importances, aggregate one-hot features back to their
    original column name, and return the top-N as sorted (name, value) pairs.
    """
    feature_names: np.ndarray = preprocessor.get_feature_names_out()

    # Get raw importances
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)
    else:
        logger.warning("Model has no feature_importances_ or coef_.")
        return []

    # Map each transformed feature name back to original column name
    aggregated: Dict[str, float] = {}
    for fname, imp in zip(feature_names, importances):
        # Transformed names look like 'num__latitude' or 'cat__city_Mumbai'
        # Strip transformer prefix
        if "__" in fname:
            raw = fname.split("__", 1)[1]
        else:
            raw = fname

        # For one-hot encoded features, take part before the first '_' that
        # matches a known original column.  A more robust approach: check known
        # categorical columns.
        original_col = _map_to_original(raw)
        aggregated[original_col] = aggregated.get(original_col, 0.0) + float(imp)

    # Sort descending
    sorted_imp = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return sorted_imp


_KNOWN_CATEGORICALS = {"city", "location_name", "area_category", "geo_cluster"}
_KNOWN_NUMERICS = {
    "latitude",
    "longitude",
    "bedrooms",
    "area_sqft",
    "bedroom_density",
    "premium_location_score",
}


def _map_to_original(raw: str) -> str:
    """Map a transformed feature name back to the original column name."""
    # Numeric features keep their name through StandardScaler
    if raw in _KNOWN_NUMERICS:
        return raw
    # One-hot names are like 'city_Mumbai', 'geo_cluster_3', etc.
    for cat in _KNOWN_CATEGORICALS:
        if raw == cat or raw.startswith(cat + "_"):
            return cat
    return raw  # fallback


# ===================== BUILD METADATA =======================================
def build_metadata(
    df: pd.DataFrame,
    best_model_name: str,
    metrics: Dict[str, Dict[str, float]],
    feature_importance: List[Tuple[str, float]],
    cleaning_stats: Dict[str, int],
    kmeans: KMeans,
    premium_score_map: Dict[str, float],
    hyperparams: Dict[str, dict],
) -> Dict[str, Any]:
    """Assemble the training_metadata dictionary."""

    # city → sorted list of locations
    city_location_map: Dict[str, List[str]] = (
        df.groupby("city")["location_name"]
        .apply(lambda s: sorted(s.unique().tolist()))
        .to_dict()
    )

    # location_coords: 'city||location' → (mean_lat, mean_lon)
    location_coords: Dict[str, Tuple[float, float]] = {}
    for (city, loc), grp in df.groupby(["city", "location_name"]):
        key = f"{city}||{loc}"
        location_coords[key] = (float(grp["latitude"].mean()), float(grp["longitude"].mean()))

    metadata: Dict[str, Any] = {
        "best_model_name": best_model_name,
        "metrics": metrics,
        "feature_importance": feature_importance,
        "cleaning_stats": cleaning_stats,
        "dataset_stats": {
            "total_properties": int(len(df)),
            "cities_covered": int(df["city"].nunique()),
            "locations_covered": int(df["location_name"].nunique()),
            "avg_price": float(df["price_value"].mean()),
            "median_price": float(df["price_value"].median()),
            "model_accuracy": metrics[best_model_name]["r2"],
        },
        "city_location_map": city_location_map,
        "location_coords": location_coords,
        "geo_clusterer": kmeans,
        "premium_score_map": premium_score_map,
        "national_avg_price": float(df["price_value"].mean()),
        "national_avg_price_per_sqft": float(df["price_per_sqft"].mean()),
        "city_avg_prices": df.groupby("city")["price_value"].mean().to_dict(),
        "city_avg_price_per_sqft": df.groupby("city")["price_per_sqft"].mean().to_dict(),
        "feature_columns": [
            "city",
            "location_name",
            "latitude",
            "longitude",
            "bedrooms",
            "area_sqft",
            "bedroom_density",
            "geo_cluster",
            "area_category",
            "premium_location_score",
        ],
        "hyperparameters": hyperparams,
    }
    return metadata


# ======================== SAVE ARTIFACTS ====================================
def save_artifacts(
    model: Any,
    preprocessor: ColumnTransformer,
    metadata: Dict[str, Any],
    df: pd.DataFrame,
    model_dir: str = MODEL_DIR,
) -> None:
    """Persist trained artefacts to disk."""
    try:
        os.makedirs(model_dir, exist_ok=True)
    except OSError as exc:
        logger.error("Failed to create model directory: %s", exc)
        raise

    paths = {
        "model": os.path.join(model_dir, "model.pkl"),
        "preprocessor": os.path.join(model_dir, "preprocessor.pkl"),
        "metadata": os.path.join(model_dir, "training_metadata.pkl"),
        "data": os.path.join(model_dir, "cleaned_data.pkl"),
    }

    joblib.dump(model, paths["model"])
    logger.info("Saved best model       → %s", paths["model"])

    joblib.dump(preprocessor, paths["preprocessor"])
    logger.info("Saved preprocessor     → %s", paths["preprocessor"])

    joblib.dump(metadata, paths["metadata"])
    logger.info("Saved training metadata → %s", paths["metadata"])

    joblib.dump(df, paths["data"])
    logger.info("Saved cleaned data     → %s", paths["data"])


# ======================= PRINT SUMMARY ======================================
def print_summary(
    metrics: Dict[str, Dict[str, float]],
    best_model_name: str,
    feature_importance: List[Tuple[str, float]],
) -> None:
    """Print a formatted comparison table and feature-importance list."""
    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)
    header = f"{'Model':<25} {'MAE':>12} {'RMSE':>12} {'R²':>10} {'CV-R² (mean±std)':>20}"
    print(header)
    print("-" * 80)
    for name, m in metrics.items():
        marker = "  🏆" if name == best_model_name else ""
        print(
            f"{name:<25} {m['mae']:>12.2f} {m['rmse']:>12.2f} {m['r2']:>10.4f} "
            f"{m['cv_r2_mean']:>8.4f} ± {m['cv_r2_std']:<6.4f}{marker}"
        )
    print("=" * 80)

    print(f"\n🏆 Best Model: {best_model_name}  (Test R² = {metrics[best_model_name]['r2']:.4f})\n")

    print("TOP 20 FEATURE IMPORTANCES")
    print("-" * 45)
    for rank, (feat, imp) in enumerate(feature_importance, 1):
        bar = "█" * int(imp / feature_importance[0][1] * 30)
        print(f"  {rank:>2}. {feat:<30} {imp:.4f}  {bar}")
    print()


# ========================== MAIN ============================================
def main() -> None:
    """Orchestrate the full training pipeline."""
    t_start = time.time()

    # 1. Load ----------------------------------------------------------------
    df = load_data(DATA_PATH, SHEET_NAME)

    # 2. Clean ---------------------------------------------------------------
    df, cleaning_stats = clean_data(df)

    # 3. Feature engineering -------------------------------------------------
    df, kmeans, premium_score_map = engineer_features(df)

    # 4. Group rare locations ------------------------------------------------
    df = group_rare_locations(df, min_count=5)

    # 5. Prepare features & target -------------------------------------------
    feature_cols: List[str] = [
        "city",
        "location_name",
        "latitude",
        "longitude",
        "bedrooms",
        "area_sqft",
        "bedroom_density",
        "geo_cluster",
        "area_category",
        "premium_location_score",
    ]
    target_col: str = "price_value"

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # 6. Train/test split ----------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE
    )
    logger.info(
        "Train/test split: %d / %d  (80/20)", len(X_train), len(X_test)
    )

    # 7. Build preprocessor & train models -----------------------------------
    preprocessor = build_preprocessor()
    best_model, best_model_name, metrics, hyperparams = train_models(
        X_train, y_train, X_test, y_test, preprocessor
    )

    # 8. Feature importance --------------------------------------------------
    feature_importance = extract_feature_importance(best_model, preprocessor, top_n=20)

    # 9. Build metadata ------------------------------------------------------
    metadata = build_metadata(
        df,
        best_model_name,
        metrics,
        feature_importance,
        cleaning_stats,
        kmeans,
        premium_score_map,
        hyperparams,
    )

    # 10. Save ---------------------------------------------------------------
    save_artifacts(best_model, preprocessor, metadata, df)

    # 11. Summary ------------------------------------------------------------
    print_summary(metrics, best_model_name, feature_importance)

    elapsed = time.time() - t_start
    logger.info("Total runtime: %.1f seconds (%.1f minutes)", elapsed, elapsed / 60)
    print(f"⏱  Total runtime: {elapsed:.1f}s ({elapsed / 60:.1f} min)\n")


if __name__ == "__main__":
    main()
