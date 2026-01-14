import streamlit as st
from supabase import create_client, Client
import urllib.parse

# 1. Config & Design Elite
st.set_page_config(page_title="Mes Commandes - Livreur Pro", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: #0e1117; color: white; }}
    
    /* Login au centre */
    .login-container {{
        text-align: center;
        padding: 50px 20px;
        max-width: 400px;
        margin: 0 auto;
    }}
    
    /* Cartes de commande */
    .order-card {{
        background-color: #1c1c1c;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }}
    
    .status-badge {{
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 0.8em;
        font-weight: bold;
        text-transform: uppercase;
    }}
    
    /* Boutons */
    .stButton>button {{
        border-radius: 12px;
        font-weight: bold;
        transition: 0.3s;
    }}
    .btn-livrer {{ background-color: #700D02 !important; color: white !important; }}
    .btn-annuler {{ background-color: #333 !important; color: #aaa !important; }}
    
    /* WhatsApp Button */
    .wa-button {{
        background-color: #25D366; color: white;
        padding: 12px; border-radius: 12px; text-decoration: none;
        display: block; text-align: center; font-weight: bold;
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Connexion
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# 3. Logique de Session (pour rester connecté)
if 'vendeur_phone' not in st.session_state:
    st.session_state.vendeur_phone = ""

# 4. Interface de Bienvenue (CENTRE)
if not st.session_state.vendeur_phone:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=80)
    st.title("Livreur Pro")
    st.write("Entrez votre numéro WhatsApp pour voir vos commandes.")
    num = st.text_input("", placeholder="22507...", label_visibility="collapsed")
    if st.button("Se connecter", use_container_width=True):
        if num:
            st.session_state.vendeur_phone = num
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. Dashboard Connecté
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.title("📋 Mes Commandes")
    with col_t2:
        if st.button("Déconnexion 🚪"):
            st.session_state.vendeur_phone = ""
            st.rerun()

    # Bouton Copier le lien
    share_url = f"https://ton-app.streamlit.app/?vendeur={st.session_state.vendeur_phone}"
    st.code(share_url, language=None)
    st.caption("👆 Copiez ce lien pour un accès direct à votre dashboard.")

    try:
        response = supabase.table("orders").select("*").eq("phone_vendeur", st.session_state.vendeur_phone).order('created_at', desc=True).execute()
        orders = response.data

        if not orders:
            st.info("Aucune commande pour le moment.")
        else:
            for order in orders:
                # Formatage du prix : 20000 -> 20.000
                prix_brut = order.get('prix', 0) or 0
                prix_formate = "{:,.0f}".format(float(prix_brut)).replace(",", ".")
                
                with st.container():
                    st.markdown(f"""
                    <div class="order-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h2 style='margin:0; color:#700D02;'>👤 {order.get('nom_client', 'Client')}</h2>
                            <span class="status-badge" style="background: {'#1e3d24' if order.get('statut') == 'Livré' else '#4a0701'};">
                                {'✅ LIVRÉ' if order.get('statut') == 'Livré' else '⏳ À LIVRER'}
                            </span>
                        </div>
                        <hr style="border: 0.5px solid #333; margin: 15px 0;">
                        <p style='font-size:1.1em;'>
                            📍 <b>Lieu :</b> {order.get('quartier', 'N/A')}<br>
                            🛍️ <b>Articles :</b> {order.get('articles', 'N/A')}<br>
                            <b style='font-size:1.4em; color:white;'>💰 {prix_formate} FCFA</b>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        msg = urllib.parse.quote(f"Bonjour {order.get('nom_client', '')}, je suis le livreur...")
                        st.markdown(f'<a href="https://wa.me/{order.get("telephone", "")}?text={msg}" target="_blank" class="wa-button">💬 WhatsApp</a>', unsafe_allow_html=True)
                    
                    with c2:
                        if order.get('statut') == 'À livrer':
                            if st.button(f"Confirmer Livraison ✅", key=f"upd_{order['id']}", use_container_width=True):
                                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                                st.rerun()
                        else:
                            if st.button(f"Annuler (Erreur) 🔄", key=f"rev_{order['id']}", use_container_width=True):
                                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order['id']).execute()
                                st.rerun()

    except Exception as e:
        st.error(f"Erreur de données : {e}")
