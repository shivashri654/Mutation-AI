from flask import Flask, render_template, request, make_response
from xhtml2pdf import pisa
from datetime import datetime
from io import BytesIO
import joblib
import os

app = Flask(__name__)

# Joblib use panni load pannu
model = joblib.load('mutation_model.joblib')
vectorizer = joblib.load('tfidf_vectorizer.joblib')

print("Model and Vectorizer loaded successfully! ✅")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    gene = request.form['gene']
    var_type = request.form['var_type']
    phenotype = request.form['phenotype']

    input_text = f"{gene} {var_type} {phenotype}"
    input_vector = vectorizer.transform([input_text])

    prediction = model.predict(input_vector)[0]
    proba = model.predict_proba(input_vector)[0]
    confidence = round(max(proba) * 100, 2)

    if prediction == 1:
        label = "Harmful - High Risk"
        risk_level = "Very High" if confidence > 85 else "High"
        dna_image = "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800"
        summary = "This mutation indicates a significant alteration in the gene function, potentially leading to protein truncation or loss of function. Immediate clinical review is advised."
    else:
        label = "Benign - Safe"
        risk_level = "Low"
        dna_image = "https://images.unsplash.com/photo-1614935151651-0bea6508db6b?w=800"
        summary = "The detected variant is classified as benign with no significant predicted impact on protein function or disease risk."

    disease_map = {
        'BRCA1': 'Breast/Ovarian Cancer',
        'TP53': 'Li-Fraumeni Syndrome',
        'CFTR': 'Cystic Fibrosis'
    }
    disease = disease_map.get(gene.upper(), 'Unknown - Requires Clinical Testing')
    effect = "Protein truncation, Loss of function" if prediction == 1 else "No significant impact on protein"

    return render_template('result.html',
                           gene=gene,
                           var_type=var_type,
                           phenotype=phenotype,
                           prediction=label,
                           confidence=confidence,
                           risk=risk_level,
                           disease=disease,
                           effect=effect,
                           summary=summary,
                           dna_image=dna_image)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = {
        'gene': request.form['gene'],
        'mutation': request.form['var_type'],  # var_type ah vangitu mutation nu maarom
        'prediction': request.form['prediction'],
        'risk': request.form['risk'],
        'confidence': request.form['confidence'],
        'summary': request.form['summary'],
        'disease': request.form['disease'],
        'effect': request.form['effect'],
        'phenotype': request.form['phenotype'],
        'date': datetime.now().strftime("%d %b %Y, %H:%M")
    }

    rendered = render_template('pdf_template.html', **data)

    # xhtml2pdf use panni PDF create panrom
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(rendered, dest=pdf)

    if pisa_status.err:
        return "PDF creation failed", 500

    pdf.seek(0)
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename=MutationAI_Report_{data['gene']}.pdf"
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)