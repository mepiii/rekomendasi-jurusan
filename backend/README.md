Backend app entrypoint: app/main.py
Run local:
1) pip install -r requirements.txt
2) python ml/dataset_generator.py --rows 800
3) python ml/train_pipeline.py
4) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
