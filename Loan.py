import streamlit as st
import numpy as np
import pickle

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Loan Predictor", page_icon="💰", layout="wide")

# ------------------ PREMIUM CSS ------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Hide default */
#MainMenu, footer, header {visibility: hidden;}

/* Title */
.main-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #22c55e, #3b82f6, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 0 25px rgba(0,0,0,0.3);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Inputs */
input, div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 12px;
    border-radius: 12px;
    border: none;
    width: 100%;
    transition: 0.3s;
    box-shadow: 0 0 15px rgba(168,85,247,0.5);
}
.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(168,85,247,1);
}

/* Result */
.result-success {
    background: rgba(34,197,94,0.15);
    border: 1px solid #22c55e;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 1.2rem;
}
.result-error {
    background: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 1.2rem;
}

</style>
""", unsafe_allow_html=True)

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    try:
        with open("model.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("❌ model.pkl file not found")
        return None
    except EOFError:
        st.error("❌ model.pkl file is empty or corrupted")
        return None

model = load_model()

# ------------------ HEADER ------------------
st.markdown("<div class='main-title'>💰 Loan Prediction App</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
st.sidebar.header("📋 Applicant Details")

gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
married = st.sidebar.selectbox("Married", ["Yes", "No"])
dependents = st.sidebar.selectbox("Dependents", ["0", "1", "2", "3+"])
education = st.sidebar.selectbox("Education", ["Graduate", "Not Graduate"])
employed = st.sidebar.selectbox("Self Employed", ["Yes", "No"])
credit = st.sidebar.selectbox("Credit History", [1.0, 0.0])
area = st.sidebar.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])

# ------------------ CENTERED LAYOUT ------------------
col_left, col_main, col_right = st.columns([1,2,1])

with col_main:

    # Income Card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💼 Income Details")
    ApplicantIncome = st.number_input("Applicant Income", min_value=0)
    CoapplicantIncome = st.number_input("Coapplicant Income", min_value=0)
    st.markdown("</div>", unsafe_allow_html=True)

    # Loan Card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏦 Loan Details")
    LoanAmount = st.number_input("Loan Amount", min_value=0)
    Loan_Amount_Term = st.number_input("Loan Term (in days)", min_value=0)
    st.markdown("</div>", unsafe_allow_html=True)

    # Button
    predict_btn = st.button("🚀 Predict Loan Eligibility")

# ------------------ ENCODING ------------------
male = 1 if gender == "Male" else 0
married_yes = 1 if married == "Yes" else 0

dependents_1 = dependents_2 = dependents_3 = 0
if dependents == '1':
    dependents_1 = 1
elif dependents == '2':
    dependents_2 = 1
elif dependents == '3+':
    dependents_3 = 1

not_graduate = 1 if education == "Not Graduate" else 0
employed_yes = 1 if employed == "Yes" else 0

semiurban = urban = 0
if area == "Semiurban":
    semiurban = 1
elif area == "Urban":
    urban = 1

# ------------------ PREDICTION ------------------
if predict_btn:

    if model is None:
        st.stop()

    ApplicantIncome = max(ApplicantIncome, 1)
    CoapplicantIncome = max(CoapplicantIncome, 1)
    LoanAmount = max(LoanAmount, 1)
    Loan_Amount_Term = max(Loan_Amount_Term, 1)

    ApplicantIncomelog = np.log(ApplicantIncome)
    totalincomelog = np.log(ApplicantIncome + CoapplicantIncome)
    LoanAmountlog = np.log(LoanAmount)
    Loan_Amount_Termlog = np.log(Loan_Amount_Term)

    prediction = model.predict([[credit, ApplicantIncomelog, LoanAmountlog,
                                 Loan_Amount_Termlog, totalincomelog, male,
                                 married_yes, dependents_1, dependents_2,
                                 dependents_3, not_graduate, employed_yes,
                                 semiurban, urban]])

    st.markdown("### 📊 Result")

    if prediction[0] == "N":
        st.markdown("<div class='result-error'>❌ Not Eligible for Loan</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='result-success'>✅ Eligible for Loan 🎉</div>", unsafe_allow_html=True)

    st.balloons()