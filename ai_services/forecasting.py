import pandas as pd
from prophet import Prophet
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import os

class ForecastingService:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def run_prophet(self, date_col, target_col, periods=30):
        try:
            # Prepare data for Prophet
            df_prophet = self.df[[date_col, target_col]].copy()
            df_prophet.columns = ['ds', 'y']
            df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
        except Exception as e:
            raise ValueError(f"Could not parse '{date_col}' as a date column. Please ensure it contains date values.")
        
        # Initialize and fit
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
        model.fit(df_prophet)
        
        # Forecast
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Evaluation (on training data for simplicity in this version)
        y_true = df_prophet['y']
        y_pred = forecast.iloc[:len(df_prophet)]['yhat']
        mape = mean_absolute_percentage_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        
        # Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name='Actual', mode='lines'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', mode='lines'))
        fig.add_trace(go.Scatter(
            x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
            y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False,
            name='Confidence Interval'
        ))
        
        fig.update_layout(title="Prophet Forecast", xaxis_title="Date", yaxis_title=target_col)
        
        return fig.to_json(), mape, rmse

    def run_lstm(self, date_col, target_col, periods=30):
        # LSTM implementation (simplified version for this structure)
        # In a real scenario, this would involve scaling, windowing, and training a Keras model
        # For this prototype, we'll implement a simplified trend-following prediction to demonstrate the UI
        try:
            df_lstm = self.df[[date_col, target_col]].copy()
            df_lstm[date_col] = pd.to_datetime(df_lstm[date_col])
            df_lstm = df_lstm.sort_values(by=date_col)
        except Exception as e:
            raise ValueError(f"Could not parse '{date_col}' as a date column. Please ensure it contains date values.")
        
        # Just a mock LSTM trend for now as full LSTM training is resource intensive for a web request
        y = df_lstm[target_col].values
        last_val = y[-1]
        trend = (y[-1] - y[0]) / len(y)
        
        # Calculate mock metrics based on trend fit
        y_pred_train = np.array([y[0] + i*trend for i in range(len(y))])
        mape = float(mean_absolute_percentage_error(y, y_pred_train))
        rmse = float(np.sqrt(mean_squared_error(y, y_pred_train)))
        
        future_dates = pd.date_range(start=df_lstm[date_col].iloc[-1] + pd.Timedelta(days=1), periods=periods)
        predictions = [last_val + (i+1)*trend for i in range(periods)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_lstm[date_col], y=df_lstm[target_col], name='Historical'))
        fig.add_trace(go.Scatter(x=future_dates, y=predictions, name='LSTM Prediction', line=dict(dash='dash')))
        fig.update_layout(title="LSTM Forecast (Simulated)", xaxis_title="Date", yaxis_title=target_col)
        
        return fig.to_json(), mape, rmse
