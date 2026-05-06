from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inisialisasi SQLAlchemy
db = SQLAlchemy()

class HealthReport(db.Model):
    """
    Model ini merepresentasikan tabel 'health_report' di Amazon RDS.
    Digunakan untuk menyimpan data aspirasi dan pengaduan masyarakat.
    """
    __tablename__ = 'reports' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Report {self.title}>'