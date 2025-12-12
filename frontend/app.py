# import streamlit as st
# import requests

# BACKEND_URL = "http://localhost:9000/chat"   # change if needed

# st.set_page_config(page_title="Loan AI Agent", layout="wide")

# st.title("💰 Loan AI Agent")
# st.write("Talk with your loan assistant powered by LLM + FastAPI.")

# # --- Session State for Chat ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []


# # ---------- SIDEBAR ----------
# st.sidebar.header("⚙️ Settings")



# # ---------- CHAT INTERFACE ----------
# st.subheader("💬 Chat")

# user_query = st.text_input("Enter your query:", key="user_input")

# if st.button("Send"):
#     if user_query.strip() == "":
#         st.warning("Please enter a query.")
#     else:

#         payload = {
#             "query": user_query
#         }

#         try:
#             response = requests.post(BACKEND_URL, json=payload)
#             data = response.json()

#             human_response = data.get("human_readable_response", "No response")

#             # Save to frontend chat history
#             st.session_state.messages.append(("user", user_query))
#             st.session_state.messages.append(("assistant", human_response))
            

#         except Exception as e:
#             st.error(f"Request failed: {e}")


# # ---------- DISPLAY CHAT ----------
# for role, msg in st.session_state.messages:
#     if role == "user":
#         st.markdown(f"**🧑 You:** {msg}")
#     else:
#         st.markdown(f"**🤖 Assistant:** {msg}")


# # ---------- DEBUG OUTPUT ----------
# with st.expander("🔍 Debug (Raw API Output)"):
#     if "data" in locals():
#         st.json(data)


import streamlit as st
import requests

BACKEND_URL = "http://localhost:9000/chat"  # change if needed

st.set_page_config(page_title="Loan AI Agent", layout="wide")

st.title("💰 Loan AI Agent")
st.write("Talk with your loan assistant powered by LLM + FastAPI.")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "last_response" not in st.session_state:
    st.session_state.last_response = {}  # store API response

# Function to handle sending message
def send_message():
    user_query = st.session_state.user_input
    if user_query.strip() == "":
        st.warning("Please enter a query.")
        return

    payload = {"query": user_query}
    try:
        response = requests.post(BACKEND_URL, json=payload)
        data = response.json()

        human_response = data.get("human_readable_response", "No response")

        # Save to frontend chat history
        st.session_state.messages.append(("user", user_query))
        st.session_state.messages.append(("assistant", human_response))

        # Save API response to session state
        st.session_state.last_response = data

        # Clear input
        st.session_state.user_input = ""

    except Exception as e:
        st.error(f"Request failed: {e}")

# ---------- CHAT INTERFACE ----------
st.subheader("💬 Chat")
st.text_input("Enter your query:", key="user_input", on_change=send_message)

# ---------- DISPLAY CHAT ----------
for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Assistant:** {msg}")

# ---------- DEBUG OUTPUT ----------
with st.expander("🔍 Debug (Raw API Output)"):
    st.json(st.session_state.last_response)