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

# ================= CSS : DESIGN MOBILE FINAL =================
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; }
    #MainMenu, footer, header {visibility: hidden;}

    /* Centrage Page Connexion */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-top: 50px;
    }
    
    .login-text {
        color: #000000 !important;
        font-weight: 600;
        margin-bottom: 5px;
    }

    /* Titre Mes Commandes */
    .main-title {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
    }

    /* Onglets style Boutons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f1f1 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #700D02 !important;
        color: white !important;
        border: none !important;
    }

    /* Style des Cartes */
    .card {
        position: relative;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #EEEEEE;
    }
    .card.pending { border-left: 8px solid #700D02; }
    .card.done { border-left: 8px solid #1FA24A; }

    /* Badges Statut */
    .badge {
        position: absolute;
        top: 15px;
        right: 15px;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
    }
    .badge-pending { background-color: #700D02; }
    .badge-done { background-color: #1FA24A; }

    /* Textes */
    .info-line { margin-bottom: 4px; font-size: 1rem; color: #111 !important; width: 70%; }
    .price { font-size: 1.3rem; font-weight: 800; color: #700D02 !important; }

    /* Boutons ROUGES MAVA */
    div.stButton > button {
        width: 100%;
        border-radius: 10px !important;
        height: 50px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    div.stButton > button div p { color: white !important; }

    /* Bouton WhatsApp */
    .btn-whatsapp {
        background-color: #25D366 !important;
        color: #000 !important;
        border-radius: 10px;
        text-align: center;
        padding: 12px;
        display: block;
        text-decoration: none;
        font-weight: 700;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-text'>Entrez votre numéro pour suivre vos commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = normalize_phone(phone_input.strip())
            st.session_state.vendeur_phone = num
            st.query_params["v"] = num
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD HEADER =================
vendeur_phone = st.session_state.vendeur_phone

col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown("<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)
with col_h2:
    dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
    if st.button("🔗"):
        st.toast("Lien copié !")
        st.markdown(f"""<script>navigator.clipboard.writeText("{dash_url}");</script>""", unsafe_allow_html=True)

# ================= FETCH =================
try:
    res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
    orders = res.data or []
except:
    orders = []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

# ================= ONGLETS =================
tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

with tab1:
    if not pending:
        st.markdown("<p style='color:black; text-align:center;'>Aucune commande en attente.</p>", unsafe_allow_html=True)
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
        st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{p_c}?text={msg}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
        
        if st.button("MARQUER COMME LIVRÉ", key=f"p_{order['id']}"):
            supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
            st.rerun()

with tab2:
    if not done:
        st.markdown("<p style='color:black; text-align:center;'>Aucune commande livrée.</p>", unsafe_allow_html=True)
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

# ================= AUTO-REFRESH =================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()
