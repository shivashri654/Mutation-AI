# MutationAI v2.0 🧬

AI-powered DNA mutation analysis tool using Flask + Machine Learning.

### 🚀 Features
- Predict gene mutations as **Harmful** or **Benign**
- Shows confidence score, risk assessment & biological effect
- Predicts potential disease association
- Generates downloadable **Clinical PDF Reports**
- Cyberpunk themed UI

### 🛠️ Tech Stack
`Python` `Flask` `Scikit-learn` `Pandas` `WeasyPrint` `HTML/CSS`

### ⚙️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/UN_USERNAME/MutationAI.git
   cd MutationAI
   2. **Download Model Files:**
   > ⚠️ Due to GitHub's file size limit, model files are hosted on Google Drive.
   
   Download the files and place them in the root directory:
   - [mutation_model.joblib](https://drive.google.com/file/d/1PS7pAznluUHAc_ejVN1PqhXBYdxe03Fd/view?usp=sharing)
   - [tfidf_vectorizer.joblib](https://drive.google.com/file/d/1h4HkUhRhDVDJBYoXkOoDS7HXkq4Qpmqe/view?usp=sharing)
   
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt