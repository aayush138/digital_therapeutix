from flask import Blueprint, render_template, session, redirect, url_for, flash, g, request, jsonify, make_response, send_file
from app.models.user import User, db
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime, timezone
from app.utils.quintx.quint_analysis import run_quint_analysis
import os


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.before_request
def restrict_blocked_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_blocked:
            session.clear()
            flash("Your account is blocked. Please contact support.", "danger")
            return redirect(url_for('auth.login'))
        g.doctor_user = session.get('doctor_name', 'Doctor')
        g.license_number = session.get('license_number', '#000000')


@dashboard_bp.route('/user/details')
def user_details():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'preferred_name': user.preferred_name,
        'email': user.email,
        'backup_email': user.backup_email,
        'phone_number': user.phone_number,
        'register_date': user.registered_at.strftime('%Y-%m-%d') if user.registered_at else '',
        'clinic_name': user.clinic_name,
        'clinic_email': user.clinic_email,
        'address_street': user.address_street,
        'address_city': user.address_city,
        'address_state': user.address_state,
        'address_zip': user.address_zip,
        'address_country': user.address_country,
        'license_number': user.license_number,
        'license_country': user.license_country,
        'medical_degree': user.medical_degree,
        'specialty': user.specialty,
        'subspecialty': user.subspecialty,
        'current_employer': user.current_employer,
        'is_blocked': user.is_blocked,
    })
        

@dashboard_bp.route('/')
def home():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/home.html', active_page='home', doctor_name=g.doctor_user, license_number=g.license_number)

@dashboard_bp.route('/cases')
def cases():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    reports = SavedReport.query.filter_by(user_id=user_id).order_by(SavedReport.created_at.desc()).limit(5).all()
    return render_template('dashboard/cases.html', reports=reports, active_page='cases',
                           doctor_name=g.doctor_user, license_number=g.license_number)

@dashboard_bp.route('/cases/filter')
def filter_cases():
    if not session.get('user_id'):
        return jsonify([])

    user_id = session.get('user_id')
    query = request.args.get('q', '').strip()

    if query:
        reports = SavedReport.query.filter(
            SavedReport.user_id == user_id,
            SavedReport.case_id.ilike(f"%{query}%")
        ).order_by(SavedReport.created_at.desc()).limit(5).all()
    else:
        reports = SavedReport.query.filter_by(user_id=user_id).order_by(SavedReport.created_at.desc()).limit(5).all()

    # Convert to JSON
    data = [{
        'case_id': r.report_id,
        'date': r.created_at.strftime('%d/%m/%Y')
    } for r in reports]

    return jsonify(data)



@dashboard_bp.route('/help')
def help():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/help.html', active_page='help', doctor_name=g.doctor_user, license_number=g.license_number)



@dashboard_bp.route('/analyze', methods=['POST'])
def analyze():
    fasta_file = request.files.get('fasta')
    notes = request.form.get('notes', '')
    model = request.form.get('model', '').strip().lower()

    try:
        threshold = float(request.form.get('threshold', 96.2))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid threshold value'}), 400

    if not fasta_file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    if model == "quint":
        try:
            result = run_quint_analysis(fasta_file, threshold, notes)

            if isinstance(result, dict) and result.get("analysis_id"):
                analysis_id = result["analysis_id"]
                return jsonify({
                    'status': 'success',
                    'redirect_url': f'/dashboard/analysis/result/{analysis_id}'
                })

            return jsonify({'status': 'error', 'message': 'Analysis failed or invalid result format'}), 500

        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'}), 500

    return jsonify({'status': 'error', 'message': f'Model \"{model}\" not implemented.'}), 400




