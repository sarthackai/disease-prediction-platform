"""
reports.py
Generates downloadable PDF reports for predictions.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user
from app.core.supabase_client import supabase
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

router = APIRouter()

@router.get("/generate/{prediction_id}")
async def generate_report(
    prediction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generates a PDF report for a specific prediction."""

    # Fetch prediction from Supabase
    result = supabase.table("predictions")\
        .select("*")\
        .eq("prediction_id", prediction_id)\
        .eq("user_id", current_user["sub"])\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction = result.data[0]

    # Fetch user info
    user_result = supabase.table("users")\
        .select("full_name, email, age, gender")\
        .eq("user_id", current_user["sub"])\
        .execute()

    user = user_result.data[0] if user_result.data else {}

    # Get top predicted disease
    top_predictions = prediction.get("top_predictions", [])
    predicted_disease = top_predictions[0]["disease"] if top_predictions else "Unknown"
    confidence = prediction.get("confidence_score", 0)

    # Get selected symptoms
    symptoms_input = prediction.get("symptoms_input", {})
    selected_symptoms = [
        k.replace("_", " ").title()
        for k, v in symptoms_input.items()
        if v == 1
    ]

    # Get SHAP explanation
    shap_explanation = prediction.get("shap_explanation", [])

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#4F46E5"),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    story.append(Paragraph("HealthAI Medical Report", title_style))

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph(
        "AI-Powered Disease Prediction · SDG 3: Good Health and Well-Being",
        subtitle_style
    ))
    story.append(Spacer(1, 0.5*cm))

    # Patient Info Table
    story.append(Paragraph("Patient Information", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))

    patient_data = [
        ["Name", user.get("full_name", "N/A")],
        ["Email", user.get("email", "N/A")],
        ["Age", str(user.get("age", "N/A"))],
        ["Gender", str(user.get("gender", "N/A")).title()],
        ["Report Date", datetime.now().strftime("%d %B %Y, %I:%M %p")],
        ["Report ID", prediction_id[:8].upper()],
    ]

    patient_table = Table(patient_data, colWidths=[5*cm, 12*cm])
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4F46E5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.8*cm))

    # Prediction Result
    story.append(Paragraph("Prediction Result", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))

    pred_data = [
        ["Predicted Disease", predicted_disease],
        ["Confidence Score", f"{confidence * 100:.1f}%"],
        ["Severity Level", prediction.get("severity_score", "Moderate")],
        ["Model Used", prediction.get("model_used", "N/A")],
    ]

    pred_table = Table(pred_data, colWidths=[5*cm, 12*cm])
    pred_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4F46E5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(pred_table)
    story.append(Spacer(1, 0.8*cm))

    # Symptoms Reported
    if selected_symptoms:
        story.append(Paragraph("Symptoms Reported", styles["Heading2"]))
        story.append(Spacer(1, 0.3*cm))
        symptoms_text = " · ".join(selected_symptoms)
        story.append(Paragraph(symptoms_text, styles["Normal"]))
        story.append(Spacer(1, 0.8*cm))

    # SHAP Explanation
    if shap_explanation:
        story.append(Paragraph(
            "AI Explanation (SHAP — Key Influencing Symptoms)",
            styles["Heading2"]
        ))
        story.append(Spacer(1, 0.3*cm))

        shap_data = [["Symptom", "Influence Score", "Direction"]]
        for s in shap_explanation:
            direction = "▲ Towards disease" if s["shap_value"] >= 0 else "▼ Away from disease"
            shap_data.append([
                s["symptom"].replace("_", " ").title(),
                str(abs(s["shap_value"])),
                direction
            ])

        shap_table = Table(shap_data, colWidths=[7*cm, 5*cm, 5*cm])
        shap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(shap_table)
        story.append(Spacer(1, 0.8*cm))

    # Disclaimer
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceBefore=20
    )
    story.append(Paragraph(
        "⚠️ DISCLAIMER: This report is generated by an AI system and is NOT a medical diagnosis. "
        "Always consult a qualified healthcare professional before making any medical decisions.",
        disclaimer_style
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=HealthAI_Report_{prediction_id[:8]}.pdf"
        }
    )