import streamlit as st
import os
from dotenv import load_dotenv
from src.parser.pdf_parser import extract_pdf_text
from src.parser.youtube_parser import extract_youtube_transcript
from src.parser.news_parser import extract_news_content
from src.llm.summarizer import summarize_text
from src.llm.ner_sentiment import analyze_text
from src.llm.insight_gen import generate_insights
from src.llm.answer_followup import answer_followup_question


st.set_page_config(page_title="ScopeAI – Multi-Source Insight Generator", layout="wide")

# Load environment variables from .env file
load_dotenv()

def load_css():
    with open("assets/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


load_css()


st.title("🌌 ScopeAI – Understand Anything in Seconds")

# Initialize session state to store results
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'entities' not in st.session_state:
    st.session_state.entities = None
if 'sentiment' not in st.session_state:
    st.session_state.sentiment = None
if 'insights' not in st.session_state:
    st.session_state.insights = None
if 'raw_text' not in st.session_state:
    st.session_state.raw_text = ""
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# Sidebar input options
st.sidebar.header("Choose your input type:")
input_type = st.sidebar.selectbox("Select Source", ["PDF", "YouTube", "News Article"])

# Add API key input in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ API Settings")

# Add a checkbox to toggle between default and custom API key
use_custom_key = st.sidebar.checkbox("Use my own OpenAI API key")

if use_custom_key:
    # Text input for API key with password masking
    api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password", 
                                    help="Your API key will not be stored and is only used for this session")
    
    # Set the API key in environment variable if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.sidebar.success("✅ API key set for this session")
    else:
        st.sidebar.warning("⚠️ Please enter a valid API key")
else:
    # Use the default API key from .env file
    st.sidebar.info("Using the default API key")
    
st.sidebar.markdown("""
<small>Get your API key from [OpenAI](https://platform.openai.com/api-keys)</small>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

if input_type == "PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        st.session_state.raw_text = extract_pdf_text(uploaded_file)

elif input_type == "YouTube":
    youtube_url = st.sidebar.text_input("Enter YouTube URL")
    if youtube_url:
        st.session_state.raw_text = extract_youtube_transcript(youtube_url)

elif input_type == "News Article":
    news_url = st.sidebar.text_input("Enter News Article URL")
    if news_url:
        st.session_state.raw_text = extract_news_content(news_url)

if st.session_state.raw_text:
    st.subheader("🔍 Extracted Raw Text")
    with st.expander("View Text"):
        st.write(st.session_state.raw_text[:3000] + "..." if len(st.session_state.raw_text) > 3000 else st.session_state.raw_text)

    if st.button("Generate Summary and Insights") or st.session_state.summary:
        # Only run analysis if not already in session state
        if not st.session_state.summary:
            with st.spinner("Analyzing..."):
                try:
                    with st.spinner("Generating summary..."):
                        st.session_state.summary = summarize_text(st.session_state.raw_text)
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
                    st.session_state.summary = "Error generating summary. Please check your API key and try again."
                analysis_result = analyze_text(st.session_state.raw_text)
                st.session_state.entities = analysis_result["entities"]
                st.session_state.sentiment = analysis_result["sentiment"]
                st.session_state.insights = generate_insights(st.session_state.summary)

        # Now display all results using session state variables
        st.subheader("📝 Summary")
        st.write(st.session_state.summary)

        st.subheader("🔎 Named Entities")
        if st.session_state.entities and len(st.session_state.entities) > 0:
            # Group entities by type
            entity_types = {}
            for entity_type, entities_list in st.session_state.entities.items():
                if entities_list:  # Only show entity types with actual entities
                    entity_types[entity_type] = entities_list
            
            if entity_types:
                tabs = st.tabs(list(entity_types.keys()))
                for i, (entity_type, tab) in enumerate(zip(entity_types.keys(), tabs)):
                    with tab:
                        # Create a grid layout for entities
                        cols = st.columns(3)
                        for j, entity in enumerate(entity_types[entity_type]):
                            with cols[j % 3]:
                                # Use different colors for different entity types
                                if entity_type == "PERSON":
                                    st.info(entity)
                                elif entity_type == "ORG" or entity_type == "ORGANIZATION":
                                    st.success(entity)
                                elif entity_type == "GPE" or entity_type == "LOC" or entity_type == "LOCATION":
                                    st.warning(entity)
                                elif entity_type == "DATE" or entity_type == "TIME":
                                    st.error(entity)
                                else:
                                    st.write(entity)
            else:
                st.write("No named entities detected in this content.")
        else:
            st.write("No named entities detected in this content.")

        st.subheader("😊 Sentiment")

        # Create columns for the two sentiment analyzers
        col1, col2 = st.columns(2)

        with col1:
            st.write("**TextBlob Analysis:**")
            tb_polarity = st.session_state.sentiment["textblob"]["polarity"]
            tb_subjectivity = st.session_state.sentiment["textblob"]["subjectivity"]
            
            # Display polarity with color and emotion
            polarity_color = "green" if tb_polarity > 0 else "red" if tb_polarity < 0 else "gray"
            polarity_emotion = "Positive 😊" if tb_polarity > 0.3 else "Negative ☹️" if tb_polarity < -0.3 else "Neutral 😐"
            
            st.markdown(f"Polarity: <span style='color:{polarity_color}'>{tb_polarity:.2f}</span> ({polarity_emotion})", unsafe_allow_html=True)
            st.progress(tb_subjectivity)
            st.write(f"Subjectivity: {tb_subjectivity:.2f} (Objective ↔️ Subjective)")

        with col2:
            st.write("**VADER Analysis:**")
            vader = st.session_state.sentiment["vader"]
            compound = vader["compound"]
            
            # Display sentiment distribution
            st.write("Sentiment Distribution:")
            
            # Create a horizontal stacked bar
            sentiment_data = {
                "Positive": vader["pos"] * 100,
                "Neutral": vader["neu"] * 100,
                "Negative": vader["neg"] * 100
            }
            
            # Display compound score with emotion
            compound_color = "green" if compound > 0.05 else "red" if compound < -0.05 else "gray"
            compound_emotion = "Positive 😊" if compound > 0.05 else "Negative ☹️" if compound < -0.05 else "Neutral 😐"
            
            st.markdown(f"Overall: <span style='color:{compound_color}'>{compound:.2f}</span> ({compound_emotion})", unsafe_allow_html=True)
            
            # Create a chart for sentiment distribution
            st.bar_chart(sentiment_data)

        st.subheader("💡 Suggested Insights")

        # Display topics in a more visual way
        if st.session_state.insights["topics"]:
            st.write("**Topics Identified:**")
            cols = st.columns(min(3, len(st.session_state.insights["topics"])))
            for i, topic in enumerate(st.session_state.insights["topics"]):
                with cols[i % 3]:
                    st.info(topic)
        else:
            st.write("**Topics Identified:** None found")

        # Display follow-up questions in an interactive way
        st.write("**Follow-up Questions:**")
        for i, question in enumerate(st.session_state.insights["follow_up_questions"]):
            with st.expander(question):
                # Check if we already have an answer
                if f"q_{i}" in st.session_state.answers:
                    st.write(st.session_state.answers[f"q_{i}"])
                else:
                    if st.button(f"Answer this question", key=f"btn_q_{i}"):
                        with st.spinner("Generating answer..."):
                            answer = answer_followup_question(question, st.session_state.raw_text)
                            # Store answer in session state
                            st.session_state.answers[f"q_{i}"] = answer
                            st.write(answer)
else:
    st.info("Please upload a file or enter a valid URL to begin.")


