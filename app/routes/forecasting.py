from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
import os

forecasting_bp = Blueprint('forecasting', __name__)

@forecasting_bp.route('/')
@login_required
def index():
    datasets = current_user.datasets.all()
    return render_template('forecasting/hub.html', datasets=datasets, title='Predictive Central')

@forecasting_bp.route('/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def run_forecast(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    import pandas as pd
    df = pd.read_csv(file_path)
    columns = df.columns.tolist()
    
    if request.method == 'POST':
        date_col = request.form.get('date_col')
        target_col = request.form.get('target_col')
        periods = int(request.form.get('periods', 30))
        model_type = request.form.get('model_type', 'prophet')
        
        from ai_services.forecasting import ForecastingService
        service = ForecastingService(file_path)
        
        try:
            if model_type == 'prophet':
                plot_json, mape, rmse = service.run_prophet(date_col, target_col, periods)
            else:
                plot_json, mape, rmse = service.run_lstm(date_col, target_col, periods)
            
            # Persist results
            from app.models.user import ForecastResult
            from app import db
            result = ForecastResult(
                model_type=model_type,
                target_col=target_col,
                mape=float(mape),
                rmse=float(rmse),
                user=current_user,
                dataset=dataset
            )
            db.session.add(result)
            db.session.commit()
            
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('forecasting.run_forecast', dataset_id=dataset.id))
            
        return render_template('forecasting/forecast.html', 
                               dataset=dataset, 
                               plot_json=plot_json, 
                               mape=mape, 
                               rmse=rmse, 
                               target_col=target_col,
                               model_type=model_type)
        
    return render_template('forecasting/index.html', title='Forecasting', dataset=dataset, columns=columns)

@forecasting_bp.route('/report/<int:dataset_id>')
@login_required
def download_forecast_report(dataset_id):
    from app.models.user import Dataset, ForecastResult
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    latest_forecast = ForecastResult.query.filter_by(dataset_id=dataset.id).order_by(ForecastResult.timestamp.desc()).first()
    
    if not latest_forecast:
        flash('No forecast found for this dataset.', 'warning')
        return redirect(url_for('forecasting.run_forecast', dataset_id=dataset.id))
    
    from app.services.report_service import ReportService
    report_filename = f"Forecast_{dataset.id}.pdf"
    report_path = os.path.join(os.getcwd(), 'reports', report_filename)
    
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path))
        
    ReportService.generate_forecast_pdf(
        dataset.original_name,
        latest_forecast.model_type,
        latest_forecast.target_col,
        latest_forecast.mape,
        latest_forecast.rmse,
        report_path
    )
    
    return send_file(report_path, as_attachment=True)

