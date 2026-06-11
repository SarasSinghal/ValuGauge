# 🚗 ValuGauge – AI-Powered Used Car Price Prediction Platform
Website Link-https://valugauge.onrender.com/login
#ValuGauge is a full-stack Machine Learning web application that predicts the resale value of used cars based on key vehicle attributes such as manufacturer, model, year of purchase, fuel type, and kilometers driven.

The platform combines a trained Machine Learning regression model with a modern Flask-based web application, allowing users to instantly estimate the market value of their vehicles through an intuitive and user-friendly interface.

---

## 🌟 Features

### Vehicle Price Prediction

* Predicts second-hand car prices using a trained Machine Learning model.
* Provides real-time valuation based on vehicle specifications.
* Supports multiple manufacturers and car models.

### Secure User Authentication

* User registration and login system.
* Password hashing for enhanced security.
* Personalized access to valuation history.

### Prediction History

* Stores all previous predictions.
* Enables users to review past vehicle valuations.
* Maintains a dedicated history dashboard for each user.

### Dynamic User Experience

* Responsive and modern user interface.
* Interactive price visualization gauge.
* Dynamic model selection based on manufacturer.

### Database Integration

* SQLite database for user and prediction storage.
* Persistent records across sessions.

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Flask
* Flask-Login
* Flask-SQLAlchemy

### Machine Learning

* Python
* NumPy
* Scikit-Learn

### Database

* SQLite

### Deployment Ready

* Environment Variable Support
* Modular Project Structure
* Lightweight Flask Architecture

---

## 📊 Model Performance

The machine learning model was evaluated using the coefficient of determination (**R² Score**), which measures how well the predicted values match the actual market prices.

| Metric   | Value     |
| -------- | --------- |
| R² Score | **0.841** |

### Interpretation

An R² score of **0.841** indicates that the model explains approximately **84.1% of the variance** in used car prices, demonstrating strong predictive capability on the dataset.

This performance suggests that the selected features—such as company, model, year, fuel type, and kilometers driven—capture most of the factors influencing vehicle resale value.

---

## 📈 Machine Learning Workflow

### Data Preprocessing

* Data Cleaning
* Handling Missing Values
* Feature Selection
* Categorical Encoding

### Feature Engineering

The model uses the following features:

| Feature           | Description                       |
| ----------------- | --------------------------------- |
| Company           | Vehicle Manufacturer              |
| Model             | Vehicle Model                     |
| Year              | Manufacturing / Registration Year |
| Kilometers Driven | Total Distance Covered            |
| Fuel Type         | Petrol, Diesel, LPG, etc.         |

### Model Training

* Linear Regression Algorithm
* One-Hot Encoding for categorical variables
* Model trained on historical used-car market data

### Prediction Pipeline

1. User enters vehicle details.
2. Features are validated and encoded.
3. The trained model processes the inputs.
4. Predicted resale value is generated.
5. Results are displayed to the user and stored in prediction history.

---

## 📂 Project Structure

```text
ValuGauge/
│
├── app.py
├── requirements.txt
│
├── model/
│   ├── model_weights.json
│   ├── company_models.json
│   └── categories.json
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── predict.html
│   ├── history.html
│   └── 404.html
│
├── static/
│   ├── css/
│   └── js/
│
└── instance/
    └── carprice.db
```

---

## 🎯 Learning Outcomes

Through this project, I gained practical experience in:

* End-to-End Machine Learning Development
* Data Cleaning and Feature Engineering
* Regression Modeling
* Flask Web Development
* Database Management
* User Authentication and Authorization
* Full-Stack Application Development
* Machine Learning Model Deployment
* Software Project Structuring and Organization

---

## 🚀 Key Highlights

* Built a complete end-to-end Machine Learning application for used car price prediction.
* Achieved an **R² Score of 0.841** on the testing dataset.
* Implemented secure user authentication and prediction history tracking.
* Developed a responsive and professional web interface using Flask.
* Integrated Machine Learning predictions with a production-style web application.
* Designed with scalability and deployment readiness in mind.
