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

# ================= CSS : DESIGN FINAL =================
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    #MainMenu, footer, header {visibility: hidden;}

    /* Textes de connexion en NOIR */
    .login-text {
        color: #000000 !important;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* Style des Cartes */
    .card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #EEEEEE;
    }
    .card.pending { border-left: 8px solid #700D02; }
    .card.done { border-left: 8px solid #1FA24A; opacity: 0.9; }

    /* Textes */
    .info-line { margin-bottom: 4px; font-size: 1rem; color: #111 !important; }
    .price { font-size: 1.3rem; font-weight: 800; color: #700D02 !important; }

    /* BOUTONS ROUGE MAVA : TEXTE BLANC */
    div.stButton > button {
        width: 100%;
        border-radius: 10px !important;
        height: 50px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important; 
        border: none !important;
    }
    
    /* Forcer le texte blanc pour Streamlit Mobile */
    div.stButton > button div p {
        color: white !important;
    }

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

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f8f8;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE CONNECTION =================
# Pas de cache ici pour garantir la fraîcheur des données
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

# ================= SESSION PERSISTANCE =================
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
    st.markdown("<div style='text-align:center; padding-top:50px;'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=130)
    
    # Textes mis en noir comme demandé
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-text'>Entrez votre numéro pour suivre vos commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("ACCÉDER AU DASHBOARD"):
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
    st.markdown("<h3 style='color:black;'>Mes Commandes</h3>", unsafe_allow_html=True)
with col_h2:
    dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
    if st.button("🔗"):
        st.toast("Lien copié !")
        # Script JS pour la copie
        st.markdown(f"""<script>navigator.clipboard.writeText("{dash_url}");</script>""", unsafe_allow_html=True)

# ================= FETCH DATA (FORCE LIVE) =================
# On récupère les données sans aucun cache
try:
    res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
    orders = res.data or []
except:
    orders = []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

# ================= AFFICHAGE =================
tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

with tab1:
    if not pending:
        st.markdown("<p style='color:black;'>Aucune commande en attente.</p>", unsafe_allow_html=True)
    for order in pending:
        st.markdown(f"""
        <div class="card pending">
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
        st.markdown("<p style='color:black;'>Aucune commande livrée.</p>", unsafe_allow_html=True)
    # Les commandes livrées s'affichent ici
    for order in done:
        st.markdown(f"""
        <div class="card done">
            <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
            <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
            <div class="price" style="color:#1FA24A !important;">{format_price(order.get('prix'))}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Annuler livraison", key=f"d_{order['id']}"):
            supabase.table("orders").update({"statut": "À livrer"}).eq("id", order['id']).execute()
            st.rerun()

# ================= AUTO-REFRESH SANS INTERRUPTIONS =================
# Actualisation automatique invisible toutes les 30 secondes
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()
    st.session_state.last_refresh = time.time()
    st.rerun()
