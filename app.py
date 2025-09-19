import streamlit as st
import pandas as pd
import google.generativeai as genai

# Helper function for safe data loading
@st.cache_data
def load_data():
    try:
        # Relative path; place "Master Dataset.xlsx" in the same folder as your script
        df = pd.read_excel("Master Dataset.xlsx")
        return df, None
    except Exception as e:
        return None, str(e)

# Use Streamlit secrets to get your API key (ensure it's added to .streamlit/secrets.toml)
API_KEY = st.secrets.get("GOOGLE_API_KEY")
if not API_KEY:
    st.error("⚠️ Please set your GOOGLE_API_KEY in .streamlit/secrets.toml or Streamlit Cloud Secrets.")
else:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

# UI TITLE and description
st.markdown("<h1 style='color:#6C63FF;'><b>🎯 AI Career & Skills Advisor</b></h1>", unsafe_allow_html=True)
st.success("Get **personalized career guidance** based on your domain, courses, and interests.")

# Automatically load the data in the background
df, data_error = load_data()
if data_error:
    st.error(f"❌ Error loading dataset: {data_error}")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Select Your Domain", sorted(df["Domain"].unique()))
with col2:
    degree_status = st.selectbox("Current Degree Status", ["Undergraduate", "Graduate", "Postgraduate", "Other"])

extra_courses = st.text_input("📚 Extra Courses (comma-separated)").strip()
special_topics = st.text_area("✨ Special Interest Topics (comma-separated)").strip()

is_ready = domain and degree_status
if st.button("🔍 Get Career Suggestions", disabled=not is_ready):
    with st.spinner("Analyzing your profile and generating creative suggestions..."):
        try:
            domain_data = df[df["Domain"] == domain].head(3).to_dict(orient="records")
            prompt = f"""
You are a modern, creative AI Career Advisor for technical professionals in India.
Based on this user's profile:
- Domain: {domain}
- Degree Status: {degree_status}
- Extra Courses: {extra_courses}
- Special Topics: {special_topics}
Limited dataset context for this domain:
{domain_data}
Please respond in engaging, creative markdown with:
1. **Potential Career Scopes** (with relevant emojis)
2. **A visually-friendly Step-by-Step Roadmap** (use emojis for each phase)
3. **Alternative Career Routes/Ideas**
4. **Recommended Learning Resources/Platforms** (with icons or symbols)
5. **Salary/Job Market Trend Insights** (present highlights or use colored text)
Use bold, sections, lists, emojis, and color for visual appeal.
            """
            response = model.generate_content(prompt)
            st.markdown("## 📌 <span style='color:#3BC14A'><b>Creative Career Suggestions</b></span>", unsafe_allow_html=True)
            with st.expander("See your tailored roadmap and advice 🚀", expanded=True):
                # Show the model's creative markdown
                st.markdown(response.text or "No response from model. Try revising your input.", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error from the AI model: {e}")
