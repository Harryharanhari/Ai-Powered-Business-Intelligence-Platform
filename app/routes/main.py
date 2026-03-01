from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from app.models.user import Dataset, ForecastResult, AIQueryLog, AnomalyLog
    
    # Calculate real-time stats
    dataset_count = current_user.datasets.count()
    forecast_count = current_user.forecasts.count()
    query_count = current_user.queries.count()
    
    # Total anomalies across all datasets for this user
    anomaly_total = db.session.query(func.sum(AnomalyLog.anomaly_count)).filter(AnomalyLog.user_id == current_user.id).scalar() or 0
    
    recent_datasets = current_user.datasets.order_by(Dataset.upload_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           title='Dashboard', 
                           recent_datasets=recent_datasets,
                           stats={
                               'datasets': dataset_count,
                               'forecasts': forecast_count,
                               'queries': query_count,
                               'anomalies': anomaly_total
                           })
