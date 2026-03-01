from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app, jsonify
from flask_login import login_required, current_user
import os

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def hub():
    from app.models.user import Dataset, ForecastResult, AIQueryLog, AnomalyLog
    datasets = current_user.datasets.order_by(Dataset.upload_date.desc()).all()
    # Summary stats for the hub
    total_rows = 0
    return render_template('analytics/hub.html', datasets=datasets, title='Analytics Hub')

@analytics_bp.route('/assistant-hub')
@login_required
def ai_assistant_hub():
    from app.models.user import Dataset
    datasets = current_user.datasets.order_by(Dataset.upload_date.desc()).all()
    return render_template('analytics/ai_assistant_hub.html', datasets=datasets, title='AI Assistant Hub')

@analytics_bp.route('/reports')
@login_required
def reports_hub():
    from app.models.user import Dataset
    datasets = current_user.datasets.order_by(Dataset.upload_date.desc()).all()
    return render_template('analytics/reports_hub.html', datasets=datasets, title='Reports Central')

@analytics_bp.route('/manage/<int:dataset_id>')
@login_required
def dataset_hub(dataset_id):
    from app.models.user import Dataset, ForecastResult, AIQueryLog, AnomalyLog
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('analytics.hub'))
    
    # Fetch activity for this specific dataset
    forecasts = ForecastResult.query.filter_by(dataset_id=dataset.id).all()
    queries = AIQueryLog.query.filter_by(dataset_id=dataset.id).all()
    anomalies = AnomalyLog.query.filter_by(dataset_id=dataset.id).all()
    
    return render_template('analytics/dataset_hub.html', 
                           dataset=dataset, 
                           forecasts=forecasts, 
                           queries=queries, 
                           anomalies=anomalies,
                           title=f'Manage: {dataset.original_name}')

@analytics_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{int(os.path.getmtime('.'))}_{filename}"
            file_path = os.path.join(os.getcwd(), 'uploads', unique_filename)
            file.save(file_path)
            
            from app.models.user import Dataset
            from app import db
            dataset = Dataset(filename=unique_filename, original_name=file.filename, owner=current_user)
            db.session.add(dataset)
            db.session.commit()
            
            flash('Dataset uploaded successfully!', 'success')
            return redirect(url_for('analytics.eda', dataset_id=dataset.id))
        else:
            flash('Invalid file type. Please upload a CSV.', 'danger')
            
    return render_template('analytics/upload.html', title='Upload Dataset')

@analytics_bp.route('/datasets')
@login_required
def list_datasets():
    datasets = current_user.datasets.all()
    return render_template('analytics/list.html', datasets=datasets, title='My Datasets')

@analytics_bp.route('/eda/<int:dataset_id>')
@login_required
def eda(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    from app.services.eda_service import EDAService
    service = EDAService(file_path)
    
    return render_template('analytics/eda.html', 
                           title='EDA - ' + dataset.original_name,
                           dataset=dataset,
                           preview_html=service.get_preview(),
                           health_report=service.get_data_health(),
                           insights=service.get_insights(),
                           row_count=service.df.shape[0],
                           col_count=service.df.shape[1],
                           corr_plot=service.get_correlations_plot(),
                           dist_plots=service.get_distribution_plots())

@analytics_bp.route('/report/<int:dataset_id>')
@login_required
def download_report(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    from app.services.eda_service import EDAService
    service = EDAService(file_path)
    
    from app.services.report_service import ReportService
    
    report_filename = f"Report_{dataset.id}.pdf"
    report_path = os.path.join(os.getcwd(), 'reports', report_filename)
    
    # Ensure reports folder exists
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path))
        
    insights = service.get_insights()
    summary_df = service.get_summary_df()
    health_report = service.get_data_health()
    
    ReportService.generate_pdf(dataset.original_name, insights, summary_df, health_report, report_path)
    
    return send_file(report_path, as_attachment=True)

@analytics_bp.route('/anomaly/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def anomaly_detection(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    import pandas as pd
    df = pd.read_csv(file_path)
    columns = df.select_dtypes(include=['number']).columns.tolist()
    
    if request.method == 'POST':
        target_col = request.form.get('target_col')
        method = request.form.get('method', 'isolation_forest')
        
        from ai_services.anomaly import AnomalyService
        service = AnomalyService(file_path)
        plot_json, summary = service.detect_anomalies(target_col, method)
        
        # Log anomalies
        from app.models.user import AnomalyLog
        from app import db
        log = AnomalyLog(
            target_col=target_col,
            method=method,
            anomaly_count=summary['total_anomalies'],
            user=current_user,
            dataset=dataset
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('analytics/anomaly_results.html', 
                               dataset=dataset, 
                               plot_json=plot_json, 
                               summary=summary, 
                               target_col=target_col)
        
    return render_template('analytics/anomaly_config.html', title='Anomaly Detection', dataset=dataset, columns=columns)

@analytics_bp.route('/nlp/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def nlp_query(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    from ai_services.nlp_query import NLPQueryService
    service = NLPQueryService(file_path)
    
    response = None
    question = None
    if request.method == 'POST':
        question = request.form.get('question')
        response = service.query(question)
        
        from app.models.user import AIQueryLog
        from app import db
        log = AIQueryLog(
            question=question,
            answer=response,
            user=current_user,
            dataset=dataset
        )
        db.session.add(log)
        db.session.commit()
    
    # Get recent history and suggestions
    from app.models.user import AIQueryLog
    history = AIQueryLog.query.filter_by(dataset_id=dataset.id).order_by(AIQueryLog.timestamp.asc()).all()
    suggestions = service.get_suggestions()
                
    return render_template('analytics/nlp_query.html', 
                           title='AI Assistant', 
                           dataset=dataset, 
                           response=response, 
                           question=question,
                           history=history,
                           suggestions=suggestions)

@analytics_bp.route('/automl/<int:dataset_id>', methods=['GET'])
@login_required
def run_automl(dataset_id):
    from app.models.user import Dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('analytics.hub'))
    
    file_path = os.path.join(os.getcwd(), 'uploads', dataset.filename)
    from ai_services.automl import AutoMLService
    
    try:
        service = AutoMLService(file_path)
        # We'll default to the first numerical column if not specified, 
        # but usually the user would pick one. For this trigger, we'll look for common targets or just first num.
        import pandas as pd
        df = pd.read_csv(file_path)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not num_cols:
            flash('No numerical columns found for AutoML.', 'warning')
            return redirect(url_for('analytics.dataset_hub', dataset_id=dataset.id))
            
        target_col = num_cols[-1] # Usually the last column is the target in many datasets
        leaderboard = service.run_automl(target_col)
        
        if isinstance(leaderboard, str): # Error message
            flash(leaderboard, 'danger')
            return redirect(url_for('analytics.dataset_hub', dataset_id=dataset.id))
            
        return render_template('analytics/automl_results.html', 
                               dataset=dataset, 
                               leaderboard=leaderboard, 
                               target_col=target_col)
    except Exception as e:
        flash(f"AutoML Error: {str(e)}", 'danger')
        return redirect(url_for('analytics.dataset_hub', dataset_id=dataset.id))