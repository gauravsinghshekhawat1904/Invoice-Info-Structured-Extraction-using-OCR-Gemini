import streamlit as st
from PIL import Image
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import io
import pytesseract
from dotenv import load_dotenv
import os
import re 
import google.generativeai as genai

load_dotenv()

# Your API Key


# Instead of typing the "AIza..." key here, we pull it from Streamlit's Secrets
#if "GOOGLE_API_KEY" in st.secrets:
 #   google_api_key = st.secrets["GOOGLE_API_KEY"]
#else:
#    st.error("API Key not found in Secrets!")
#    st.stop()

# 2. Configure the library
#genai.configure(api_key=google_api_key)

# 1. FIXED: Added the -preview suffix for 2026 model access
llm = ChatGoogleGenerativeAI(
   # google_api_key=google_api_key,
    model="gemini-3-flash-preview", 
    temperature=0, 
    max_output_tokens=8192,
    model_kwargs={"response_mime_type": "application/json"}
)

# 2. FIXED: Robust function to handle both string and list-based responses
def clean_json_string(ai_response_content):
    # If the AI sends back a list (new 2026 format), join the text parts
    if isinstance(ai_response_content, list):
        full_text = "".join([part.get('text', '') for part in ai_response_content if isinstance(part, dict)])
    else:
        full_text = str(ai_response_content)
    
    # This finds the actual JSON part { ... } and ignores any other talk or "extras"
    match = re.search(r'\{.*\}', full_text, re.DOTALL)
    if match:
        return match.group(0)
    return full_text

def extract_text_from_file(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        gray_image = image.convert("L")
        extracted_text = pytesseract.image_to_string(gray_image).strip()
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None

# --- UI Setup ---
st.set_page_config(page_title="Invoice Information Extractor", layout="wide")
st.title("📑 Invoice Information Extractor")

uploaded_file = st.file_uploader("Upload an Invoice Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Invoice", use_column_width=True)

    if st.button("Extract Information"):
        with st.spinner("Step 1: Reading text from image..."):
            extracted_text = extract_text_from_file(uploaded_file)

        if extracted_text:
            st.subheader("🔎 OCR Extracted Text:")
            st.text(extracted_text)

            #st.subheader("🤖 Step 2: Processing with Gemini AI...")
            
            #*prompt = f"""
            #Extract the following from the text into a JSON object:
           # - Invoice Number
           # - Date
           # - Total Amount
           # - Vendor Name
           # - Items list (description and price)

           # Text: {extracted_text}
           # """

           try:
                response = llm.invoke(prompt)
                
                # 3. FIXED: Get the cleaned JSON string correctly
               # clean_json = clean_json_string(response.content)
                
               # json_data = json.loads(clean_json)

                st.success("✅ Success! Data Extracted.")
                st.subheader("📋 Final Results:")
               # st.json(json_data)

              #  st.download_button(
               #     label="💾 Download JSON Result",
               #     data=json.dumps(json_data, indent=4),
               #     file_name="invoice_data.json",
               #     mime="application/json"
             #   )

        #    except json.JSONDecodeError:
           #     st.error("AI output was not in a valid JSON format. Try again.")
            except Exception as e:
                # This catches the 404 or other API errors
                st.error(f"Error in Step 2: {str(e)}")
