"""
Core utility functions for PDF processing and AI interactions
"""
import PyPDF2
import os
from typing import List, Dict, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class PDFExtractor:
    """Handles PDF text extraction with error handling"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """
        Extracts text from an uploaded PDF file.
        
        Args:
            pdf_file: File-like object or path to PDF
            
        Returns:
            str: Extracted text from PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            return "\n\n".join(text_parts).strip()
        
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def get_pdf_metadata(pdf_file) -> Dict:
        """Extract metadata from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata = pdf_reader.metadata or {}
            
            return {
                "title": metadata.get("/Title", "Unknown"),
                "author": metadata.get("/Author", "Unknown"),
                "pages": len(pdf_reader.pages),
                "creator": metadata.get("/Creator", "Unknown")
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {"error": str(e)}


class TextProcessor:
    """Handles text processing and chunking"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunks.append(text[start:end])
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    @staticmethod
    def get_text_stats(text: str) -> Dict:
        """Get statistics about the text"""
        words = text.split()
        return {
            "characters": len(text),
            "words": len(words),
            "lines": text.count('\n'),
            "paragraphs": len([p for p in text.split('\n\n') if p.strip()])
        }


class AIClient:
    """Wrapper for Azure OpenAI client with better error handling"""
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_API_KEY')
        self.endpoint = os.getenv('AZURE_ENDPOINT')
        self.api_version = os.getenv('AZURE_API_VERSION', '2024-02-15-preview')
        self.model_name = os.getenv('MODEL_NAME', 'gpt-4')
        
        if not all([self.api_key, self.endpoint]):
            raise ValueError("Azure OpenAI credentials not configured. Check .env file.")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
    
    def get_system_prompt(self) -> str:
        """Returns the default system prompt for PDF Q&A"""
        return """You are an intelligent PDF assistant with the following capabilities:

1. **Answer Questions**: Provide accurate answers based on the PDF content
2. **Cite Sources**: Reference specific sections or pages when answering
3. **Summarize**: Create concise summaries of document sections
4. **Extract Information**: Find and extract specific data points
5. **Compare**: Compare information across multiple documents

Guidelines:
- Always base answers on the provided PDF content
- If information is not in the document, clearly state: "This information is not available in the provided document(s)."
- Use markdown formatting for clarity (headers, lists, bold, etc.)
- Be concise but thorough
- Cite page numbers when possible

Remember: Your knowledge is limited to the provided PDF content only."""
    
    def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        """
        Send chat completion request
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Randomness in response (0-1)
            max_tokens: Maximum length of response
            
        Returns:
            AI response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise RuntimeError(f"AI request failed: {str(e)}")
    
    def ask_question(
        self,
        question: str,
        pdf_context: str,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Ask a question about PDF content
        
        Args:
            question: User's question
            pdf_context: Full or chunked PDF text
            chat_history: Previous conversation messages
            
        Returns:
            AI's answer
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"PDF Content:\n\n{pdf_context}"}
        ]
        
        # Add chat history (last 5 exchanges)
        if chat_history:
            messages.extend(chat_history[-10:])
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return self.chat_completion(messages)
    
    def summarize_pdf(self, pdf_text: str, max_length: int = 500) -> str:
        """Generate a summary of the PDF content"""
        messages = [
            {"role": "system", "content": "You are a document summarization expert. Create concise, informative summaries."},
            {"role": "user", "content": f"Summarize the following document in approximately {max_length} words:\n\n{pdf_text}"}
        ]
        
        return self.chat_completion(messages, temperature=0.5, max_tokens=max_length * 2)


class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 20):
        self.messages: List[Dict] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.messages.append({"role": role, "content": content})
        
        # Trim history if too long
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.messages.copy()
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
    
    def get_summary(self) -> str:
        """Get a text summary of the conversation"""
        summary = []
        for msg in self.messages:
            role = msg['role'].upper()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary.append(f"{role}: {content}")
        return "\n".join(summary)


# Convenience functions for backward compatibility
def extract_text_from_pdf(pdf_file) -> str:
    """Legacy function - extract text from PDF"""
    return PDFExtractor.extract_text_from_pdf(pdf_file)


def get_system_prompt() -> str:
    """Legacy function - get system prompt"""
    return AIClient().get_system_prompt()


def ask_question(messages: List[Dict], user_query: str) -> str:
    """Legacy function - ask a question"""
    try:
        client = AIClient()
        return client.chat_completion(messages + [{"role": "user", "content": user_query}])
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage
    print("PDF Processing Utilities")
    print("=" * 50)
    
    # Test text processing
    sample_text = "This is a sample text. " * 100
    processor = TextProcessor()
    stats = processor.get_text_stats(sample_text)
    print(f"Text stats: {stats}")
    
    chunks = processor.chunk_text(sample_text, chunk_size=200)
    print(f"Text chunked into {len(chunks)} parts")