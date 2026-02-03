import streamlit as st
from supabase import create_client
import urllib.parse
import time
import streamlit.components.v1 as components

# ================= CONFIG =================
st.set_page_config(
    page_title="MAVA",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= PERSISTANCE & ÉTAT =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 

if "vendeur_phone" not in st.session_state and "v" in st.query_params:
    st.session_state.vendeur_phone = st.query_params["v"]

# ================= COULEURS DYNAMIQUES =================
bg_color = "#000000" if st.session_state.dark_mode else "#FFFFFF"
card_bg = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
price_color = "#FF0000" if st.session_state.dark_mode else "#700D02"

# ================= CSS DYNAMIQUE (FIXÉ POUR MODE CLAIR) =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}

    .main-title {{ 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: {text_color} !important;
        display: block;
        margin-top: 10px;
    }}

    .card {{
        position: relative;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        background: {card_bg};
        border: 1px solid {border_color};
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        overflow: hidden;
    }}
    
    .card.pending::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #FF0000; box-shadow: 2px 0px 12px #FF0000; }}
    .card.done::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #1FA24A; box-shadow: 2px 0px 12px #1FA24A; }}

    .badge {{ position: absolute; top: 15px; right: 15px; padding: 5px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; color: white; }}
    .badge-pending {{ background-color: #FF0000; }}
    .badge-done {{ background-color: #1FA24A; }}

    .info-line {{ margin-bottom: 6px; font-size: 1.1rem; color: {text_color} !important; }}
    .price {{ font-size: 1.5rem; font-weight: 900; color: {price_color} !important; margin-top: 10px; }}

    /* Correction couleur texte onglets */
    .stTabs [data-baseweb="tab"] p {{
        color: {text_color} !important;
    }}

    div.stButton > button {{
        width: 100%;
        border-radius: 10px !important;
        height: 50px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important;
        border: none !important;
    }}
    
    .login-text {{ color: {text_color} !important; font-weight: 600; text-align: left !important; }}
    .footer {{ margin-top: 50px; padding: 20px; text-align: center; color: {sub_text}; font-size: 0.75rem; border-top: 1px solid {border_color}; }}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = get_supabase()

def fetch_data(phone):
    res = supabase.table("orders").select("*").eq("phone_vendeur", phone).order("created_at", desc=True).execute()
    return res.data or []

# ================= TOP BAR =================
col_left, col_mid, col_right = st.columns([0.7, 0.1, 0.2])
with col_right:
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ================= LOGIQUE D'AFFICHAGE =================
if "vendeur_phone" not in st.session_state:
    # --- PAGE LOGIN ---
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-text' style='font-weight:400;'>Entre ton numéro pour suivre tes commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = phone_input.replace(" ", "").replace("+", "")
            if len(num) == 10 and num.startswith("0"): num = "225" + num
            st.session_state.vendeur_phone = num
            st.query_params["v"] = num
            st.rerun()
else:
    # --- DASHBOARD ---
    vendeur_phone = st.session_state.vendeur_phone
    
    # Bouton de déconnexion discret
    if st.button("Se déconnecter 🚪", key="logout"):
        del st.session_state.vendeur_phone
        st.query_params.clear()
        st.rerun()

    st.markdown("<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    # Notifs (uniquement si connecté)
    components.html(f"""
        <script>
        if (window.Notification && Notification.permission === "default") {{
            // On peut ajouter ici un petit rappel discret si besoin
        }}
        </script>
    """, height=0)

    orders = fetch_data(vendeur_phone)
    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with tab1:
        if not pending:
            st.markdown(f"<p style='text-align:center; color:{sub_text};'>Aucune commande en cours.</p>", unsafe_allow_html=True)
        for order in pending:
            st.markdown(f"""
            <div class="card pending">
                <div class="badge badge-pending">À LIVRER 📦</div>
                <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
                <div class="price">{int(order.get('prix', 0)):,} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("MARQUER COMME LIVRÉ", key=f"btn_{order['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                st.rerun()

    with tab2:
        if not done:
            st.markdown(f"<p style='text-align:center; color:{sub_text};'>Aucune commande livrée.</p>", unsafe_allow_html=True)
        for order in done:
            st.markdown(f"""
            <div class="card done">
                <div class="badge badge-done">LIVRÉE ✅</div>
                <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                <div class="price" style="color:#1FA24A !important;">{int(order.get('prix', 0)):,} FCFA</div>
            </div>
            """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown(f'<div class="footer">MAVA © 2026 • Stable Sync Release</div>', unsafe_allow_html=True)

# Refresh automatique toutes les 30s si connecté
if "vendeur_phone" in st.session_state:
    if "last_ts" not in st.session_state: st.session_state.last_ts = time.time()
    if time.time() - st.session_state.last_ts > 30:
        st.session_state.last_ts = time.time()
        st.rerun()
