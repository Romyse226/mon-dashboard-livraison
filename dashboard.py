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
card_bg = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
price_color = "#FF0000" if st.session_state.dark_mode else "#700D02"

# ================= CSS INJECTION (FORCE LE BOUTON À DROITE) =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    
    /* Cache les éléments natifs qui gênent */
    header, [data-testid="stHeader"] {{ visibility: hidden; }}

    /* FORCE LE BOUTON DE MODE EN HAUT À DROITE ABSOLU */
    .mode-switch-container {{
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999999;
    }}
    
    .mode-switch-container button {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}

    /* Titres et Textes */
    .main-title {{ font-size: 1.8rem !important; font-weight: 800 !important; color: {text_color} !important; display: block; margin-top: 10px; }}
    .login-text {{ color: {text_color} !important; font-weight: 600; text-align: center; }}

    /* Cartes & Badges */
    .card {{
        position: relative;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        background: {card_bg};
        border: 1px solid {border_color};
    }}
    .card.pending {{ border-left: 8px solid #FF0000; }}
    .card.done {{ border-left: 8px solid #1FA24A; }}
    
    .badge {{
        position: absolute; top: 15px; right: 15px; padding: 4px 8px;
        border-radius: 5px; font-size: 0.7rem; font-weight: bold; color: white;
    }}
    .badge-pending {{ background-color: #FF0000; }}
    .badge-done {{ background-color: #1FA24A; }}

    /* Infos & Prix */
    .info-line {{ margin-bottom: 4px; font-size: 1rem; color: {text_color} !important; width: 75%; }}
    .price {{ font-size: 1.3rem; font-weight: 800; color: {price_color} !important; }}

    /* Boutons MAVA */
    div.stButton > button {{
        width: 100%; border-radius: 10px !important; height: 50px;
        font-weight: 700 !important; background-color: #700D02 !important;
        color: #FFFFFF !important; border: none !important;
    }}
    div.stButton > button div p {{ color: white !important; }}

    /* WhatsApp */
    .btn-whatsapp {{
        background-color: #25D366 !important; color: #000 !important;
        border-radius: 10px; text-align: center; padding: 12px;
        display: block; text-decoration: none; font-weight: 700; margin-bottom: 8px;
    }}

    /* Footer */
    .footer {{
        margin-top: 50px; padding: 20px; text-align: center;
        color: {sub_text}; font-size: 0.75rem; border-top: 1px solid {border_color};
    }}

    /* Onglets Tactiles */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg} !important; color: {text_color} !important;
        border: 1px solid {border_color} !important; border-radius: 10px !important;
        padding: 10px 12px !important;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #700D02 !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

# ================= BOUTON TOGGLE (DÉTACHÉ) =================
# Ce bloc utilise un conteneur flottant pour rester en haut à droite
st.markdown('<div class="mode-switch-container">', unsafe_allow_html=True)
if st.button("☀️" if st.session_state.dark_mode else "🌙", key="top_right_toggle"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div style="text-align:center; padding-top:40px;">', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown(f"<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='login-text'>Entrez votre numéro pour suivre vos commandes</p>", unsafe_allow_html=True)
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = normalize_phone(phone_input.strip())
            st.session_state.vendeur_phone = num
            st.query_params["v"] = num
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # ================= DASHBOARD =================
    vendeur_phone = st.session_state.vendeur_phone
    col_t, col_c = st.columns([0.85, 0.15])
    with col_t:
        st.markdown(f"<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)
    with col_c:
        dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
        if st.button("🔗"):
            st.toast("Lien copié !")
            st.markdown(f"""<script>navigator.clipboard.writeText("{dash_url}");</script>""", unsafe_allow_html=True)

    try:
        res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
        orders = res.data or []
    except:
        orders = []

    p_orders = [o for o in orders if o["statut"] != "Livré"]
    d_orders = [o for o in orders if o["statut"] == "Livré"]

    t1, t2 = st.tabs([f"🔔 En cours ({len(p_orders)})", f"✅ Livrées ({len(d_orders)})"])

    with t1:
        if not p_orders: st.markdown("<p style='text-align:center;'>Aucune commande.</p>", unsafe_allow_html=True)
        for o in p_orders:
            st.markdown(f'<div class="card pending"><div class="badge badge-pending">À LIVRER 📦</div><div class="info-line">👤 <b>{o.get("nom_client")}</b></div><div class="info-line">📍 {o.get("quartier")}</div><div class="info-line">🛍️ {o.get("articles")}</div><div class="price">{format_price(o.get("prix"))}</div></div>', unsafe_allow_html=True)
            p_c = normalize_phone(o.get("telephone",""))
            st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{p_c}?text=Bonjour" target="_blank">CONTACTER</a>', unsafe_allow_html=True)
            if st.button("MARQUER LIVRÉ", key=f"p_{o['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", o['id']).execute()
                st.rerun()

    with t2:
        if not d_orders: st.markdown("<p style='text-align:center;'>Aucun historique.</p>", unsafe_allow_html=True)
        for o in d_orders:
            st.markdown(f'<div class="card done"><div class="badge badge-done">LIVRÉE ✅</div><div class="info-line">👤 <b>{o.get("nom_client")}</b></div><div class="info-line">🛍️ {o.get("articles")}</div><div class="price" style="color:#1FA24A !important;">{format_price(o.get("prix"))}</div></div>', unsafe_allow_html=True)
            if st.button("Annuler 🔄", key=f"d_{o['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", o['id']).execute()
                st.rerun()

st.markdown(f'<div class="footer">MAVA © 2025 • Tous droits réservés<br><span style="opacity:0.5;">v2.1.0</span></div>', unsafe_allow_html=True)

if "last_refresh" not in st.session_state: st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()
