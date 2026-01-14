import streamlit as st
from supabase import create_client, Client
import urllib.parse

# 1. Configuration de la page
st.set_page_config(page_title="Livreur Pro Elite", layout="wide")

# 2. Design CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #1a0301; border-right: 1px solid #700D02; }
    .order-card {
        background: linear-gradient(145deg, #1c1c1c, #0d0d0d);
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #700D02;
        margin-bottom: 15px;
    }
    .card-title { color: #FFFFFF; font-size: 1.2rem; font-weight: 700; }
    .stButton>button {
        background: linear-gradient(90deg, #700D02, #a31403);
        color: white; border-radius: 10px; border: none; width: 100%;
    }
    .wa-button {
        background: linear-gradient(90deg, #128C7E, #25D366);
        color: white; padding: 10px; border-radius: 10px;
        text-decoration: none; display: block; text-align: center;
        font-weight: 700; margin-bottom: 10px; font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Connexion Supabase
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 4. Sidebar
st.sidebar.title("🔑 Connexion")
vendeur_phone = st.sidebar.text_input("Numéro WhatsApp")

# 5. Logique Principale
if vendeur_phone:
    st.title("📦 Vos Commandes")
    try:
        # Requête
        res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order('created_at', desc=True).execute()
        orders = res.data

        if not orders:
            st.info("Aucune commande pour ce numéro.")
        else:
            for order in orders:
                col_info, col_btn = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
                    <div class="order-card">
                        <div class="card-title">👤 {order.get('nom_client', 'Client')}</div>
                        <p>📍 {order.get('quartier', 'Abidjan')} | 🛍️ {order.get('articles', 'Produit')}</p>
                        <p style='font-size:1.1rem;'>💰 <b>{order.get('prix', 0)} FCFA</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    # Bouton WhatsApp
                    c_phone = str(order.get('telephone', '')).replace(" ", "")
                    msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison.")
                    st.markdown(f'<a href="https://wa.me/{c_phone}?text={msg}" target="_blank" class="wa-button">💬 WHATSAPP</a>', unsafe_allow_html=True)
                    
                    # Bouton Statut
                    if order.get('statut') == 'À livrer':
                        if st.button("LIVRÉ ✅", key=f"btn_{order['id']}"):
                            supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                            st.rerun()
                    else:
                        st.success("Livré")
    except Exception as e:
        st.error(f"Erreur technique : {e}")
else:
    st.write("Veuillez entrer votre numéro dans la barre latérale.")