@dashboard_bp.route('/analysis/result/<int:analysis_id>')
def view_analysis_result(analysis_id):
    from app.models.quintx import (
        CaseReport, PhageMatch, Bacteria, Phages, Manufacturers,
        AdditionalMatch, AdditionalPhageMatch, PhagesManufacturers
    )

    case = CaseReport.query.get_or_404(analysis_id)
    bacteria = Bacteria.query.filter_by(name=case.name).first()

    bacteria_info = {
        "name": bacteria.name if bacteria else "Unknown",
        "ncbi_id": getattr(bacteria, "ncbi_id", "N/A"),
        "tax_id": getattr(bacteria, "tax_id", "N/A"),
    }

    # Main match phages
    phage_matches = PhageMatch.query.filter_by(case_report_id=case.id).all()
    phage_info_list = []
    for match in phage_matches:
        # You can join with Phages if needed to get NCBI ID etc.
        phage = Phages.query.filter_by(name=match.phage_name).first()
        manufacturer_data = (
            db.session.query(Manufacturers.name, PhagesManufacturers.price)
            .join(PhagesManufacturers, Manufacturers.manufacturer_id == PhagesManufacturers.manufacturer_id)
            .filter(PhagesManufacturers.phage_id == phage.phage_id if phage else None)
            .all()
        )
        phage_info_list.append({
            "name": match.phage_name,
            "ncbi": getattr(phage, "ncbi_id", "N/A") if phage else "N/A",
            "manufacturers": [
                {"name": name, "price": f"${price:.2f}"} for name, price in manufacturer_data
            ] if manufacturer_data else [{"name": "None", "price": "N/A"}]
        })

    # Additional matches
    additional_outputs = []
    additional_matches = AdditionalMatch.query.filter_by(case_report_id=case.id).all()

    for add in additional_matches:
        phage_links = AdditionalPhageMatch.query.filter_by(additional_match_id=add.id).all()

        phage_info_list = []
        for link in phage_links:
            phage = Phages.query.filter_by(phage_id=link.phage_id).first()
            if not phage:
                continue

            manufacturer_data = (
                db.session.query(Manufacturers.name, PhagesManufacturers.price)
                .join(PhagesManufacturers, Manufacturers.manufacturer_id == PhagesManufacturers.manufacturer_id)
                .filter(PhagesManufacturers.phage_id == phage.phage_id)
                .all()
            )

            phage_info_list.append({
                "name": phage.name,
                "ncbi": phage.ncbi_id or "N/A",
                "manufacturers": [
                    {"name": name, "price": f"${price:.2f}"} for name, price in manufacturer_data
                ] if manufacturer_data else [{"name": "None", "price": "N/A"}]
            })

        additional_outputs.append({
            "prob": add.match_score,
            "bacteria_info": {
                "name": add.bacteria_name,
                "ncbi_id": add.ncbi_id or "N/A",
                "tax_id": add.tax_id or "N/A",
            },
            "phage_info_list": phage_info_list
        })

    return render_template(
        "dashboard/result.html",
        report=case,
        bacteria_info=bacteria_info,
        phage_info_list=phage_info_list,
        additional_outputs=additional_outputs,
        no_match=False
    )













# Testing for Templates
# Analyze Template
@dashboard_bp.route('/report/<int:report_id>')
def report_view(report_id):
    # Simulate DB fetch
    report = {
        "date": "May 26, 2025",
        "case_id": report_id,
        "file_name": "e_coli_sample",
        "severity": "Moderate",
        "specimen_number": 23,
        "genome_length": "4.6 Mb",
        "name": "Escherichia coli",
        "gc_content": "50.8%",
        "resistance": "High",
        "background": "Escherichia coli is a versatile bacterium...",
        "best_phage": "Phage X1 (95%)",
        "match_effectiveness": "91%",
        "match_count": 2,
        "partial_matches": 1,
        "support_phone": "1-800-555-1234",
        "support_email": "vendor@digitaltherapeutix.com"
    }
    return render_template("components/analysis_report.html", report=report)



@dashboard_bp.route('/report/<int:report_id>/download')
def download_pdf(report_id):
    user_id = session.get('user_id')
    user_name = session.get('doctor_name', 'Doctor')
    if not user_id:
        flash("You must be logged in to download reports.", "danger")
        return redirect(url_for('auth.login'))

    # Simulated report data (replace this with actual database fetch logic)
    report = {
        "date": "May 26, 2025",
        "case_id": report_id,
        "file_name": "e_coli_sample",
        "severity": "Moderate",
        "specimen_number": 23,
        "genome_length": "4.6 Mb",
        "name": "Escherichia coli",
        "gc_content": "50.8%",
        "resistance": "High",
        "background": "Escherichia coli is a versatile bacterium...",
        "best_phage": "Phage X1 (95%)",
        "match_effectiveness": "91%",
        "match_count": 2,
        "partial_matches": 1,
        "support_phone": "1-800-555-1234",
        "support_email": "vendor@digitaltherapeutix.com"
    }

    # Generate PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    def add_title(text):
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>{text}</b>", styles["Heading3"]))
        elements.append(Spacer(1, 4))

    elements.append(Paragraph("Quint Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Date: {report['date']}<br/>Case ID: {report['case_id']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Uploaded Scan Data
    add_title("Uploaded Scan Data")
    data_table = [
        ["Uploaded File Name", report["file_name"]],
        ["Severity", report["severity"]],
        ["Specimen Number", report["specimen_number"]],
        ["Genome Length", report["genome_length"]],
        ["Name", report["name"]],
        ["GC Content", report["gc_content"]],
        ["Resistance", report["resistance"]],
        ["Background", report["background"]],
    ]
    table = Table(data_table, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Match Result
    add_title("Match Status & Result")
    match_table = [
        ["Most Effective Phage", report["best_phage"]],
        ["Match Effectiveness", report["match_effectiveness"]],
        ["100% Matches", report["match_count"]],
        ["Partial Matches", report["partial_matches"]],
    ]
    match = Table(match_table, colWidths=[200, 300])
    match.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(match)
    elements.append(Spacer(1, 12))

    # Support Info
    elements.append(Paragraph(f"""
        <b>Support</b><br/>
        Phone: {report['support_phone']}<br/>
        Email: {report['support_email']}
    """, styles["Normal"]))

    doc.build(elements)

    # Create dynamic filename for download (NOT stored permanently)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f'{user_name}_{report_id}_{timestamp}.pdf'

    # Return the PDF from memory without saving to disk or updating DB
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


