from flask import Flask, render_template, request, make_response
from xhtml2pdf import pisa
from datetime import datetime
from io import BytesIO
import joblib
import os
import gdown

app = Flask(__name__)

# =============== GOOGLE DRIVE FILE IDs - UNNODADHU READY ✅ ===============
MODEL_FILE_ID = "1PS7pAznluUHAc_ejVN1PqhXBYdxe03Fd"
VECTORIZER_FILE_ID = "1h4HkUhRhDVDJBYoXkOoDS7HXkq4Qpmqe"
# =========================================================================

model = None
vectorizer = None

def download_from_drive():
    global model, vectorizer

    # Model download
    if not os.path.exists('mutation_model.joblib'):
        print("Downloading mutation_model.joblib from Google Drive... Idhu periya file, 2-3 min aagum")
        try:
            gdown.download(f'https://drive.google.com/uc?id={MODEL_FILE_ID}', 'mutation_model.joblib', quiet=False)
            print("✅ Model downloaded successfully")
        except Exception as e:
            print(f"❌ Model download failed: {e}")

    # Vectorizer download
    if not os.path.exists('tfidf_vectorizer.joblib'):
        print("Downloading tfidf_vectorizer.joblib from Google Drive...")
        try:
            gdown.download(f'https://drive.google.com/uc?id={VECTORIZER_FILE_ID}', 'tfidf_vectorizer.joblib', quiet=False)
            print("✅ Vectorizer downloaded successfully")
        except Exception as e:
            print(f"❌ Vectorizer download failed: {e}")

    # Load panna muyarchi
    try:
        if os.path.exists('mutation_model.joblib') and os.path.exists('tfidf_vectorizer.joblib'):
            model = joblib.load('mutation_model.joblib')
            vectorizer = joblib.load('tfidf_vectorizer.joblib')
            print("✅✅✅ REAL ML MODEL LOADED SUCCESSFULLY FROM GOOGLE DRIVE! ✅✅✅")
        else:
            print("⚠️ Files download aagala. Drive 'Anyone with the link' permission check pannu da.")
    except Exception as e:
        print(f"⚠️ Error loading model: {e}")

# App start aagum bodhe download aagidum
download_from_drive()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or vectorizer is None:
        return "Error 500: Model load aagala. Render logs la check pannu. Drive file ku 'Anyone with the link' permission iruka nu paaru.", 500

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
        'CFTR': 'Cystic Fibrosis',
        'EGFR': 'Lung Cancer',
        'APC': 'Colon Cancer'
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
        'mutation': request.form['var_type'],
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
    app.run(host='0.0.0.0', port=port, debug=False)
