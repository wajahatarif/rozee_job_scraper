import streamlit as st
import pandas as pd
from rozee_scraper import scrape_rozee  # ✅ Import your function

st.set_page_config(page_title="Rozee Job Scraper", layout="centered")

st.title("📄 Rozee.pk Job Scraper")
st.write("Enter a job title to scrape the latest listings from Rozee.pk")

# Input field
keyword = st.text_input("🔍 Job Keyword", "python developer")

# Scrape button
if st.button("Scrape Jobs"):
    with st.spinner("Scraping in progress... please wait."):
        try:
            df = scrape_rozee(keyword)
            if not df.empty:
                st.success(f"✅ Scraped {len(df)} jobs for '{keyword}'")
                st.dataframe(df)

                # Optional download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download as CSV",
                    data=csv,
                    file_name="rozee_jobs.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No job data found.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
