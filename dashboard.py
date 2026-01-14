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

    /* BOUTONS ROUGE MAVA : TEXTE BLANC FORCE */
    div.stButton > button {
        width: 100%;
        border-radius: 10px !important;
        height: 50px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important; /* Texte Blanc */
        border: none !important;
    }
    
    /* Correction spécifique pour le texte blanc sur certains navigateurs mobiles */
    .stButton button p {
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

    /* Tabs (Onglets) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f8f8f8;
        padding: 5px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = supabase_client()

# ================= SESSION URL =================
query_params = st.query_params
if "v" in query_params and "vendeur_phone" not in st.session_state:
    st.session_state.vendeur_phone = query_params["v"]

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
    st.markdown("## Bienvenue")
    st.write("Entrez votre numéro pour suivre vos commandes")
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
    st.markdown("### Mes Commandes")
with col_h2:
    dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
    if st.button("🔗"):
        st.write(f'<script>navigator.clipboard.writeText("{dash_url}")</script>', unsafe_allow_html=True)
        st.toast("Lien copié !")

# ================= FETCH DATA (SANS CACHE) =================
# On force le fetch à chaque run pour avoir les données fraîches
res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
orders = res.data or []

pending = [o for o in orders if o["statut"] != "Livré"]
# Pour l'historique : trié du plus récent livré au plus ancien livré
done = [o for o in orders if o["statut"] == "Livré"]

# ================= ORGANISATION PAR ONGLETS (MOBILE FRIENDLY) =================
tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

with tab1:
    if not pending:
        st.info("Aucune commande en attente.")
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
        st.write("Historique vide.")
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

# ================= AUTO-REFRESH INVISIBLE =================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()
