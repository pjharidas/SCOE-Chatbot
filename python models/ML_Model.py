import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load the dataset
df = pd.read_csv('python models/colleges.csv')

# Clean and preprocess
for col in ['Year', 'Round', 'Percentile']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(subset=['College', 'Year', 'Round', 'Branch', 'Category', 'Percentile'], inplace=True)
df.reset_index(drop=True, inplace=True)

def predict_cutoff_for_college_branch(data, college, branch, category, current_year):
    try:
        subset = data[
            (data['College'] == college) &
            (data['Branch'] == branch) &
            (data['Category'] == category)
        ]
        if subset.shape[0] < 3:
            return None, None

        # Model training
        X = subset[['Year', 'Round']]
        y = subset['Percentile']
        model = LinearRegression()
        model.fit(X, y)

        # Predict for current year using median round
        median_round = float(np.median(subset['Round']))
        X_new = pd.DataFrame([[current_year, median_round]], columns=['Year', 'Round'])
        predicted_cutoff = float(model.predict(X_new)[0])

        # Gather historical data (convert to pure Python float)
        historical_data = [
            {
                'Year': float(row['Year']),
                'Round': float(row['Round']),
                'Percentile': float(row['Percentile'])
            }
            for _, row in subset[['Year', 'Round', 'Percentile']].sort_values(by=['Year', 'Round']).iterrows()
        ]

        return round(predicted_cutoff, 2), historical_data

    except Exception as e:
        return None, None

def get_college_recommendations(data, category, user_percentile, current_year):
    recommendations = []
    colleges = data['College'].unique()

    for college in colleges:
        branches = data[data['College'] == college]['Branch'].unique()
        for branch in branches:
            predicted_cutoff, history = predict_cutoff_for_college_branch(data, college, branch, category, current_year)
            if predicted_cutoff is not None and user_percentile >= predicted_cutoff:
                recommendations.append({
                    'College': college,
                    'Branch': branch,
                    'Category': category,
                    'Historical_Cutoffs': history,
                    'Predicted_Cutoff': predicted_cutoff
                })

    return recommendations

# Example usage
# user_category = "SC"
# user_percentile = 60
# current_year = 2025

# recommendations = get_college_recommendations(df, user_category, user_percentile, current_year)
# recommendations
# print(recommendations)
# Example output    