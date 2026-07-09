# Streamlit Community Cloud Deployment

Use this option for the free online demo of the Credibility Review Center.

## Recommended Setup

- Platform: Streamlit Community Cloud
- App folder: `fake_news_detection_system`
- Main file path: `fake_news_detection_system/app.py`
- Python dependencies: `fake_news_detection_system/requirements.txt`
- System dependency for OCR: `packages.txt`
- Included model: `fake_news_detection_system/models/baseline/logistic_regression_model.pkl`

## Deploy Steps

1. Push this workspace to GitHub.
2. Open https://share.streamlit.io.
3. Click **Create app**.
4. Choose the GitHub repository and branch.
5. Set **Main file path** to:

```text
fake_news_detection_system/app.py
```

6. Click **Deploy**.

## Important Notes

- Do not upload `data/raw/` or `data/processed/`; they are large training files.
- The deployed demo uses the lightweight baseline model.
- Review history on Streamlit Cloud is temporary and may reset when the app restarts.
- For permanent history storage, connect the app to a database later.
