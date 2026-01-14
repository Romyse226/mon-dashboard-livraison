import streamlit as st
from supabase import create_client, Client

# 1. Config & Style Bordeaux
st.set_page_config(page_title="Livreur Pro Dashboard", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; color: white; }}
    .stButton>button {{
        background-color: #700D02; color: white;
        border-radius: 10px; border: none; height: 3em;
    }}
    .order-card {{
        background-color: #1c1c1c; padding: 20px;
        border-radius: 15px; border-left: 6px solid #700D02;
        margin-bottom: 15px;
    }}
    .stTextInput>div>div>input {{ background-color: #262730; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Connexion (Secrets Streamlit)
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Sidebar : Login via Numéro WhatsApp
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=50)
st.sidebar.title("Accès Vendeur")
vendeur_phone = st.sidebar.text_input("Entrez votre numéro WhatsApp (ex: 22507...)")

if vendeur_phone:
    st.title(f"📦 Commandes de {vendeur_phone}")
    
    # Récupération des commandes liées à ce numéro
    try:
        query = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).execute()
        st.write("Données reçues :", query.data) # Pour voir si les données arrivent
    except Exception as e:
        st.error(f"Détail de l'erreur : {e}") # Ceci nous dira ENFIN le vrai problème
else:
    st.markdown("""
    ## 👋 Bienvenue sur votre espace de livraison
    Veuillez entrer votre **numéro de téléphone professionnel** dans la barre latérale pour gérer vos commandes en temps réel.
    """)
