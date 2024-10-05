import streamlit as st
import os
from dotenv import load_dotenv
from ai_coding_assistant import AICodingAssistant
# Load environment variables
load_dotenv()

# Initialize the AICodingAssistant
ai_assistant = AICodingAssistant()

# Set page configuration
st.set_page_config(page_title="AI Coding Assistant", layout="wide")

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None
if "file_content" not in st.session_state:
    st.session_state.file_content = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "need_rerun" not in st.session_state:
    st.session_state.need_rerun = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "show_file_uploader" not in st.session_state:
    st.session_state.show_file_uploader = False
# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    .stButton>button {
        border-radius: 50%;
        height: 3em;
        width: 3em;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextArea textarea {
        border-radius: 10px;
    }
    .stSidebar .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    .send-button {
        border-radius: 50% !important;
        width: 3em !important;
        height: 3em !important;
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .send-button:hover {
        background-color: #45a049 !important;
    }
    .hidden {
        display: none;
    }
    .new-conversation-btn {
        width: 100% !important;
        border-radius: 20px !important;
        margin-bottom: 20px !important;
    }
    .conversation-history {
        margin-top: 20px;
        border-top: 1px solid #e0e0e0;
        padding-top: 20px;
    }
</style>
""", unsafe_allow_html=True)
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
# Main chat interface
st.title("Tetika AI: Your Coding Assistant")

# Display current conversation messages
if st.session_state.current_conversation is not None:
    current_conv = st.session_state.conversations[st.session_state.current_conversation]
    for message in current_conv["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Function to detect input type
def detect_input_type(input_text, uploaded_file):
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

# Unified input area at the bottom
col1, col2, col3 = st.columns([0.85, 0.075, 0.075])

with col1:
    user_input = st.text_area("Type your message, paste an image URL, or enter a YouTube video URL (use @web for web search):", key="user_input")

with col2:
    upload_button = st.button("➕", key="upload_button")

with col3:
    send_button = st.button("➤", key="send_button")
    st.markdown(
        """
        <script>
            var send_button = document.querySelector('button[kind="secondary"]:not(.stDownloadButton)');
            send_button.innerHTML = '<i class="fas fa-paper-plane"></i>';
            send_button.classList.add('send-button');
            
            var new_conv_button = document.querySelector('.stButton button');
            new_conv_button.classList.add('new-conversation-btn');
        </script>
        """,
        unsafe_allow_html=True
    )

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

if send_button or (user_input and user_input != st.session_state.get("previous_input", "")):
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
                search_results = ai_assistant.search_online(search_query)
                response = "Web search results:\n\n"
                for result in search_results:
                    response += f"**{result['title']}**\n{result['snippet']}\n[Link]({result['link']})\n\n"
                response += f"\nBased on these search results, here's my analysis of your query '{search_query}':\n"
                response += ai_assistant.process_text_input(combined_input + response)
            else:
                response = ai_assistant.process_text_input(combined_input)
            
            current_conv["messages"].append({"role": "user", "content": user_input if user_input else f"Analyzing file: {st.session_state.file_name}"})
            current_conv["messages"].append({"role": "assistant", "content": response})
        else:
            st.warning("Please provide input or upload a file.")
    elif input_type == "Image":
        image_path = user_input if user_input.startswith("http") else st.session_state.uploaded_file
        if image_path:
            combined_input = f"Image: {image_path}\nUser question: Analyze this image"
            response = ai_assistant.process_image_input(image_path, combined_input)
            current_conv["messages"].append({"role": "user", "content": f"Image: {image_path}"})
            current_conv["messages"].append({"role": "assistant", "content": response})
        else:
            st.warning("Please provide a valid image URL or upload an image file.")
    elif input_type == "Video":
        video_url = user_input
        if video_url:
            combined_input = f"Video URL: {video_url}\nUser question: Analyze this video"
            response = ai_assistant.process_video_input(video_url, combined_input)
            current_conv["messages"].append({"role": "user", "content": f"Video URL: {video_url}"})
            current_conv["messages"].append({"role": "assistant", "content": response})
        else:
            st.warning("Please provide a valid YouTube video URL.")

    # Update conversation title if it's the first message
    if len(current_conv["messages"]) == 2:  # First user message and AI response
        current_conv["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input

    # Clear the file content after processing
    st.session_state.file_content = None
    st.session_state.file_name = None
    st.session_state.need_rerun = True
# Check if we need to rerun the app
if st.session_state.need_rerun:
    st.session_state.need_rerun = False
    st.rerun()
