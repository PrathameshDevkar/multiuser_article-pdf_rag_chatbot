import streamlit as st
import requests

"""
Frontend built using Streamlit:
- Login / Register with JWT
- Upload PDF or URL
- Chat using the multi-user RAG backend
"""


API_BASE = "here add the url where the backend is running"

st.title("🧠 Multi-User Research RAG Chatbot")

if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # list of dicts [{"user": "...", "ai": "..."}]

tab1, tab2, tab3 = st.tabs(["🔐 Login / Register", "📄 Upload PDF / URL", "💬 Chat"])

# --- Login / Register ---
with tab1:
    st.header("🔐 Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = requests.post(f"{API_BASE}/register", data={"username": username, "password": password})
        st.write(res.json())
    if st.button("Login"):
        res = requests.post(f"{API_BASE}/login", data={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json()["access_token"]
            st.session_state["token"] = token
            st.session_state["username"] = username
            st.success("Login successful ✅")
        else:
            st.error("Login failed ❌")

"""
Important: Streamlit runs top-to-bottom each interaction; 
button presses cause a rerun. 
Storing token in session_state preserves it across reruns."""

# --- Upload URL ---
with tab2:
    st.header("📄 Upload Research Article or PDF")

    if not st.session_state["token"]:
        st.warning("Please login first.")
    else:
        upload_type = st.radio("Select upload type:", ["Upload PDF", "Upload URL"])

        if upload_type == "Upload PDF":
                    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
                    print('==================uploaded file is',uploaded_file)
                    print('===========================')
                    if uploaded_file:
                        if st.button("📤 Upload PDF"):
                            with st.spinner("Uploading and processing PDF..."):
                                try:
                                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                                    data = {"token": st.session_state["token"]}
                                    res = requests.post(f"{API_BASE}/upload_pdf", data=data,files=files )
                                    if res.status_code == 200:
                                        st.success(res.json().get("message", "PDF processed successfully"))
                                    else:
                                        st.error(res.json().get("detail", "Failed to upload PDF"))
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            
        else:  # Upload URL
            url = st.text_input("Enter article URL")
            if st.button("🌐 Upload URL"):
                with st.spinner("Fetching and processing URL..."):
                    try:
                        data = {"token": st.session_state["token"], "url": url}
                        res = requests.post(f"{API_BASE}/upload_url", data=data)
                        if res.status_code == 200:
                            st.success(res.json().get("message", "URL processed successfully"))
                        else:
                            st.error(res.json().get("detail", "Failed to upload URL"))
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        
# --- Chatbot ---
with tab3:
    st.header(f"💬 Chat as {st.session_state['username'] or 'Guest'}")

    if not st.session_state["token"]:
        st.warning("Please login first.")
    else:
        # Display previous chat history
        for chat in st.session_state["chat_history"]:
            st.markdown(f"**👤 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['ai']}")
            st.markdown("---")
            
        query = st.text_input("Ask a question:")
        if st.button("Send"):
            if not query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        data = {"token": st.session_state["token"], "query": query}
                        res = requests.post(f"{API_BASE}/chat", data=data)

                        if res.status_code == 200:
                            ai_response = res.json()["response"]
                            st.session_state["chat_history"].append(
                                {"user": query, "ai": ai_response}
                            )
                            st.success("Response received ✅")

                            # Immediately show new chat
                            st.markdown(f"**👤 You:** {query}")
                            st.markdown(f"**🤖 AI:** {ai_response}")
                            st.markdown("---")

                        else:
                            st.error(res.json().get("detail", "Error from server."))

                    except Exception as e:
                        st.error(f"❌ Error: {e}")