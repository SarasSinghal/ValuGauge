# ValuGauge — Second-Hand Car Price Estimator

A small full-stack web app around your trained `LinearRegressionModel.pkl`. It includes
sign up / sign in (with hashed passwords), a responsive valuation form that only asks
for the fields the model actually needs, an animated "gauge" result, and a per-user
history of past estimates stored in a SQLite database.

## What the model needs

Your model (`LinearRegressionModel.pkl`) was a scikit-learn pipeline
(`OneHotEncoder` + `LinearRegression`) that expects exactly these 5 inputs:

| Field | Type | Notes |
|---|---|---|
| `name` | category | Car model, e.g. `Maruti Suzuki Swift` (the encoder was trained on "brand + first two model words") |
| `company` | category | Manufacturer, e.g. `Maruti` |
| `year` | integer | Year of purchase/registration |
| `kms_driven` | integer | Total kilometres driven |
| `fuel_type` | category | `Petrol`, `Diesel`, or `LPG` |

**Why there's no `.pkl` file in this project:** pickled scikit-learn objects
are tied to the exact scikit-learn version used to create them, and loading
a pickle from a different version commonly throws errors like
`AttributeError: ... has no attribute '_RemainderColsList'`. To avoid that,
the OneHotEncoder's trained categories and the LinearRegression's
coefficients/intercept were extracted once and saved as plain JSON
(`model/model_weights.json`). At runtime, `app.py` reproduces the exact same
one-hot-encode + linear-regression math using only `numpy` — no
scikit-learn dependency, and no version coupling. This was verified to
produce identical predictions to the original pipeline.

The site only lets the user pick manufacturer/model values that the encoder was
actually trained on (loaded from `model/company_models.json` and
`model/categories.json`, both extracted from the original pickle's
`OneHotEncoder.categories_`).
Selecting a manufacturer dynamically loads the matching list of models via
`/api/models/<company>`.

## Project structure

```
carapp/
├── app.py                  # Flask app: auth, routes, prediction, history
├── requirements.txt
├── model/
│   ├── model_weights.json  # OneHotEncoder categories + LinearRegression coef/intercept
│   ├── categories.json     # fuel types + raw category lists
│   └── company_models.json # manufacturer -> list of valid model names
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── predict.html
│   ├── history.html
│   └── 404.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── instance/                # SQLite DB created here at runtime
```

## Setup

1. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser. The SQLite database
   (`instance/carprice.db`) is created automatically on first run.

## How it works

- **Sign up / sign in** — accounts are stored in SQLite via Flask-SQLAlchemy,
  passwords are hashed with Werkzeug's `generate_password_hash`. Sessions are
  managed with Flask-Login.
- **Valuation form** (`/predict`, login required) — collects manufacturer,
  model, year, kilometres driven, and fuel type (all required). On submit,
  the values are one-hot encoded and combined with the model's saved
  coefficients/intercept (`predict_price()` in `app.py`) to produce the
  estimate — exactly reproducing the original pipeline's output.
- **Result** — shown as an animated price "gauge" plus a summary of the inputs
  used, and is also saved to the signed-in user's history.
- **History** (`/history`) — a table/log of every valuation the user has run,
  most recent first.

## Notes / things you may want to adjust

- The gauge's full-scale reference value is ₹20,00,000, set in
  `static/js/main.js` (`MAX_REFERENCE`). Adjust if your typical predictions
  fall outside this range.
- `app.config['SECRET_KEY']` should be set via the `SECRET_KEY` environment
  variable in production.
- The year dropdown currently spans 1995 → current year; change `YEAR_RANGE`
  in `app.py` if your training data covers a different range.
- Predicted prices are clamped at a minimum of ₹0 in case the linear model
  extrapolates a negative value for unusual inputs.
