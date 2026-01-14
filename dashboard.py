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

# ================= GESTION DU MODE =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 

bg_color = "#000000" if st.session_state.dark_mode else "#FFFFFF"
card_bg = "#121212" if st.session_state.dark_mode else "#F9F9F9"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
accent_red = "#FF0000" # Ton rouge vif

# ================= CSS DYNAMIQUE (BRIGHT & NEON) =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}

    /* Alignement boutons du haut */
    .stButton {{ display: flex; justify-content: flex-end; }}
    
    /* Titre Mes Commandes AGRANDI */
    .main-title {{ 
        font-size: 2.5rem !important; 
        font-weight: 900 !important; 
        color: {text_color} !important;
        margin-top: 10px;
        margin-bottom: 20px;
    }}

    /* DESIGN DES CARTES SÉPARÉES (Effet brillant/Néon) */
    .order-container {{
        background: {card_bg};
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid {border_color};
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
    }}
    
    /* Liseré brillant à gauche */
    .glow-border {{
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 6px;
        background: {accent_red};
        box-shadow: 2px 0px 12px {accent_red};
    }}

    /* Badges Statut */
    .badge {{
        float: right;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
        text-transform: uppercase;
    }}
    .badge-pending {{ background-color: {accent_red}; box-shadow: 0 0 10px {accent_red}; }}
    .badge-done {{ background-color: #1FA24A; box-shadow: 0 0 10px #1FA24A; }}

    /* Textes dans la carte */
    .info-line {{ margin: 8px 0; font-size: 1.1rem; color: {text_color}; display: flex; align-items: center; gap: 10px; }}
    .price {{ font-size: 1.6rem; font-weight: 900; color: {accent_red} !important; margin-top: 10px; }}

    /* Boutons MAVA */
    div.stButton > button {{
        width: 100%; border-radius: 12px !important; height: 55px;
        font-weight: 800 !important; background-color: #700D02 !important;
        color: white !important; border: none !important;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{ transform: scale(1.02); }}

    /* LOGIN */
    .login-text {{ color: {text_color} !important; text-align: left !important; }}
    div.login-btn-container div.stButton {{ justify-content: center !important; }}

    /* WhatsApp */
    .btn-whatsapp {{
        background-color: #25D366 !important; color: #000 !important;
        border-radius: 12px; text-align: center; padding: 15px;
        display: block; text-decoration: none; font-weight: 800;
        margin-bottom: 10px; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
    }}

    /* Footer */
    .footer {{
        margin-top: 60px; padding: 30px; text-align: center;
        color: {sub_text}; font-size: 0.8rem; border-top: 1px solid {border_color};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 15px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border: 1px solid {border_color} !important; border-radius: 12px !important;
        padding: 12px 20px !important;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #700D02 !important; border: 1px solid {accent_red} !important; }}
</style>
""", unsafe_allow_html=True)

# ================= TOP BAR (Toggle) =================
col_left, col_mid, col_right = st.columns([0.7, 0.1, 0.2])
with col_right:
    if st.button("☀️" if st.session_state.dark_mode else "🌙", key="mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ================= SUPABASE =================
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = get_supabase()

# ================= LOGIN / DASHBOARD =================
if "vendeur_phone" not in st.session_state:
    if "v" in st.query_params: st.session_state.vendeur_phone = st.query_params["v"]
    
if "vendeur_phone" not in st.session_state:
    st.markdown('<div style="padding-top:20px;">', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-text' style='font-weight:400;'>Entre ton numéro pour suivre tes commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    st.markdown('<div class="login-btn-container">', unsafe_allow_html=True)
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            st.session_state.vendeur_phone = phone_input.strip()
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
else:
    # DASHBOARD
    v_phone = st.session_state.vendeur_phone
    
    # Bouton Lien
    c_e, c_link = st.columns([0.8, 0.2])
    with c_link:
        if st.button("🔗", key="copy"):
            st.toast("Lien copié !")

    st.markdown("<h1 class='main-title'>Mes Commandes</h1>", unsafe_allow_html=True)

    try:
        res = supabase.table("orders").select("*").eq("phone_vendeur", v_phone).order("created_at", desc=True).execute()
        orders = res.data or []
    except: orders = []

    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    t1, t2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with t1:
        for o in pending:
            st.markdown(f"""
            <div class="order-container">
                <div class="glow-border"></div>
                <div class="badge badge-pending">À LIVRER 📦</div>
                <div class="info-line">👤 <b>{o.get('nom_client')}</b></div>
                <div class="info-line">📍 {o.get('quartier')}</div>
                <div class="info-line">🛍️ {o.get('articles')}</div>
                <div class="price">{o.get('prix')} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Boutons d'action
            msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison MAVA.")
            st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{o.get("telephone")}?text={msg}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
            if st.button("MARQUER COMME LIVRÉ", key=f"btn_{o['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", o['id']).execute()
                st.rerun()

    with t2:
        for o in done:
            st.markdown(f"""
            <div class="order-container" style="border-color: #1FA24A33;">
                <div class="glow-border" style="background: #1FA24A; box-shadow: 2px 0px 12px #1FA24A;"></div>
                <div class="badge badge-done">LIVRÉE ✅</div>
                <div class="info-line">👤 <b>{o.get('nom_client')}</b></div>
                <div class="price" style="color:#1FA24A !important;">{o.get('prix')} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Rétablir 🔄", key=f"rev_{o['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", o['id']).execute()
                st.rerun()

# ================= FOOTER =================
st.markdown("""
    <div class="footer">
        MAVA © 2025 • Tous droits réservés<br>
        Plateforme de suivi logistique sécurisée<br>
        <span style="opacity:0.5;">v2.1.5 • Stable Release</span>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh 30s
if "refresh" not in st.session_state: st.session_state.refresh = time.time()
if time.time() - st.session_state.refresh > 30:
    st.session_state.refresh = time.time()
    st.rerun()
