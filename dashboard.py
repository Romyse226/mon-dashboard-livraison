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

# ================= CSS DYNAMIQUE & INTERACTIF =================
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Titre et Icône de copie */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }

    /* Style des Cartes */
    .card {
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        background: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .card.pending { border-left: 10px solid #700D02; }
    
    .info-line { margin-bottom: 8px; font-size: 1.05rem; }
    .price { font-size: 1.5rem; font-weight: 900; color: #700D02; }

    /* Boutons Ultra-Réactifs */
    div.stButton > button {
        width: 100%;
        border-radius: 15px !important;
        height: 55px;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: transform 0.1s active;
    }
    
    /* Effet clic sur mobile */
    div.stButton > button:active {
        transform: scale(0.96);
    }

    /* Bouton WhatsApp noir sur vert */
    .btn-whatsapp {
        background-color: #25D366 !important;
        color: #000000 !important;
        border-radius: 15px;
        text-align: center;
        padding: 15px;
        display: block;
        text-decoration: none;
        font-weight: 800;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.2);
    }

    /* Login Page */
    .login-box { text-align: center; padding-top: 50px; }
</style>

<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert("Lien copié !");
    }, function(err) {
        console.error('Erreur lors de la copie', err);
    });
}
</script>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = supabase_client()

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
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=150)
    st.markdown("## Bienvenue")
    st.write("Entrez votre numéro pour suivre vos commandes")
    
    phone_input = st.text_input("Numéro WhatsApp", placeholder="Ex: 07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("ACCÉDER AU DASHBOARD", type="primary"):
        if phone_input.strip():
            st.session_state.vendeur_phone = normalize_phone(phone_input.strip())
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD CORE =================
vendeur_phone = st.session_state.vendeur_phone
dashboard_link = f"https://mava.streamlit.app/?vendeur={vendeur_phone}"

# Header avec bouton copie
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown(f"## Mes Commandes")
with col_h2:
    # Bouton de copie invisible mais avec icone
    if st.button("🔗", help="Copier mon lien"):
        st.write(f'<script>copyToClipboard("{dashboard_link}")</script>', unsafe_allow_html=True)
        st.toast("Lien copié dans le presse-papier !")

# Logo à droite (optionnel selon le rendu souhaité)
st.sidebar.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png")

# ================= AUTO REFRESH INVISIBLE (30s) =================
if "refresh_timer" not in st.session_state:
    st.session_state.refresh_timer = time.time()

if time.time() - st.session_state.refresh_timer > 30:
    st.session_state.refresh_timer = time.time()
    st.rerun()

# ================= FETCH DATA =================
res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
orders = res.data or []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

# ================= AFFICHAGE DES COMMANDES =================
if pending:
    st.markdown("#### 🔔 NOUVELLES")
    for order in pending:
        # On utilise une clé unique basée sur l'ID et le timestamp pour éviter les bugs de cache
        order_id = order['id']
        
        st.markdown(f"""
        <div class="card pending">
            <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
            <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
            <div class="info-line">🛍️ <b>Article :</b> {order.get('articles','—')}</div>
            <div class="price">{format_price(order.get('prix'))}</div>
        </div>
        """, unsafe_allow_html=True)
        
        phone_c = normalize_phone(order.get("telephone",""))
        msg = urllib.parse.quote("Bonjour, je suis en route pour votre livraison MAVA.")
        
        # WhatsApp Link
        st.markdown(f'<a class="btn-whatsapp" href="https://wa.me/{phone_c}?text={msg}" target="_blank">CONTACTER LE CLIENT</a>', unsafe_allow_html=True)
        
        # Bouton Action Direct (C'est ici qu'on gère le "clic unique")
        if st.button(f"MARQUER COMME LIVRÉ", key=f"ship_{order_id}", type="primary"):
            supabase.table("orders").update({"statut": "Livré"}).eq("id", order_id).execute()
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

if done:
    with st.expander("✅ Historique (Livrés)"):
        for order in done:
            st.markdown(f"""
            <div style="padding:10px; border-bottom:1px solid #eee;">
                <b>{order.get('nom_client')}</b> - {format_price(order.get('prix'))}<br>
                <small>{order.get('articles')}</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Annuler", key=f"unship_{order['id']}"):
                supabase.table("orders").update({"statut": "À livrer"}).eq("id", order['id']).execute()
                st.rerun()
