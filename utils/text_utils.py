from fpdf import FPDF
import io
import re
import datetime   # <-- import datetime here

def json_to_pdf(data: dict) -> bytes:
    # Mapping from JSON keys to human-readable labels
    key_labels = {
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "address": "Address",
        "chief_complaint": "Chief Complaint",
        "symptom_duration": "Symptom Duration",
        "symptom_frequency": "Symptom Frequency",
        "medical_history": "Medical History",
        "surgical_history": "Surgical History",
        "current_medications": "Current Medications",
        "allergies": "Allergies",
        "region": "Region",
        "partner_name": "Partner’s Name",
        "partner_age": "Partner’s Age",
        "pregnancies": "Number of Pregnancies",
        "deliveries": "Number of Deliveries",
        "miscarriages": "Number of Miscarriages",
        "menstrual_cycle_regular": "Is Menstrual Cycle Regular",
        "last_period": "Start of Last Period",
        "previous_treatments": "Previous Treatments, If Any",
        "family_history": "Family History",
        "lifestyle": "Lifestyle",
        "diet": "Diet",
        "exercise": "Exercise",
        "sleep_pattern": "Sleeping Habits",
        "stress_levels": "Stress Level",
        "smoking": "Smoke",
        "drinking": "Drink"
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Patient Intake Summary", ln=True, align="C")
    pdf.ln(5)

    # ─── Insert current date and time ─────────────────────────────────────────────────
    now = datetime.datetime.now()
    formatted = now.strftime("%Y-%m-%d  %H:%M:%S")  # e.g. "2025-06-02  14:30:05"
    pdf.set_font("Arial", "", 10)
    # Place date at left margin
    pdf.cell(0, 6, f"Generated on: {formatted}", ln=True, align="L")
    pdf.ln(5)
    # ────────────────────────────────────────────────────────────────────────────────

    def add_kv(key, value, indent=0):
        # Determine the label (fallback to raw key if not found)
        label = key_labels.get(key, key)

        # Compute x‐position based on indent (5 mm per indent level)
        x_pos = pdf.l_margin + indent * 5
        pdf.set_x(x_pos)

        if isinstance(value, dict):
            # Section header (bold)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"{label}:", ln=True)

            # Recurse into nested dictionary items
            for subkey, subval in value.items():
                add_kv(subkey, subval, indent + 1)
        else:
            # Regular key: show in two columns
            pdf.set_font("Arial", "", 12)

            # Compute width for the label column (reduce if indented)
            base_label_width = 60
            label_width = max(20, base_label_width - indent * 5)

            # First cell: label
            pdf.cell(label_width, 10, f"{label}:", border=0)

            # Second cell: value (rest of the line)
            pdf.cell(0, 10, str(value), ln=True)

    # Iterate through top‐level items
    for top_key, top_val in data.items():
        add_kv(top_key, top_val)

    # Generate PDF bytes (handle both str and bytes returns)
    raw = pdf.output(dest="S")
    return raw.encode("latin-1") if isinstance(raw, str) else raw
