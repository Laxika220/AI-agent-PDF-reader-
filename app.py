import streamlit as st
import PyPDF2
import requests
from typing import List, Dict

st.set_page_config(page_title="AI PDF Reader", page_icon="📚", layout="wide")

class PDFProcessor:
    @staticmethod
    def extract_text(pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text += f"[Page {page_num + 1}]\n{extracted}\n\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return ""

class OllamaAssistant:
    def __init__(self, model_name="llama3:latest"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.api_url = f"{self.base_url}/api/generate"
    
    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def chat(self, user_query, pdf_context=""):
        try:
            if len(pdf_context) > 3000:
                pdf_context = pdf_context[:3000] + "\n[Document truncated...]"
            
            if pdf_context:
                prompt = f"""Answer the question based on this document:

DOCUMENT:
{pdf_context}

QUESTION: {user_query}

ANSWER:"""
            else:
                prompt = user_query
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300,
                    "top_k": 40,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated').strip()
            else:
                return f"❌ Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "⏰ Timeout! The model is taking too long. Try:\n1. Using 'gemma3:1b' model (faster)\n2. Asking a shorter question\n3. Running: ollama run llama3 'test' in terminal first"
        except requests.exceptions.ConnectionError:
            return "❌ Can't connect to Ollama. Run: ollama serve"
        except Exception as e:
            return f"❌ Error: {str(e)}"

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pdf_texts' not in st.session_state:
        st.session_state.pdf_texts = []
    if 'pdf_names' not in st.session_state:
        st.session_state.pdf_names = []
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "gemma3:1b"

def main():
    initialize_session_state()
    
    with st.sidebar:
        st.title("📄 Upload PDFs")
        
        ai = OllamaAssistant()
        
        if ai.check_connection():
            st.success("✅ Ollama Connected")
        else:
            st.error("⚠️ Ollama not running")
            st.info("Run in terminal: ollama serve")
        
        models = ai.get_available_models()
        if models:
            default_model = "gemma3:1b" if "gemma3:1b" in models else models[0]
            try:
                default_index = models.index(default_model)
            except:
                default_index = 0
            
            st.session_state.selected_model = st.selectbox(
                "🤖 Model", 
                models,
                index=default_index,
                help="gemma3:1b is fastest!"
            )
        
        st.divider()
        
        uploaded_files = st.file_uploader("Choose PDFs", type="pdf", accept_multiple_files=True)
        
        if uploaded_files and st.button("🔄 Process", use_container_width=True):
            with st.spinner("Processing..."):
                st.session_state.pdf_texts = []
                st.session_state.pdf_names = []
                processor = PDFProcessor()
                for pdf_file in uploaded_files:
                    text = processor.extract_text(pdf_file)
                    if text:
                        st.session_state.pdf_texts.append(text)
                        st.session_state.pdf_names.append(pdf_file.name)
                if st.session_state.pdf_texts:
                    st.success(f"✅ Processed {len(st.session_state.pdf_texts)} PDF(s)")
                    st.session_state.messages = []
        
        if st.session_state.pdf_names:
            st.divider()
            st.write("📚 Loaded:")
            for name in st.session_state.pdf_names:
                st.write(f"• {name}")
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.pdf_texts = []
                st.session_state.pdf_names = []
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        st.markdown("### 💡 Tips")
        st.write("• First question takes 30-60s")
        st.write("• Use gemma3:1b for speed")
        st.write("• llama3 for quality")
    
    st.title("🤖 AI PDF Reader")
    st.write("Ask questions about your PDFs - Free & Private!")
    
    for msg in st.session_state.messages:
        with st.container():
            if msg["role"] == "user":
                st.markdown(f"**🧑 You:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI:** {msg['content']}")
    
    user_input = st.chat_input("Ask a question...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        status_text = st.empty()
        status_text.info("🤔 Thinking... (first question takes 30-60 seconds)")
        
        pdf_context = ""
        if st.session_state.pdf_texts:
            pdf_context = "\n\n".join(st.session_state.pdf_texts)
        
        ai = OllamaAssistant(st.session_state.selected_model)
        response = ai.chat(user_input, pdf_context)
        
        status_text.empty()
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()