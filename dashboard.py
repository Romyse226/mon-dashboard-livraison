import streamlit as st
from supabase import create_client
import urllib.parse
import time

# ================= CONFIG =================
st.set_page_config(
    page_title="MAVA",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= GESTION DU MODE (CLAIR/SOMBRE) =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 

# Couleurs dynamiques
bg_color = "#000000" if st.session_state.dark_mode else "#FFFFFF"
card_bg = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
price_color = "#FF0000" if st.session_state.dark_mode else "#700D02"

# ================= CSS DYNAMIQUE =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}

    /* Alignement bouton Toggle */
    .stButton {{
        display: flex;
        justify-content: flex-end;
    }}
    
    /* Titre Mes Commandes */
    .main-title {{ 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: {text_color} !important;
        display: block;
        margin-top: 10px;
    }}

    /* --- NOUVEAU DESIGN : SECTIONS SÉPARÉES ET BRILLANTES --- */
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
    
    /* Le liseré brillant/néon à gauche */
    .card.pending::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 6px;
        background: #FF0000;
        box-shadow: 2px 0px 12px #FF0000;
    }}
    
    .card.done::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 6px;
        background: #1FA24A;
        box-shadow: 2px 0px 12px #1FA24A;
    }}

    .badge {{
        position: absolute;
        top: 15px;
        right: 15px;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
    }}
    .badge-pending {{ background-color: #FF0000; box-shadow: 0 0 8px #FF0000; }}
    .badge-done {{ background-color: #1FA24A; box-shadow: 0 0 8px #1FA24A; }}

    /* Infos Cartes */
    .info-line {{ margin-bottom: 6px; font-size: 1.1rem; color: {text_color} !important; width: 85%; }}
    .price {{ font-size: 1.5rem; font-weight: 900; color: {price_color} !important; margin-top: 10px; }}

    /* Boutons MAVA */
    div.stButton > button {{
        width: 100%;
        border-radius: 10px !important;
        height: 50px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important;
        border: none !important;
    }}
    div.stButton > button div p {{ color: white !important; }}

    /* LOGIN TEXT ALIGNEMENT GAUCHE */
    .login-text {{ 
        color: {text_color} !important; 
        font-weight: 600; 
        text-align: left !important; 
        width: 100%;
    }}

    /* Centrage spécifique du bouton de login sur mobile */
    div.login-btn-container div.stButton {{
        justify-content: center !important;
    }}

    /* Footer */
    .footer {{
        margin-top: 50px;
        padding: 20px;
        text-align: center;
        color: {sub_text};
        font-size: 0.75rem;
        border-top: 1px solid {border_color};
    }}

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #700D02 !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

# ================= TOP BAR (Toggle) =================
col_left, col_mid, col_right = st.columns([0.7, 0.1, 0.2])
with col_right:
    label_mode = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(label_mode, key="mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ================= SUPABASE =================
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = get_supabase()

# ================= SESSION =================
if "v" in st.query_params and "vendeur_phone" not in st.session_state:
    st.session_state.vendeur_phone = st.query_params["v"]

# ================= UTILS =================
def normalize_phone(phone: str):
    phone = phone.replace(" ", "").replace("+", "")
    if len(phone) == 10 and phone.startswith("0"): return "225" + phone
    elif len(phone) == 8: return "225" + phone
    return phone

def format_price(val):
    try: return f"{int(val):,}".replace(",", ".") + " FCFA"
    except: return "—"

# ================= LOGIN =================
if "vendeur_phone" not in st.session_state:
    st.markdown('<div style="text-align:left; padding-top:20px;">', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown(f"<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='login-text' style='font-weight:400;'>Entre ton numéro pour suivre tes commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    st.markdown('<div class="login-btn-container">', unsafe_allow_html=True)
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = normalize_phone(phone_input.strip())
            st.session_state.vendeur_phone = num
            st.query_params["v"] = num
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
else:
    # ================= DASHBOARD =================
    vendeur_phone = st.session_state.vendeur_phone

    col_empty, col_btn_link = st.columns([0.8, 0.2])
    with col_btn_link:
        dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
        if st.button("🔗", key="copy_link"):
            st.toast("Lien copié !")
            st.markdown(f"""<script>navigator.clipboard.writeText("{dash_url}");</script>""", unsafe_allow_html=True)

    st.markdown(f"<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    try:
        res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
        orders = res.data or []
    except:
        orders = []

    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with tab1:
        if not pending:
            st.markdown(f"<p style='text-align:center; color:{sub_text};'>Aucune commande en attente.</p>", unsafe_allow_html=True)
        for order in pending:
            st.markdown(f"""
            <div class="card pending">
                <div class="badge badge-pending">À LIVRER 📦</div>
                <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
                <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
                <div class="price">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            p_c = normalize_phone(order.get("telephone",""))
            msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison MAVA.")
            st.markdown(f'<a style="background-color:#25D366; color:#000; border-radius:10px; text-align:center; padding:12px; display:block; text-decoration:none; font-weight:700; margin-bottom:8px;" href="https://wa.me/{p_c}?text={msg}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
            
            if st.button("MARQUER COMME LIVRÉ", key=f"p_{order['id']}"):
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
                <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
                <div class="price" style="color:#1FA24A !important;">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Annuler 🔄", key=f"d_{order['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order['id']).execute()
                st.rerun()

# ================= FOOTER =================
st.markdown(f"""
    <div class="footer">
        MAVA © 2025 • Tous droits réservés<br>
        Plateforme de suivi logistique sécurisée<br>
        <span style="opacity:0.5;">v2.1.0 • Stable Release</span>
    </div>
""", unsafe_allow_html=True)

# ================= AUTO-REFRESH =================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()
