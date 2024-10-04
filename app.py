import streamlit as st
import os
from assistant import AICodingAssistant
from file_utils import select_image_from_folder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the AICodingAssistant
ai_assistant = AICodingAssistant()

# Set page configuration
st.set_page_config(page_title="AI Coding Assistant", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for chat history
with st.sidebar:
    st.header("Chat History")
    if st.session_state.messages:
        for i, message in enumerate(st.session_state.messages):
            st.text(f"{message['role']}: {message['content'][:50]}...")
    else:
        st.text("No messages yet.")

# Main chat interface
st.title("AI Coding Assistant")

# Input type selection
input_type = st.radio("Select input type:", ("Text", "Image", "Video"))

if input_type == "Text":
    # Text input
    user_input = st.text_area("Type your message here:", height=100)
    uploaded_file = st.file_uploader("Or choose a file", type=["txt", "py", "java", "cpp", "html", "css", "js"])
elif input_type == "Image":
    # Image input
    image_path = select_image_from_folder()
    if image_path:
        st.image(image_path, caption="Selected Image", use_column_width=True)
    user_input = None
    uploaded_file = None
elif input_type == "Video":
    # Video input
    video_url = st.text_input("Enter YouTube video URL:")
    user_input = None
    uploaded_file = None

# Send button
if st.button("Send"):
    if input_type == "Text" and user_input:
        # Process text input
        response = ai_assistant.process_text_input(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif input_type == "Text" and uploaded_file:
        # Process uploaded file
        file_contents = uploaded_file.read().decode("utf-8")
        response = ai_assistant.process_text_input(f"Analyze this code:\n\n{file_contents}")
        st.session_state.messages.append({"role": "user", "content": f"Uploaded file: {uploaded_file.name}"})
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif input_type == "Image" and image_path:
        # Process image input
        response = ai_assistant.process_image_input(image_path)
        st.session_state.messages.append({"role": "user", "content": f"Uploaded image: {os.path.basename(image_path)}"})
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif input_type == "Video" and video_url:
        # Process video input
        response = ai_assistant.process_video_input(video_url)
        st.session_state.messages.append({"role": "user", "content": f"Video URL: {video_url}"})
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("Please provide input based on the selected input type.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Add a search functionality
search_query = st.text_input("Search online:")
if st.button("Search"):
    if search_query:
        search_results = ai_assistant.search_online(search_query)
        st.subheader("Search Results:")
        for result in search_results:
            st.write(f"**{result['title']}**")
            st.write(result['snippet'])
            st.write(f"[Link]({result['link']})")
            st.write("---")