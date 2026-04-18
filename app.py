import streamlit as st
import pandas as pd
import os
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------- CONFIG -------------------
DATA_FILE = "data/lost_found_data.csv"
import os

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# ----------------------------------------------

st.set_page_config(page_title="Lost & Found", page_icon="💗", layout="wide")

# ------------------- CUSTOM CSS -------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5c4d8, #f0a7cb, #d989b6);
    color: #2d0f28;
}
[data-testid="stHeader"] {
    background-color: rgba(255, 255, 255, 0);
}
[data-testid="stSidebar"] {
    background-color: #b85a8f;
    color: white;
}
h1, h2, h3 {
    color: #7a0f4b;
    text-align: center;
}
.stButton>button {
    background-color: #e75480;
    color: white;
    border-radius: 15px;
    font-size: 16px;
    padding: 10px 20px;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #ff69b4;
}
div.stAlert > div {
    color: #fff;
    background-color: #b85a8f;
    border-radius: 10px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------------- FUNCTIONS -------------------
def send_email(to_email, item_name, found_by, contact_info):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = f"Good news! Your lost item '{item_name}' might be found 💌"

        body = f"""Hello there,

Someone has uploaded a found item that matches your lost item:
💗 Item Name: {item_name}
💗 Found by: {found_by}
💗 Contact: {contact_info}

Please reach out to confirm if it's yours!

With love,
Lost & Found System 💖
"""
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("Email sent successfully 💌")
    except Exception as e:
        st.error(f"Email sending failed: {e}")

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Type", "Item Name", "Description", "Contact", "Email", "Image"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def match_items(df, new_entry):
    if new_entry["Type"] == "Found":
        lost_items = df[df["Type"] == "Lost"]
        for _, row in lost_items.iterrows():
            if new_entry["Item Name"].strip().lower() in row["Item Name"].strip().lower():
                send_email(row["Email"], row["Item Name"], new_entry["Contact"], new_entry["Email"])
                st.success(f"Match found! Email sent to {row['Email']} 💌")
    elif new_entry["Type"] == "Lost":
        found_items = df[df["Type"] == "Found"]
        for _, row in found_items.iterrows():
            if new_entry["Item Name"].strip().lower() in row["Item Name"].strip().lower():
                send_email(new_entry["Email"], new_entry["Item Name"], row["Contact"], row["Email"])
                st.success(f"Possible match found! Email sent to {new_entry['Email']} 💌")

# ------------------- UI -------------------
st.title("💗 Lost & Found System 💗")


menu = st.sidebar.radio("Menu", ["Upload Item", "Search Items", "View All Items"])

if menu == "Upload Item":
    st.subheader("📤 Upload Lost or Found Item")

    t = st.selectbox("Type", ["Lost", "Found"])
    n = st.text_input("Item Name")
    d = st.text_area("Description")
    c = st.text_input("Your Name / Contact Info")
    e = st.text_input("Your Email ID")
    i = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png"])

    if st.button("Submit"):
        if n and d and c and e:
            img_path = ""
            if i:
                img_path = f"images/{i.name}"
                os.makedirs("images", exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(i.getbuffer())

            df = load_data()
            new_entry = {
                "Type": t,
                "Item Name": n,
                "Description": d,
                "Contact": c,
                "Email": e,
                "Image": img_path
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)

            match_items(df, new_entry)
            st.success("Item uploaded successfully 🎀")
        else:
            st.error("Please fill all required fields 🌸")

elif menu == "Search Items":
    st.subheader("🔍 Search Lost or Found Items")
    df = load_data()
    query = st.text_input("Enter item name or keyword to search")
    if query:
        results = df[df["Item Name"].str.contains(query, case=False, na=False)]
        if len(results) == 0:
            st.info("No matching items found 🩷")
        else:
            for _, row in results.iterrows():
                with st.expander(f"{row['Type']}: {row['Item Name']}"):
                    st.write(f"**Description:** {row['Description']}")
                    st.write(f"**Contact:** {row['Contact']}")
                    st.write(f"**Email:** {row['Email']}")
                    if row['Image'] and os.path.exists(row['Image']):
                        st.image(row['Image'], width=250)

elif menu == "View All Items":
    st.subheader("📜 List of Uploaded Items")
    df = load_data()
    if len(df) == 0:
        st.info("No items yet 🩷")
    else:
        for _, row in df.iterrows():
            with st.expander(f"{row['Type']}: {row['Item Name']}"):
                st.write(f"**Description:** {row['Description']}")
                st.write(f"**Contact:** {row['Contact']}")
                st.write(f"**Email:** {row['Email']}")
                if row['Image'] and os.path.exists(row['Image']):
                    st.image(row['Image'], width=250)
st.markdown(
    """
    <div style='text-align: center; margin-top: 40px; color: #7a0f4b; font-size: 16px;'>
        Made with 💗 by <b>Mallika Mathur</b> ✨
    </div>
    """,
    unsafe_allow_html=True
)
