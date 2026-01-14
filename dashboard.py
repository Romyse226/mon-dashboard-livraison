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
accent_red = "#FF0000"

# ================= CSS DYNAMIQUE =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}

    .stButton {{ display: flex; justify-content: flex-end; }}
    
    .main-title {{ 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: {text_color} !important;
        margin-top: 10px;
    }}

    /* CARTES SEPAREES AVEC EFFET LUMINEUX */
    .order-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid {border_color};
        position: relative;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    
    .glow-line {{
        position: absolute;
        left: 0; top: 15%; bottom: 15%;
        width: 5px;
        background: {accent_red};
        box-shadow: 0px 0px 10px {accent_red};
        border-radius: 0 5px 5px 0;
    }}

    .badge {{
        float: right;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
        background-color: {accent_red};
    }}

    .info-line {{ margin-bottom: 6px; font-size: 1.05rem; color: {text_color}; }}
    .price {{ font-size: 1.4rem; font-weight: 800; color: {accent_red} !important; margin-top: 10px; }}

    /* BOUTONS */
    div.stButton > button {{
        width: 100%; border-radius: 10px !important; height: 50px;
        font-weight: 700 !important; background-color: #700D02 !important;
        color: white !important; border: none !important;
    }}

    /* LOGIN */
    .login-text {{ color: {text_color} !important; text-align: left !important; }}
    div.login-btn-container div.stButton {{ justify-content: center !important; }}

    .btn-whatsapp {{
        background-color: #25D366 !important; color: #000 !important;
        border-radius: 10px; text-align: center; padding: 12px;
        display: block; text-decoration: none; font-weight: 700; margin-bottom: 8px;
    }}

    .footer {{
        margin-top: 50px; padding: 20px; text-align: center;
        color: {sub_text}; font-size: 0.75rem; border-top: 1px solid {border_color};
    }}
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

# ================= LOGIC =================
if "vendeur_phone" not in st.session_state:
    if "v" in st.query_params: st.session_state.vendeur_phone = st.query_params["v"]

if "vendeur_phone" not in st.session_state:
    # PAGE LOGIN (TEXTE A GAUCHE / BOUTON CENTRE)
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
    
    # Bouton Lien en haut
    c_e, c_link = st.columns([0.8, 0.2])
    with c_link:
        if st.button("🔗"): st.toast("Lien copié !")

    st.markdown("<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    try:
        res = supabase.table("orders").select("*").eq("phone_vendeur", v_phone).order("created_at", desc=True).execute()
        orders = res.data or []
    except: orders = []

    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    t1, t2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with t1:
        for o in pending:
            # SECTION CLIENT AVEC INFOS VISIBLES
            st.markdown(f"""
            <div class="order-card">
                <div class="glow-line"></div>
                <div class="badge">À LIVRER 📦</div>
                <div class="info-line">👤 <b>Client :</b> {o.get('nom_client')}</div>
                <div class="info-line">📍 <b>Lieu :</b> {o.get('quartier')}</div>
                <div class="info-line">🛍️ <b>Article :</b> {o.get('articles')}</div>
                <div class="price">{o.get('prix')} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{o.get("telephone")}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
            if st.button("MARQUER COMME LIVRÉ", key=f"b_{o['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", o['id']).execute()
                st.rerun()

    with t2:
        for o in done:
            st.markdown(f"""
            <div class="order-card">
                <div class="glow-line" style="background:#1FA24A; box-shadow:0 0 10px #1FA24A;"></div>
                <div class="badge" style="background:#1FA24A;">LIVRÉE ✅</div>
                <div class="info-line">👤 <b>Client :</b> {o.get('nom_client')}</div>
                <div class="price" style="color:#1FA24A !important;">{o.get('prix')} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Rétablir 🔄", key=f"r_{o['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", o['id']).execute()
                st.rerun()

st.markdown('<div class="footer">MAVA © 2025 • Tous droits réservés</div>', unsafe_allow_html=True)
