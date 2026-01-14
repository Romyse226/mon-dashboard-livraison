import streamlit as st
from supabase import create_client
import urllib.parse
import time

# ================= CONFIG =================
st.set_page_config(
    page_title="MAVA • Dashboard Vendeur",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CSS (VISUEL PRO & MOBILE FIRST) =================
st.markdown(f"""
<style>
    /* Global */
    .stApp {{
        background-color: #FFFFFF;
        color: #111;
    }}
    
    /* Login Box */
    .login-box {{
        max-width: 400px;
        margin: auto;
        padding: 40px 20px;
        background: white;
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(112, 13, 2, 0.1);
        text-align: center;
    }}

    /* Cartes Commandes */
    .card {{
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        background: #fdfdfd;
        border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}
    .card.pending {{ border-left: 8px solid #700D02; }}
    .card.done {{ border-left: 8px solid #1FA24A; opacity: 0.8; }}

    .badge-new {{
        background-color: #700D02;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }}

    .price {{
        color: #700D02;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 10px;
    }}

    /* Boutons */
    div.stButton > button {{
        width: 100%;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }}
    
    /* Bouton Primaire (Couleur MAVA) */
    div.stButton > button[kind="primary"] {{
        background-color: #700D02 !important;
        color: white !important;
        border: none !important;
        height: 3em;
    }}

    /* Bouton WhatsApp (Noir sur Vert) */
    .btn-whatsapp {{
        background-color: #25D366 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        text-align: center;
        padding: 10px;
        display: block;
        font-weight: 700;
        text-decoration: none;
        margin-bottom: 10px;
        border: 1px solid #128C7E;
    }}

    /* Header */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = supabase_client()

# ================= UTILS =================
def normalize_phone(phone: str):
    phone = "".join(filter(str.isdigit, phone))
    if len(phone) == 10 and phone.startswith("0"):
        return "225" + phone
    return phone

def format_price(val):
    try:
        return f"{int(val):,}".replace(",", " ") + " FCFA"
    except:
        return "—"

# ================= AUTO REFRESH (30s) =================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Script d'auto-refresh toutes les 30 secondes
st.empty()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ================= LOGIN =================
if "vendeur_phone" not in st.session_state:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 style='color:#700D02;'>Espace Vendeur</h2>", unsafe_allow_html=True)

    phone_input = st.text_input(
        "Entrez votre numéro WhatsApp",
        placeholder="Ex: 0707070707"
    )

    if st.button("Se connecter", type="primary"):
        if phone_input.strip():
            # On normalise pour le stockage mais l'utilisateur tape juste son numéro
            st.session_state.vendeur_phone = normalize_phone(phone_input.strip())
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD (CONNECTÉ) =================
vendeur_phone = st.session_state.vendeur_phone
logo_url = "https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png"

# Header avec Logo à droite
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown(f"<h2 style='margin:0;'>Mes Commandes</h2>", unsafe_allow_html=True)
with col_t2:
    st.image(logo_url, width=60)

# Lien Dashboard unique (Copiable proprement)
dashboard_url = f"https://mava.streamlit.app/?vendeur={vendeur_phone}"
st.info(f"🔗 **Lien unique :** {dashboard_url}")
st.caption("Maintenez le lien appuyé pour le copier sur mobile.")

# ================= FETCH DATA =================
try:
    res = supabase.table("orders") \
        .select("*") \
        .eq("phone_vendeur", vendeur_phone) \
        .order("created_at", desc=True) \
        .execute()
    orders = res.data or []
except:
    orders = []

pending = [o for o in orders if o.get("statut") != "Livré"]
done = [o for o in orders if o.get("statut") == "Livré"]

# Affichage des sections
if pending:
    st.markdown("### 🔔 NOUVELLES COMMANDES")
    for order in pending:
        with st.container():
            st.markdown(f"""
            <div class="card pending">
                <div class="badge-new">À LIVRER</div><br>
                👤 <b>Client :</b> {order.get('nom_client','—')}<br>
                📍 <b>Lieu :</b> {order.get('quartier','—')}<br>
                🛍️ <b>Article :</b> {order.get('articles','—')}
                <div class="price">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Boutons Mobile-First (WhatsApp au centre, Action à droite)
            phone_client = normalize_phone(order.get("telephone",""))
            msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison MAVA.")
            
            st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{phone_client}?text={msg}" target="_blank">💬 WhatsApp Client</a>', unsafe_allow_html=True)
            
            if st.button("✅ Livraison effectuée", key=f"btn_{order['id']}", type="primary"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", order["id"]).execute()
                st.rerun()
            st.markdown("---")

if done:
    with st.expander("📊 Historique des livraisons", expanded=False):
        for order in done:
            st.markdown(f"""
            <div class="card done">
                👤 <b>Client :</b> {order.get('nom_client','—')}<br>
                🛍️ <b>Article :</b> {order.get('articles','—')}
                <div class="price" style="font-size:1rem;">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Annuler le statut Livré", key=f"undo_{order['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order["id"]).execute()
                st.rerun()

# Footer auto-refresh
st.caption(f"Dernière mise à jour : {time.strftime('%H:%M:%S')} (Refresh auto 30s)")
