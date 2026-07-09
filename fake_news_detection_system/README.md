# AI-Powered Fake News Detection and Credibility Analysis System Using Transformer Models

This project is a complete Streamlit web application for fake news detection and credibility analysis. It is designed for a final-year Computer Science project and uses a locally fine-tuned transformer model as the main classifier.

## Streamlit Community Cloud Deployment

This folder is ready to deploy on Streamlit Community Cloud.

Recommended first deployment:

- Platform: Streamlit Community Cloud
- Repository folder: `fake_news_detection_system`
- Main file path: `fake_news_detection_system/app.py` if you push the whole workspace, or `app.py` if this folder is the GitHub repository root
- Model mode: lightweight baseline model from `models/baseline/logistic_regression_model.pkl`

Large training datasets in `data/raw/` and `data/processed/` are intentionally ignored for deployment. The cloud app only needs the app code, requirements, samples, reports, and the lightweight baseline model.

Deployment steps:

1. Push this project to GitHub.
2. Open Streamlit Community Cloud: https://share.streamlit.io
3. Select **Create app**.
4. Choose your GitHub repository and branch.
5. Set the main file path to `fake_news_detection_system/app.py` if this folder is inside a larger repository.
6. Deploy the app.

The app includes:

- `requirements.txt` for Python dependencies
- `packages.txt` for the Tesseract OCR system dependency
- `.gitignore` rules to avoid uploading large training data and local history

Run locally from this folder:

```bash
streamlit run app.py
```

The app does not use image upload, OCR, automatic URL extraction, or an online fake-news classifier. The transformer model must be trained by this project and saved locally before prediction.

## Features

- Manual news checking from title and article content
- CSV batch upload with downloadable results
- Prediction classes: Likely Real News, Fake News, Suspicious / Needs Review
- Fake probability, real probability, credibility score, and risk level
- User-friendly explanation and recommended verification action
- Prediction history saved to CSV
- Dashboard analytics with KPIs and Plotly charts
- About Model page with metrics, reports, confusion matrix, and limitations
- Baseline TF-IDF + Logistic Regression model for comparison
- Main BERT-base or RoBERTa-base fine-tuning pipeline

## Folder Structure

```text
fake_news_detection_system/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   ├── processed/
│   └── history/
├── models/
│   ├── baseline/
│   └── transformer_fake_news/
├── reports/
├── training/
├── utils/
├── pages/
└── samples/
```

## Setup

Create and activate a virtual environment if preferred, then install dependencies:

```bash
pip install -r requirements.txt
```

## Dataset Preparation

Use one of these dataset options.

Kaggle Fake and Real News Dataset:

```text
data/raw/Fake.csv
data/raw/True.csv
```

The preparation script assigns:

- `Fake.csv` -> `label = 1`
- `True.csv` -> `label = 0`

WELFake Dataset:

```text
data/raw/WELFake_Dataset.csv
```

The script expects `title`, `text`, and `label` columns. It standardizes output into:

- `title`
- `text`
- `combined_text`
- `label`

Target label mapping:

- `REAL = 0`
- `FAKE = 1`

If your WELFake file uses a different original label convention, pass:

```bash
python training/prepare_data.py --welfake-real-label 0
```

Default:

```bash
python training/prepare_data.py
```

## Train Baseline Model

```bash
python training/train_baseline.py
```

This trains TF-IDF + Logistic Regression and saves:

```text
models/baseline/logistic_regression_model.pkl
reports/baseline_metrics.json
```

## Train Transformer Model

Default training uses `bert-base-uncased`:

```bash
python training/train_transformer.py
```

Recommended MacBook M3 Pro settings:

```bash
python training/train_transformer.py --model-name bert-base-uncased --max-length 256 --batch-size 4 --epochs 2 --learning-rate 2e-5 --weight-decay 0.01
```

To use RoBERTa-base:

```bash
python training/train_transformer.py --model-name roberta-base --max-length 256 --batch-size 4 --epochs 2
```

The script automatically reports the detected device:

- MPS on Apple Silicon if available
- CUDA if available
- CPU fallback

The trained local model is saved to:

```text
models/transformer_fake_news/
```

## Evaluate Transformer Model

```bash
python training/evaluate_model.py
```

This saves:

```text
reports/metrics.json
reports/classification_report.txt
reports/confusion_matrix.png
```

## Run Streamlit App

```bash
streamlit run app.py
```

If the transformer has not been trained yet, the app will show a clear warning and prediction pages will ask you to train the model first.

## How To Use The App

1. Open the Streamlit app.
2. Go to `Check News`.
3. Enter a news title and article content.
4. Optionally enter source and URL metadata.
5. Click `Analyze News`.
6. Review the prediction, probabilities, credibility score, risk level, explanation, and recommended action.
7. Use `Batch Upload` for CSV files with required columns `title` and `text`.
8. Use `History` and `Dashboard` to review saved predictions and analytics.

Sample batch template:

```text
samples/sample_batch_template.csv
```

## Prediction Rules

The transformer outputs fake-news probability. The app converts it into user-facing decisions:

- `fake_probability >= 75%`: Fake News, High Risk
- `fake_probability >= 45% and < 75%`: Suspicious / Needs Review, Medium Risk
- `fake_probability < 45%`: Likely Real News, Low Risk

Credibility score:

```text
credibility_score = 100 - fake_probability
```

## Limitations

This system does not prove whether news is 100% true or false. It provides an AI-based credibility prediction to support user verification. Users should still check trusted and official sources before sharing sensitive information.

The model can be affected by dataset bias, outdated training data, short articles, satire, copied content, and topics not represented well in the training dataset.

## Future Improvements

- Add stronger explainability using SHAP, LIME, or attention visualizations
- Add source reputation features
- Add multilingual fake news detection
- Add model drift monitoring
- Add authenticated admin analytics
- Add optional URL extraction later, with careful source validation
- Add OCR/image checking later as a separate module

## Full Command Sequence

```bash
pip install -r requirements.txt
python training/prepare_data.py
python training/train_baseline.py
python training/train_transformer.py
python training/evaluate_model.py
streamlit run app.py
```
