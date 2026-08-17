# Gallbladder Cancer Dynamic Survival Nomogram

Shiny for Python implementation of the locked **Redefined 2 + XGBoost-Cox** survival model.

## Local use

```bash
pip install -r requirements.txt
python -m shiny run --host 127.0.0.1 --port 8010 app.py
```

Open `http://127.0.0.1:8010`.

Run the command from this directory. Do not use `--reload` behind Colab,
Cloudflare, shinyapps.io, or another reverse proxy: the development reload
endpoint can be converted to a plain-text `Not Found` response and cause a
browser-side JSON parsing error.

## Deploy to shinyapps.io

```bash
pip install rsconnect-python
rsconnect add --account YOUR_ACCOUNT --name shinyapps --token YOUR_TOKEN --secret YOUR_SECRET
rsconnect deploy shiny . --name gallbladder-survival-nomogram --title "Gallbladder Cancer Survival Nomogram"
```

For a generic hosted container, use:

```bash
python -m shiny run --host 0.0.0.0 --port ${PORT:-8000} app.py
```

Do not commit deployment tokens or raw SEER case-level data. The application uses the locked model bundle and does not require the development dataset at runtime.

## Interpretation

The display is a dynamic nomogram-style prediction interface. It is not a conventional additive Cox nomogram because XGBoost-Cox is a nonlinear ensemble model. T, Redefined 2 N, and M are first converted to the Redefined 2 stage group; the final model then uses stage, age, sex, race, and grade.
