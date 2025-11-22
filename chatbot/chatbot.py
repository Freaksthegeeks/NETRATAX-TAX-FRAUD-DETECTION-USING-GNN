import streamlit as st
import pandas as pd
from groq import Groq  # changed from OpenAI -> Groq

# Configure Streamlit
st.set_page_config(page_title="GST Fraud Detection Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 GST Fraud Detection Chatbot")
st.info("Ask questions about GST invoices, companies, fraud, ITC claims, etc.")

# Load Data
@st.cache_data
def load_data():
    try:
        companies = pd.read_csv('data/companies.csv')
        invoices = pd.read_csv('data/invoices.csv')
        return companies, invoices
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

companies_df, invoices_df = load_data()

# Display Dataset Info
with st.sidebar:
    st.header("📊 Dataset Info")
    if companies_df is not None:
        st.write("**Companies:**", len(companies_df))
        if "location" in companies_df:
            st.write("**Locations:**", companies_df["location"].unique())
        if "is_fraud" in companies_df:
            st.write("**Fraud Labels:**", companies_df["is_fraud"].sum())
    if invoices_df is not None:
        st.write("**Invoices:**", len(invoices_df))
        if "amount" in invoices_df:
            st.write("**Total Value:**", f"₹{invoices_df['amount'].sum():,.2f}")
        if "itc_claimed" in invoices_df:
            st.write("**ITC Claims:**", invoices_df["itc_claimed"].sum())
    st.divider()
    st.write("💡 Examples:")
    st.markdown("""
    - Show top 5 companies with most invoices
    - List all invoices above ₹1,00,000
    - Which companies claimed the most ITC?
    - Show fraudulent companies
    - Fraud distribution by state
    """)

# Initialize Groq client (use GROQ_API_KEY in your Streamlit secrets)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question about your GST data...")

def get_statistics():
    stats = []
    if companies_df is not None and invoices_df is not None:
        stats.append(f"Companies: {len(companies_df)}")
        stats.append(f"Fraud Companies: {companies_df['is_fraud'].sum() if 'is_fraud' in companies_df else 0}")
        stats.append(f"Invoices: {len(invoices_df)}")
        stats.append(f"Total Invoice Value: ₹{invoices_df['amount'].sum():,.0f}" if "amount" in invoices_df else "")
        stats.append(f"ITC Claim Count: {invoices_df['itc_claimed'].sum() if 'itc_claimed' in invoices_df else 0}")
    return "\n".join(stats)

def get_chatbot_response(question):
    # System context for GPT
    context = (
        "You are a helpful GST fraud analyst assistant. "
        "Below is a summary of the current dataset. "
        "Answer using summary stats if exact data is unavailable.\n"
        + get_statistics()
    )
    messages = [
        {"role": "system", "content": context},
        *st.session_state.messages[-5:],  # up to last 5 messages for context
        {"role": "user", "content": question}
    ]
    # Use a Groq model name here — for example mixtral or llama family on Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # change if you prefer another Groq model
        messages=messages,
        temperature=0.2,
        max_tokens=500
    )
    # extract content (same shape as OpenAI compatibility)
    return response.choices[0].message.content

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            ai_response = get_chatbot_response(user_input)
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
