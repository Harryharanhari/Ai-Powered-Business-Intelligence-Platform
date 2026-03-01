import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

class EDAService:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def get_preview(self):
        return self.df.head(10).to_html(classes='table table-striped table-hover', index=False)

    def get_data_health(self):
        """Perform a Data Quality & Health Audit"""
        health_report = {
            'total_rows': len(self.df),
            'total_cols': len(self.df.columns),
            'duplicate_rows': int(self.df.duplicated().sum()),
            'missing_cells': int(self.df.isnull().sum().sum()),
            'missing_percentage': float((self.df.isnull().sum().sum() / self.df.size) * 100),
            'columns': []
        }
        
        for col in self.df.columns:
            health_report['columns'].append({
                'name': col,
                'dtype': str(self.df[col].dtype),
                'missing': int(self.df[col].isnull().sum()),
                'unique': int(self.df[col].nunique()),
                'constant': bool(self.df[col].nunique() <= 1)
            })
        return health_report

    def get_summary_stats(self):
        return self.df.describe().reset_index().to_html(classes='table table-bordered table-sm', index=False)

    def get_summary_df(self):
        return self.df.describe().reset_index()

    def get_correlations_plot(self):
        numerical_df = self.df.select_dtypes(include=['number'])
        if numerical_df.empty or len(numerical_df.columns) < 2:
            return None
        corr = numerical_df.corr()
        fig = px.imshow(
            corr, 
            text_auto=".2f", 
            aspect="auto", 
            title="Correlation Heatmap (Feature Dependencies)", 
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        return fig.to_json()

    def get_distribution_plots(self):
        plots = []
        # Intelligent Selection: Pick numerical columns with highest variance/entropy
        numerical_cols = self.df.select_dtypes(include=['number'])
        if numerical_cols.empty:
            return []
            
        # Select top 6 columns with most unique values (proxy for interest)
        selected_cols = numerical_cols.nunique().sort_values(ascending=False).index[:6]
        
        for col in selected_cols:
            fig = px.histogram(
                self.df, x=col, 
                title=f"Distribution & Outliers: {col}", 
                marginal="box",
                color_discrete_sequence=['#636EFA']
            )
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            plots.append({'name': col, 'json': fig.to_json()})
        return plots

    def get_insights(self):
        insights = []
        # Executive AI Insights
        insights.append(f"Capacity: {self.df.shape[0]} records analyzed across {self.df.shape[1]} descriptors.")
        
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            insights.append(f"Attention Required: {duplicates} duplicate rows detected in the source data.")
            
        missing_count = self.df.isnull().sum().sum()
        if missing_count > 0:
            insights.append(f"Data Gaps: {missing_count} null intersections found. Cleaning recommended for ML stability.")
        else:
            insights.append("Data Integrity: No missing values detected in the primary dataset.")
            
        num_cols = self.df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
            # Simple correlation insight
            if len(num_cols) >= 2:
                corr = self.df[num_cols].corr().unstack().sort_values(ascending=False)
                strongest = corr[corr < 1].index[0]
                if corr[strongest] > 0.7:
                    insights.append(f"Strong Driver: Found significant correlation between {strongest[0]} and {strongest[1]} ({corr[strongest]:.2f}).")
            
        return insights
