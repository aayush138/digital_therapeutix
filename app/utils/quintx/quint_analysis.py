from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app.extensions import db
from app.models.quintx import CaseReport, PhageMatch, Bacteria, Phages, Manufacturers, BacteriaPhages, PhagesManufacturers, AdditionalMatch, AdditionalPhageMatch
from app.utils.matcher.matcher import Matcher

def run_quint_analysis(fasta_file, threshold=96.2, notes=None,case_id=None):
    filename = secure_filename(fasta_file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    # Create folder if doesn't exist
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

    fasta_file.save(filepath)
    additional_notes = notes.strip() if notes else "No additional notes provided."

    matcher = Matcher(ref_db="data/bacteria_blst/blst", high_prob_threshold=threshold)
    exact, matches = matcher.match(filepath)
    if not matches:
        return {"error": "No match found"}

    top_matches = matches[:4]
    main_match = top_matches[0]
    additional_matches = top_matches[1:]
    match_id, prob = main_match
    bacteria = Bacteria.query.filter_by(bacteria_id=match_id).first()

    phage_links = BacteriaPhages.query.filter_by(bacteria_id=match_id).all()
    phage_info_list = []
    phage_match_objs = []

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

        phage_match_objs.append(PhageMatch(
            phage_name=phage.name,
            effectiveness=prob,
            host_range='Unknown',
            cost='N/A',
            turnaround_time='Unknown',
            insurance_status='Unknown',
            match_type='100%' if exact else 'Partial',
            recommended=exact
        ))

    case = CaseReport(
        user_id=1,
        case_id=case_id,
        uploaded_file_name=filename,
        specimen_number="N/A",
        genome_length="N/A",
        name=bacteria.name if bacteria else "Unknown",
        gc_content="N/A",
        resistance="Unknown",
        severity="Unknown",
        background=additional_notes,
        most_effective_phage=phage_info_list[0]["name"] if phage_info_list else "None",
        match_effectiveness=prob,
        match_score=prob,
        matches_100=1 if exact else 0,
        matches_partial=0 if exact else 1,
        pdf_filename=f"{filename}.pdf",
        pdf_path=f"/static/reports/{filename}.pdf",
        created_at=datetime.utcnow()
    )
    db.session.add(case)
    db.session.flush()  # So we can get case.id

    for ph in phage_match_objs:
        ph.case_report_id = case.id
        db.session.add(ph)


    for add_match_id, add_prob in additional_matches:
        bacteria = Bacteria.query.filter_by(bacteria_id=add_match_id).first()
        if not bacteria:
            continue

        # Save the additional bacteria match
        add_match = AdditionalMatch(
            case_report_id=case.id,
            bacteria_name=bacteria.name,
            ncbi_id=bacteria.ncbi_id,
            tax_id=bacteria.tax_id,
            match_score=add_prob
        )
        db.session.add(add_match)
        db.session.flush()  # to get add_match.id

        # Get associated phages for this suggested bacteria
        links = BacteriaPhages.query.filter_by(bacteria_id=bacteria.bacteria_id).all()
        for link in links:
            phage = Phages.query.filter_by(phage_id=link.phage_id).first()
            if not phage:
                continue
            add_phage = AdditionalPhageMatch(
                additional_match_id=add_match.id,
                phage_id=phage.phage_id
            )
            db.session.add(add_phage)    

    db.session.commit()

    
    return {"analysis_id": case_id}