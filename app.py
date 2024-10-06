import streamlit as st
import os
from dotenv import load_dotenv
from ai_coding_assistant import AICodingAssistant
from typing import Any, Dict, List

# Load environment variables
load_dotenv()

# Initialize the AICodingAssistant
ai_assistant = AICodingAssistant()

# Set page configuration
st.set_page_config(page_title="AI Coding Assistant", layout="wide")

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations: List[Dict[str, Any]] = []
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation: int | None = None
if "file_content" not in st.session_state:
    st.session_state.file_content: str | None = None
if "file_name" not in st.session_state:
    st.session_state.file_name: str | None = None
if "need_rerun" not in st.session_state:
    st.session_state.need_rerun: bool = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file: Any = None
if "show_file_uploader" not in st.session_state:
    st.session_state.show_file_uploader: bool = False
if "current_model" not in st.session_state:
    st.session_state.current_model: str = ai_assistant.get_current_model()
if "previous_input" not in st.session_state:
    st.session_state.previous_input: str = ""

# Custom CSS for styling
st.markdown("""
<style>
    /* ... (previous CSS remains unchanged) ... */
    
    .model-button {
        position: absolute;
        bottom: 5px;
        left: 5px;
        z-index: 1000;
    }
    .model-button button {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
        border-radius: 15px;
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d1d5db;
    }
    .model-button button:hover {
        background-color: #e5e7eb;
    }
    .model-icon {
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Function to detect input type
def detect_input_type(input_text: str, uploaded_file: Any) -> str:
    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'png']:
            return "Image"
        elif file_extension == 'mp4':
            return "Video"
        else:
            return "Text"
    elif input_text.startswith("http") and any(ext in input_text.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
        return "Image"
    elif "youtube.com" in input_text or "youtu.be" in input_text:
        return "Video"
    else:
        return "Text"

# Function to get the current model name
def get_current_model_name():
    return ai_assistant.get_current_model()

# Sidebar for conversation management
with st.sidebar:
    st.header("Tetika AI Assistant")
    # Button to start a new conversation
    if st.button("New Conversation", key="new_conv_button", help="Start a new conversation"):
        new_conv = {"title": "New Conversation", "messages": []}
        st.session_state.conversations.append(new_conv)
        st.session_state.current_conversation = len(st.session_state.conversations) - 1
        st.session_state.need_rerun = True

    st.markdown('<div class="conversation-history">', unsafe_allow_html=True)
    st.subheader("Conversation History")
    # Display existing conversations
    for i, conv in enumerate(st.session_state.conversations):
        if st.button(conv["title"], key=f"conv_{i}"):
            st.session_state.current_conversation = i
            st.session_state.need_rerun = True

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"**Current Model:** {st.session_state.current_model}")

# Main chat interface
st.title("Tetika AI: Your Coding Assistant")
# Display current conversation messages
if st.session_state.current_conversation is not None:
    current_conv = st.session_state.conversations[st.session_state.current_conversation]
    for message in current_conv["messages"]:
        with st.chat_message(message["role"]):
           if isinstance(message["content"], dict) and "model" in message["content"] and "content" in message["content"]:
                st.write(f"[{message['content']['model']}]")
                st.write(f"{message['content']['content']}")
           else:
               st.write(message["content"])

# Unified input area at the bottom
col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

with col1:
    user_input = st.text_area("Type your message, paste an image URL, or enter a YouTube video URL (use @web for web search):", key="user_input", on_change=None)
    
    # Add the model button below the text area
    model_button_col, _ = st.columns([0.3, 0.7])
    with model_button_col:
        model_button = st.button(
            f"🤖 {st.session_state.current_model}",
            key="model_button",
            help="Change AI model"
        )

with col2:
    upload_button = st.button("➕", key="upload_button")

with col3:
    send_button = st.button("➤", key="send_button")

# Model selection modal
if model_button:
    st.session_state.show_model_selector = True

if st.session_state.get("show_model_selector", False):
    with st.form(key="model_selector_form"):
        st.subheader("Select LLM Model")
        available_models = ai_assistant.get_available_models()
        selected_model = st.selectbox("Choose a model", available_models, index=available_models.index(st.session_state.current_model))
        submit_button = st.form_submit_button("Confirm")
        
        if submit_button:
            ai_assistant.set_model(selected_model)
            st.session_state.current_model = selected_model
            st.session_state.show_model_selector = False
            st.success(f"Model changed to {selected_model}")
            st.rerun()
            
# File uploader logic
if upload_button:
    st.session_state.show_file_uploader = True

if st.session_state.show_file_uploader:
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "py", "java", "cpp", "html", "css", "js", "jpg", "png", "mp4"], key="file_uploader")
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"File uploaded: {uploaded_file.name}")
    elif st.session_state.uploaded_file:
        st.success(f"File uploaded: {st.session_state.uploaded_file.name}")

# Process user input
if send_button or (user_input and user_input != st.session_state.previous_input):
    process_input = True
else:
    process_input = False

if process_input:
    st.session_state.previous_input = user_input
    # Create a new conversation if none exists
    if st.session_state.current_conversation is None:
        new_conv = {"title": "New Conversation", "messages": []}
        st.session_state.conversations.append(new_conv)
        st.session_state.current_conversation = len(st.session_state.conversations) - 1

    current_conv = st.session_state.conversations[st.session_state.current_conversation]

    # Detect input type
    input_type = detect_input_type(user_input, st.session_state.uploaded_file)
    if input_type == "Text":
        if user_input or st.session_state.file_content:
            combined_input = f"User question: {user_input}\n\n"
            if st.session_state.file_content:
                combined_input += f"File content ({st.session_state.file_name}):\n{st.session_state.file_content}\n\n"

            if user_input.startswith("@web"):
                search_query = user_input[4:].strip()
                try:
                    search_results = ai_assistant.search_online(search_query)
                    response = "Web search results:\n\n"
                    for result in search_results:
                        response += f"**{result['title']}**\n{result['snippet']}\n[Link]({result['link']})\n\n"
                    response += f"\nBased on these search results, here's my analysis of your query '{search_query}':\n"
                            
                    ai_input = f"Web search query: {search_query}\n\nSearch results:\n{response}\n\nPlease analyze these results and provide insights."
                            
                    ai_response = ai_assistant.process_text_input(ai_input)
                            
                    if isinstance(ai_response, dict):
                        if "content" in ai_response:
                            response += ai_response["content"]
                        else:
                            response += str(ai_response)
                    else:
                        response += str(ai_response)
                except Exception as e:
                    st.error(f"An error occurred during web search: {str(e)}")
                    response = f"I'm sorry, but I encountered an error while processing your web search request. Error details: {str(e)}"
            else:
                response = ai_assistant.process_text_input(combined_input)

            current_conv["messages"].append({"role": "user", "content": user_input if user_input else f"Analyzing file: {st.session_state.file_name}"})
            current_conv["messages"].append({"role": "assistant", "content": response})

    # Update conversation title if it's the first message
    if len(current_conv["messages"]) == 2:  # First user message and AI response
        current_conv["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input

    # Clear the file content after processing
    st.session_state.file_content = None
    st.session_state.file_name = None
    st.session_state.need_rerun = True

# Rerun the app if needed
if st.session_state.need_rerun:
    st.session_state.need_rerun = False
    st.rerun()
