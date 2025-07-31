from flask import Blueprint, render_template, session, redirect, url_for, flash, g, request, jsonify, make_response, send_file
from app.models.user import User, db
from weasyprint import HTML
from collections import defaultdict
from app.models.quintx import  CaseReport, PhageMatch, Bacteria, Phages, Manufacturers, AdditionalMatch, AdditionalPhageMatch, PhagesManufacturers
from datetime import datetime, timezone
from app.utils.quintx.quint_analysis import run_quint_analysis
import os, random, tempfile


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

    user_id = session['user_id']

    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Fetch paginated case reports for the logged-in doctor
    reports = CaseReport.query.filter_by(user_id=user_id) \
        .order_by(CaseReport.created_at.desc()) \
        .paginate(page=page, per_page=per_page)

    # Calculate start and end indices
    start = (reports.page - 1) * reports.per_page + 1 if reports.total > 0 else 0
    end = min(reports.page * reports.per_page, reports.total)

    return render_template(
        'dashboard/cases.html',
        reports=reports,
        start=start,
        end=end,
        active_page='cases',
        doctor_name=g.doctor_user,
        license_number=g.license_number
    )


@dashboard_bp.route('/cases/filter')
def filter_cases():
    if not session.get('user_id'):
        return jsonify([])

    user_id = session.get('user_id')
    query = request.args.get('q', '').strip()

    if query:
        reports = CaseReport.query.filter(
            CaseReport.user_id == user_id,
            CaseReport.case_id.ilike(f"%{query}%")
        ).order_by(CaseReport.created_at.desc()).limit(5).all()
    else:
        reports = CaseReport.query.filter_by(user_id=user_id).order_by(CaseReport.created_at.desc()).limit(5).all()

    data = [{
        'case_id': r.case_id,
        'date': r.created_at.strftime('%d/%m/%Y')
    } for r in reports]

    return jsonify(data)



@dashboard_bp.route('/help')
def help():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/help.html', active_page='help', doctor_name=g.doctor_user, license_number=g.license_number)



def generate_case_id():
    last_case = db.session.query(CaseReport).order_by(CaseReport.id.desc()).first()
    return random.randint(10000, 99999) if not last_case else last_case.id + 1

@dashboard_bp.route('/analyze', methods=['POST'])
def analyze():
    fasta_file = request.files.get('fasta')
    notes = request.form.get('notes', '')
    model = request.form.get('model', '').strip().lower()
    case_id = request.form.get('case_id')  # coming silently from frontend

    try:
        threshold = float(request.form.get('threshold', 96.2))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid threshold value'}), 400

    if not fasta_file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    
    if not case_id:
        last = CaseReport.query.order_by(CaseReport.id.desc()).first()
        new_number = last.id + 1 if last else 10001
        case_id = f"{new_number}"

    if model == "quint":
        try:
            result = run_quint_analysis(fasta_file, threshold, notes, case_id)

            if isinstance(result, dict) and result.get("analysis_id"):
                analysis_id = result["analysis_id"]
                return jsonify({
                    'status': 'success',
                    'redirect_url': f'/dashboard/analysis/result/{analysis_id}'
                })

            return jsonify({'status': 'error'}), 500

        except Exception:
            return jsonify({'status': 'error'}), 500

    return jsonify({'status': 'error'}), 400




@dashboard_bp.route('/analysis/result/<string:case_id>')
def view_analysis_result(case_id):
    case = CaseReport.query.filter_by(case_id=case_id).first_or_404()
    bacteria = Bacteria.query.filter_by(name=case.name).first()

    bacteria_info = {
        "name": bacteria.name if bacteria else "Unknown",
        "ncbi_id": getattr(bacteria, "ncbi_id", "N/A"),
        "tax_id": getattr(bacteria, "tax_id", "N/A"),
    }

    # Main match phages
    phage_matches = PhageMatch.query.filter_by(case_report_id=case.id).all()
    main_phage_info_list = []
    for match in phage_matches:
        phage = Phages.query.filter_by(name=match.phage_name).first()
        manufacturer_data = (
            db.session.query(Manufacturers.name, PhagesManufacturers.price)
            .join(PhagesManufacturers, Manufacturers.manufacturer_id == PhagesManufacturers.manufacturer_id)
            .filter(PhagesManufacturers.phage_id == phage.phage_id if phage else None)
            .all()
        )
        main_phage_info_list.append({
            "name": match.phage_name,
            "ncbi": getattr(phage, "ncbi_id", "N/A") if phage else "N/A",
            "phage_id": getattr(phage, "phage_id", None) if phage else None,
            "manufacturers": [
                {"name": name, "price": f"${price:.2f}"} for name, price in manufacturer_data
            ] if manufacturer_data else [{"name": "None", "price": "N/A"}]
        })

    # Additional matches
    additional_outputs = []
    additional_matches = AdditionalMatch.query.filter_by(case_report_id=case.id).all()

    for add in additional_matches:
        phage_links = AdditionalPhageMatch.query.filter_by(additional_match_id=add.id).all()

        additional_phages = []
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

            additional_phages.append({
                "name": phage.name,
                "ncbi": phage.ncbi_id or "N/A",
                "phage_id": phage.phage_id,
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
            "phage_info_list": additional_phages  # clearly named
        })

    return render_template(
        "dashboard/result.html",
        report=case,
        bacteria_info=bacteria_info,
        main_phage_info_list=main_phage_info_list,  # proper reference
        additional_outputs=additional_outputs,
        no_match=False,
        doctor_name=g.doctor_user,
        license_number=g.license_number,
    )




