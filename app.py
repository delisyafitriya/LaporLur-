import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, HealthReport  # Pastikan di models.py kolomnya sesuai
from s3_utils import upload_to_s3
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Gunakan secret key dari .env untuk keamanan
app.secret_key = os.getenv("SECRET_KEY", "laporlur-secret-key-2026")

# 1. Konfigurasi Database RDS (Pastikan DATABASE_URL sudah benar di .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Pastikan tabel dibuat di RDS saat aplikasi pertama kali jalan
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET"])
def index():
    # Mengambil semua laporan untuk ditampilkan di feed sebelah kanan
    # Variabel 'reports' harus sama dengan yang dipanggil di loop HTML {% for report in reports %}
    reports = HealthReport.query.order_by(HealthReport.created_at.desc()).all()
    
    # Ambil URL CloudFront untuk keperluan file statis jika diperlukan
    cf_url = os.getenv("CLOUDFRONT_URL") 
    return render_template("index.html", reports=reports, cloudfront_url=cf_url)

@app.route("/submit", methods=["POST"])
def submit_report():
    # 2. Sinkronisasi dengan atribut 'name' pada form HTML
    # Di HTML kita pakai: name="title", name="description", name="photo"
    title = request.form.get("title") 
    description = request.form.get("description")
    photo = request.files.get("photo")

    if photo:
        # 3. Penamaan file unik untuk mencegah bentrok di S3
        filename = f"laporlur-{uuid.uuid4()}-{photo.filename}"
        
        try:
            # 4. Integrasi S3 & CloudFront (PENTING!)
            # Fungsi upload_to_s3 harus mengembalikan URL CloudFront, bukan URL S3
            photo_url = upload_to_s3(photo, filename)
            
            # Simpan data ke RDS
            new_report = HealthReport(
                title=title,                # Pastikan kolom di models.py juga bernama 'title'
                description=description,    # Pastikan kolom di models.py juga bernama 'description'
                image_url=photo_url,        # URL hasil upload_to_s3
                status="Pending"            # Status default sesuai kriteria tugas
            )
            
            db.session.add(new_report)
            db.session.commit()
            flash("Laporan berhasil terkirim ke sistem Cloud!", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal mengirim laporan: {str(e)}", "danger")
    else:
        flash("Mohon lampirkan foto bukti laporan.", "warning")
        
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Host 0.0.0.0 wajib agar bisa diakses dari dalam Docker Container di ECS
    app.run(host="0.0.0.0", port=5000)