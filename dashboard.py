import streamlit as st
from supabase import create_client, Client
import urllib.parse

# 1. Config & Style Bordeaux
st.set_page_config(page_title="Livreur Pro Dashboard", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; color: white; }}
    .stButton>button {{
        background-color: #700D02; color: white;
        border-radius: 10px; border: none; height: 3em; width: 100%;
    }}
    .order-card {{
        background-color: #1c1c1c; padding: 20px;
        border-radius: 15px; border-left: 6px solid #700D02;
        margin-bottom: 15px;
    }}
    /* Style pour le lien WhatsApp en bouton vert */
    .wa-button {{
        background-color: #25D366; color: white;
        padding: 10px; border-radius: 10px; text-decoration: none;
        display: inline-block; text-align: center; width: 100%;
        font-weight: bold; margin-bottom: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Connexion
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=50)
st.sidebar.title("Accès Vendeur")
vendeur_phone = st.sidebar.text_input("Numéro WhatsApp Vendeur")

if vendeur_phone:
    st.title(f"📦 Vos Livraisons")
    
    try:
        # Récupération des données sans le debug st.write
       response = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order('created_at', desc=True).execute()
        orders = response.data

        if not orders:
            st.info("Aucune commande trouvée.")
        else:
            for order in orders:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="order-card">
                            <h3 style='margin:0;'>👤 {order['nom_client'] or 'Client Inconnu'}</h3>
                            <p style='font-size:1.1em;'>📍 <b>Quartier :</b> {order['quartier']}<br>
                            🛍️ <b>Articles :</b> {order['articles']}<br>
                            💰 <b>Prix :</b> {order['prix']} FCFA</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # --- BOUTON WHATSAPP CLIENT ---
                        # On prépare le message automatique
                        msg = urllib.parse.quote(f"Bonjour {order['nom_client']}, je vous contacte concernant votre commande de {order['articles']}.")
                        wa_url = f"https://wa.me/{order['telephone']}?text={msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">💬 WhatsApp Client</a>', unsafe_allow_html=True)

                        # --- BOUTON STATUT ---
                        if order['statut'] == 'À livrer':
                            if st.button(f"Livré ✅", key=f"btn_{order['id']}"):
                                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                                st.rerun()
                        else:
                            st.success("Terminé")

    except Exception as e:
        st.error(f"Erreur : {e}")
else:
    st.markdown("## 👋 Entrez votre numéro à gauche pour commencer.")
