import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go

class AnomalyService:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def detect_anomalies(self, target_col, method='isolation_forest', contamination=0.05):
        data = self.df[[target_col]].copy()
        data = data.ffill().bfill()
        
        if method == 'isolation_forest':
            model = IsolationForest(contamination=contamination, random_state=42)
            data['anomaly_score'] = model.fit_predict(data[[target_col]])
            data['is_anomaly'] = data['anomaly_score'] == -1
            explanation = f"Isolation Forest identified outliers by isolating them based on {target_col} deviations."
        else:
            # Z-score method
            mean = data[target_col].mean()
            std = data[target_col].std()
            data['z_score'] = (data[target_col] - mean) / std
            data['is_anomaly'] = np.abs(data['z_score']) > 3
            explanation = f"Z-Score method flagged points more than 3 standard deviations from the mean of {target_col}."
            
        anomalies = data[data['is_anomaly']]
        
        # Professional Plotly with Shaded Confidence
        fig = go.Figure()
        
        # Add normal line
        fig.add_trace(go.Scatter(
            x=self.df.index, y=self.df[target_col], 
            name='Historical Data', 
            mode='lines',
            line=dict(color='#2c3e50', width=1.5)
        ))
        
        # Add anomaly markers
        fig.add_trace(go.Scatter(
            x=anomalies.index, 
            y=anomalies[target_col], 
            name='Detected Anomaly', 
            mode='markers', 
            marker=dict(
                color='#e74c3c', 
                size=12, 
                symbol='circle-open',
                line=dict(width=2)
            ),
            hovertemplate="Index: %{x}<br>Value: %{y}<br>Status: ANOMALOUS<extra></extra>"
        ))
        
        fig.update_layout(
            title=f"Anomaly Intelligence: {target_col}", 
            xaxis_title="Timeline Index", 
            yaxis_title="Measured KPI",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Detect significant anomalies for the results page
        sig_anomalies = anomalies.tail(5).index.tolist()
        
        summary = {
            'total_anomalies': int(data['is_anomaly'].sum()),
            'anomaly_percentage': float(data['is_anomaly'].mean() * 100),
            'method_used': method,
            'explanation': explanation,
            'significant_indices': sig_anomalies
        }
        
        return fig.to_json(), summary
