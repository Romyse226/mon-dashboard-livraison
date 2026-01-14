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

# ================= CSS : VISIBILITÉ TOTALE & MOBILE =================
st.markdown("""
<style>
    /* Fond blanc pur pour un contraste maximum */
    .stApp { 
        background-color: #FFFFFF !important; 
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* Textes en noir profond */
    h1, h2, h3, h4, p, span, div {
        color: #111111 !important;
    }

    /* Card Design avec bordures visibles */
    .card {
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 15px;
        background: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid #EEEEEE; /* Bordure grise claire pour détacher du fond */
    }
    .card.pending { border-left: 10px solid #700D02; }

    /* Infos de la commande */
    .info-line { 
        margin-bottom: 6px; 
        font-size: 1.1rem; 
        color: #111111 !important;
    }
    .price { 
        font-size: 1.6rem; 
        font-weight: 900; 
        color: #700D02 !important; 
        margin-top: 10px;
    }

    /* Bouton WhatsApp : Texte NOIR sur Fond VERT */
    .btn-whatsapp {
        background-color: #25D366 !important;
        color: #000000 !important;
        border-radius: 12px;
        text-align: center;
        padding: 15px;
        display: block;
        text-decoration: none;
        font-weight: 800;
        margin-bottom: 10px;
        border: 1px solid #1DA851;
    }

    /* Bouton Streamlit : Texte BLANC sur Fond ROUGE MAVA */
    div.stButton > button {
        width: 100%;
        border-radius: 12px !important;
        height: 55px;
        font-weight: 700 !important;
        background-color: #700D02 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* Page de connexion */
    .login-box { text-align: center; padding-top: 40px; }
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = supabase_client()

# ================= PERSISTANCE SESSION (URL) =================
# On récupère le numéro depuis l'URL si il existe
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

# ================= LOGIN PAGE =================
if "vendeur_phone" not in st.session_state:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("## Bienvenue")
    st.markdown("<p style='color:#666 !important;'>Entrez votre numéro pour suivre vos commandes</p>", unsafe_allow_html=True)
    
    phone_input = st.text_input("Numéro WhatsApp", placeholder="Ex: 07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("ACCÉDER AU DASHBOARD"):
        if phone_input.strip():
            num = normalize_phone(phone_input.strip())
            st.session_state.vendeur_phone = num
            # On ajoute le numéro dans l'URL pour ne pas être déconnecté
            st.query_params["v"] = num
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD =================
vendeur_phone = st.session_state.vendeur_phone

# Header
col_h1, col_h2 = st.columns([0.85, 0.15])
with col_h1:
    st.markdown("## Mes Commandes")
with col_h2:
    # Bouton de copie
    dash_url = f"https://mava.streamlit.app/?v={vendeur_phone}"
    if st.button("🔗"):
        st.toast("Lien copié !")
        st.write(f'<script>navigator.clipboard.writeText("{dash_url}")</script>', unsafe_allow_html=True)

# Logo discret
st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=60)

# ================= AUTO REFRESH INVISIBLE (30s) =================
if "last_ts" not in st.session_state:
    st.session_state.last_ts = time.time()

if time.time() - st.session_state.last_ts > 30:
    st.session_state.last_ts = time.time()
    st.rerun()

# ================= FETCH & DISPLAY =================
res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
orders = res.data or []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

if not orders:
    st.info("Aucune commande trouvée pour ce numéro.")

if pending:
    st.markdown("#### 🔔 EN COURS")
    for order in pending:
        st.markdown(f"""
        <div class="card pending">
            <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
            <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
            <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
            <div class="price">{format_price(order.get('prix'))}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # WhatsApp
        p_c = normalize_phone(order.get("telephone",""))
        msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison MAVA.")
        st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{p_c}?text={msg}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
        
        # Action (Une seule pression suffit)
        if st.button("MARQUER COMME LIVRÉ", key=f"ok_{order['id']}"):
            supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

if done:
    with st.expander("✅ Historique des livraisons"):
        for order in done:
            st.write(f"**{order.get('nom_client')}** - {format_price(order.get('prix'))}")
            if st.button("Annuler", key=f"rev_{order['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order['id']).execute()
                st.rerun()
