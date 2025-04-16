#!/usr/bin/env python3
"""
predict_cutoffs.py

Train a gradient-boosted model to predict college cutoff percentiles,
and generate recommendations based on a user’s percentile.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor
import argparse
import json

def load_and_clean(csv_path):
    df = pd.read_csv(csv_path)
    # numeric conversion
    for col in ['Year', 'Round', 'Percentile']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # drop incomplete rows
    df.dropna(subset=['College', 'Branch', 'Category', 'Year', 'Round', 'Percentile'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Standardize category column to uppercase
    df['Category'] = df['Category'].str.strip().str.upper()
    return df

def build_pipeline():
    num_feats = ['Year', 'Round']
    cat_feats = ['College', 'Branch', 'Category']

    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), num_feats),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_feats),

    ])

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    pipe = Pipeline([
        ('prep', preprocessor),
        ('xgb', model),
    ])

    return pipe

def cross_validate(df, pipe, n_splits=5):
    # group by college|branch|category so future years aren't in both train/test
    df['Group'] = df['College'] + '|' + df['Branch'] + '|' + df['Category']
    groups = df['Group']
    gkf = GroupKFold(n_splits=n_splits)
    scores = cross_val_score(
        pipe,
        df[['Year','Round','College','Branch','Category']],
        df['Percentile'],
        groups=groups,
        cv=gkf,
        scoring='neg_mean_absolute_error',
        n_jobs=-1
    )
    print(f"CV MAE: {-np.mean(scores):.3f} ± {np.std(scores):.3f}")

def fit_full(df, pipe):
    pipe.fit(
        df[['Year','Round','College','Branch','Category']],
        df['Percentile']
    )
    return pipe

def predict_cutoff(pipe, college, branch, category, year, median_round):
    X_new = pd.DataFrame([{
        'Year': year,
        'Round': median_round,
        'College': college,
        'Branch': branch,
        'Category': category
    }])
    pred = pipe.predict(X_new)[0]
    # Ensure predicted percentile is within 0 and 100
    pred = np.clip(pred, 0, 100)
    return float(pred)

def get_recommendations(df, pipe, category, user_pct, current_year):
    recs = []
    # precompute median rounds per group
    medians = df.groupby(['College','Branch','Category'])['Round'].median().to_dict()

    for (college, branch) in df[['College','Branch']].drop_duplicates().values:
        key = (college, branch, category)
        if key not in medians:
            continue
        subset = df[
            (df.College==college)&
            (df.Branch==branch)&
            (df.Category==category)
        ]
        if len(subset) < 3:
            continue

        median_round = float(medians[key])
        pred = predict_cutoff(pipe, college, branch, category, current_year, median_round)

        if user_pct >= pred:
            history = subset.sort_values(['Year','Round'])[['Year','Round','Percentile']]\
                            .to_dict(orient='records')
            recs.append({
                'College': college,
                'Branch': branch,
                'Category': category,
                'Predicted_Cutoff': round(pred,2),
                'Historical_Cutoffs': history
            })
    return recs

def main():
    parser = argparse.ArgumentParser(
        description="Train cutoff predictor and generate recommendations."
    )
    
    parser.add_argument('--user_percentile', type=float, required=True,
                        help="Your percentile for recommendations")
    parser.add_argument('--category', type=str, required=True,
                        help="Category (e.g. OBC, SC, GEN)")
    parser.add_argument('--output', type=str,
                        help="(optional) Path to save recommendations JSON")
    args = parser.parse_args()

    # 1. Load & clean
    df = load_and_clean("colleges.csv")

    # 2. Build pipeline
    pipe = build_pipeline()

    # 3. Cross-validate
    cross_validate(df, pipe)

    # 4. Fit on full data
    pipe = fit_full(df, pipe)

    # 5. Generate recommendations
    recs = get_recommendations(df, pipe, args.category, args.user_percentile, 2025)

    # 6. Output
    print(f"\nFound {len(recs)} recommendations for category={args.category}, "
          f"user_percentile={args.user_percentile}\n")
    for r in recs:
        print(f"{r['College']} - {r['Branch']}: Predicted cutoff = {r['Predicted_Cutoff']}")
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(recs, f, indent=2)
        print(f"\nRecommendations saved to {args.output}")

if __name__ == '__main__':
    main()
