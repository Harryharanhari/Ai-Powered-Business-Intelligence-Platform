import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

class AutoMLService:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def run_automl(self, target_col):
        # Prepare data
        df_clean = self.df.select_dtypes(include=['number']).dropna()
        if target_col not in df_clean.columns:
            return "Target column must be numerical for this prototype."

        X = df_clean.drop(columns=[target_col])
        y = df_clean[target_col]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            "Random Forest": RandomForestRegressor(),
            "Gradient Boosting": GradientBoostingRegressor(),
            "Linear Regression": LinearRegression()
        }
        
        results = []
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = r2_score(y_test, preds)
            results.append({"model": name, "r2_score": score})
            
        # Return leaderboard sorted by score
        leaderboard = sorted(results, key=lambda x: x['r2_score'], reverse=True)
        return leaderboard