# Report Viewer
def get_report_data(report_id):
    # Get main case report
    case = CaseReport.query.filter_by(case_id=report_id).first_or_404()
    bacteria = Bacteria.query.filter_by(name=case.name).first()

    primary_bacteria = {
        "name": bacteria.name if bacteria else case.name or "Unknown",
        "ncbi": getattr(bacteria, "ncbi_id", "N/A"),
        "tax_id": getattr(bacteria, "tax_id", "N/A"),
        "score": round(case.match_score, 2) if case.match_score is not None else 100,
        "phages": []
    }

    phage_groups = defaultdict(list)

    for match in case.phage_matches:
        phage = match.phage or Phages.query.filter_by(name=match.phage_name).first()
        if not phage:
            continue

        manufacturer_links = PhagesManufacturers.query.filter_by(phage_id=phage.phage_id).all()
        for link in manufacturer_links:
            manufacturer = link.manufacturer
            phage_groups[phage.name].append({
                "source": manufacturer.name if manufacturer else "Unknown",
                "price": f"${link.price:.2f}" if link.price is not None else "N/A"
            })

    # Convert grouped phages to list format
    for phage_name, vendors in phage_groups.items():
        sorted_vendors = sorted(
            vendors,
            key=lambda v: float(v["price"].replace("$", "")) if v["price"] != "N/A" else float("inf")
        )
        primary_bacteria["phages"].append({
            "name": phage_name,
            "vendors": sorted_vendors
        })

    # --- Additional Matches Grouped ---
    additional_matches = []

    for add_match in case.additional_matches:
        phage_group = defaultdict(list)

        for link in add_match.phage_matches:
            phage = link.phage
            if not phage:
                continue

            manufacturer_links = PhagesManufacturers.query.filter_by(phage_id=phage.phage_id).all()
            for m in manufacturer_links:
                manufacturer = m.manufacturer
                phage_group[phage.name].append({
                    "source": manufacturer.name if manufacturer else "Unknown",
                    "price": f"${m.price:.2f}" if m.price is not None else "N/A"
                })

        # Convert group to list
        grouped_phages = []
        for name, vendors in phage_group.items():
            sorted_vendors = sorted(
                vendors,
                key=lambda v: float(v["price"].replace("$", "")) if v["price"] != "N/A" else float("inf")
            )
            grouped_phages.append({
                "name": name,
                "vendors": sorted_vendors
            })

        additional_matches.append({
            "name": add_match.bacteria_name or "Unknown",
            "ncbi": add_match.ncbi_id or "N/A",
            "tax_id": add_match.tax_id or "N/A",
            "score": round(add_match.match_score or 0, 2),
            "phages": grouped_phages
        })

    return {
        "case_id": case.case_id,
        "date": case.created_at.strftime("%B %d, %Y") if case.created_at else "N/A",
        "support_phone": "1-800-555-1234",
        "support_email": "vendor@digitaltherapeutix.com",
        "primary_bacteria": primary_bacteria,
        "additional_matches": additional_matches
    }


# view report
@dashboard_bp.route('/report/<int:report_id>')
def report_view(report_id):
    report = get_report_data(report_id)
    return render_template("components/analysis_report.html", report=report)

# download report as PDF
@dashboard_bp.route('/report/<int:report_id>/download')
def download_pdf(report_id):
    user_id = session.get('user_id')
    user_name = session.get('doctor_name', 'Doctor').replace(" ", "_")

    if not user_id:
        flash("You must be logged in to download reports.", "danger")
        return redirect(url_for('auth.login'))

    # Reuse shared report logic
    report = get_report_data(report_id)
    rendered_html = render_template("components/analysis_report.html", report=report)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            HTML(string=rendered_html, base_url=request.url_root).write_pdf(temp_pdf.name)
            temp_pdf.seek(0)
            pdf_data = temp_pdf.read()
        os.unlink(temp_pdf.name)
    except Exception as e:
        flash(f"PDF generation failed: {str(e)}", "danger")
        return redirect(url_for('dashboard.report_view', report_id=report_id))

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{user_name}_Report_{report_id}_{timestamp}.pdf"

    response = make_response(pdf_data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response




# Phage Manufacturers
@dashboard_bp.route('/phage/<phage_id>/vendors')
def view_phage_vendors(phage_id):
    report_id = request.args.get('report_id')
    phage = Phages.query.get(phage_id)

    if not phage:
        flash('Phage not found', 'danger')
        return redirect(url_for('dashboard.report_view', report_id=report_id))
    
    bacteria_info = [bp.bacteria for bp in phage.bacteria]

    manufacturers_data = []
    for pm in phage.manufacturers:
        manufacturers_data.append({
            "name": pm.manufacturer.name,
            "type": pm.manufacturer.type,
            "location": pm.manufacturer.address,
            "price": f"${pm.price:.2f}",
            "manufacturer_id": pm.manufacturer.manufacturer_id,
            "description": pm.manufacturer.application,
        })

    return render_template('dashboard/phage_vendors.html', phage=phage, bacteria_info=bacteria_info ,manufacturers=manufacturers_data, report_id=report_id)