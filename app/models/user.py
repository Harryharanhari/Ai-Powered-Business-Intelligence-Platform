from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    datasets = db.relationship('Dataset', backref='owner', lazy='dynamic')
    forecasts = db.relationship('ForecastResult', backref='user', lazy='dynamic')
    queries = db.relationship('AIQueryLog', backref='user', lazy='dynamic')
    anomalies = db.relationship('AnomalyLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128))
    original_name = db.Column(db.String(128))
    upload_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    forecasts = db.relationship('ForecastResult', backref='dataset', lazy='dynamic')
    queries = db.relationship('AIQueryLog', backref='dataset', lazy='dynamic')
    anomalies = db.relationship('AnomalyLog', backref='dataset', lazy='dynamic')

class ForecastResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(32))
    target_col = db.Column(db.String(64))
    mape = db.Column(db.Float)
    rmse = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))

class AIQueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))

class AnomalyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_col = db.Column(db.String(64))
    method = db.Column(db.String(32))
    anomaly_count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
