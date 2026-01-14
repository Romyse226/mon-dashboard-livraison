import streamlit as st
from supabase import create_client
import urllib.parse
import time

# ================= CONFIG =================
st.set_page_config(
    page_title="MAVA • Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Couleur MAVA : #700D02
# Logo : https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png

# ================= CSS MOBILE FIRST & DESIGN =================
st.markdown(f"""
<style>
    /* Global */
    .stApp {{
        background-color: #FFFFFF;
        color: #111;
    }}
    
    /* Cacher les éléments Streamlit inutiles */
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}

    /* Card Design */
    .card {{
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }}
    .card.pending {{ border-left: 8px solid #700D02; }}
    .card.done {{ border-left: 8px solid #1FA24A; opacity: 0.8; }}

    /* Typography */
    .price {{
        font-size: 1.4rem;
        font-weight: 900;
        color: #700D02;
        margin-top: 10px;
    }}
    .info-line {{
        margin-bottom: 5px;
        font-size: 1rem;
    }}

    /* Buttons Modernization */
    div.stButton > button {{
        width: 100%;
        border-radius: 12px !important;
        height: 45px;
        font-weight: 600 !important;
        transition: 0.3s;
    }}
    
    /* Bouton Livraison Effectuée (Primaire MAVA) */
    .stButton > button[kind="primary"] {{
        background-color: #700D02 !important;
        color: white !important;
        border: none !important;
    }}

    /* WhatsApp Button Custom */
    .btn-whatsapp {{
        background-color: #25D366 !important;
        color: #000000 !important; /* Texte Noir comme demandé */
        border-radius: 12px;
        text-align: center;
        padding: 12px;
        display: block;
        text-decoration: none;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    /* Login Box */
    .login-box {{
        padding: 20px;
        text-align: center;
    }}
    
    /* Badge Nouvelle Commande */
    .new-badge {{
        background-color: #700D02;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }}

</style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = supabase_client()

# ================= UTILS =================
def normalize_phone(phone: str):
    phone = phone.replace(" ", "").replace("+", "")
    # Si l'utilisateur saisit 10 chiffres commençant par 0, on ajoute 225
    if len(phone) == 10 and phone.startswith("0"):
        return "225" + phone
    # Si l'utilisateur saisit 10 chiffres sans le 0 (ex: 07...)
    elif len(phone) == 8:
        return "225" + phone
    return phone

def format_price(val):
    try: return f"{int(val):,}".replace(",", ".") + " FCFA"
    except: return "—"

# ================= LOGIN LOGIC =================
if "vendeur_phone" not in st.session_state:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=180)
    
    st.markdown("### Bienvenue chez MAVA")
    st.write("Entrez votre numéro pour accéder à vos livraisons")

    phone_input = st.text_input("Numéro WhatsApp", placeholder="Ex: 0701020304")

    if st.button("Se connecter", type="primary"):
        if phone_input.strip():
            # On normalise pour l'enregistrement en session
            st.session_state.vendeur_phone = normalize_phone(phone_input.strip())
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD HEADER =================
vendeur_phone = st.session_state.vendeur_phone

col_title, col_logo = st.columns([3, 1])
with col_title:
    st.markdown(f"## Mes Commandes")
with col_logo:
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=70)

# Dashboard Link Unique (Copiable proprement)
dashboard_link = f"https://mava.streamlit.app/?vendeur={vendeur_phone}"
st.markdown(f"🔗 **Lien Dashboard :** `{dashboard_link}`", help="Appuyez longuement pour copier votre lien unique.")

# ================= AUTO REFRESH (30s) =================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ================= DATA FETCH =================
res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
orders = res.data or []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

# ================= DISPLAY =================
if not orders:
    st.info("Aucune commande pour le moment.")

# Section Nouvelles / En cours
if pending:
    st.markdown("#### 🔔 NOUVELLES COMMANDES")
    for order in pending:
        with st.container():
            st.markdown(f"""
            <div class="card pending">
                <div class="new-badge">À LIVRER</div>
                <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
                <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
                <div class="price">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Boutons Action
            phone_c = normalize_phone(order.get("telephone",""))
            msg = urllib.parse.quote("Bonjour MAVA, je suis en route pour votre livraison.")
            
            st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{phone_c}?text={msg}" target="_blank">💬 WhatsApp Client</a>', unsafe_allow_html=True)
            
            if st.button("✅ Livraison effectuée", key=f"btn_{order['id']}", type="primary"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", order["id"]).execute()
                st.rerun()
            st.markdown("---")

# Section Historique
if done:
    with st.expander("✅ Commandes Livrées", expanded=False):
        for order in done:
            st.markdown(f"""
            <div class="card done">
                <div class="info-line">👤 Client : {order.get('nom_client','—')}</div>
                <div class="info-line">🛍️ Article : {order.get('articles','—')}</div>
                <div class="price" style="color: #1FA24A;">{format_price(order.get('prix'))}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Annuler le statut livré", key=f"undo_{order['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order["id"]).execute()
                st.rerun()

# Petit script pour forcer le rafraîchissement sans déconnecter
st.caption("🔄 Mise à jour automatique toutes les 30s")
