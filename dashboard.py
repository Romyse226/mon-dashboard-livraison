iimport streamlit as st
from supabase import create_client
import urllib.parse
import time
import streamlit.components.v1 as components

# ================= CONFIG =================
st.set_page_config(
    page_title="MAVA",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= PERSISTANCE & ÉTAT (PWA READY) =================
# Empêche l'app de revenir à zéro
if "vendeur_phone" not in st.session_state and "v" in st.query_params:
    st.session_state.vendeur_phone = st.query_params["v"]

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 

# ================= NOTIFICATIONS JAVASCRIPT =================
# Bloc pour demander l'accès et gérer les notifs mobiles
def inject_notification_logic():
    js_code = """
    <script>
    const requestPermission = () => {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Notifs autorisées");
                document.getElementById("notif-banner").style.display = "none";
            }
        });
    }

    // Vérification au chargement
    if (Notification.permission === "default") {
        // Affiche la bannière si pas encore décidé
    } else if (Notification.permission === "granted") {
        // Déjà autorisé
    }
    </script>
    """
    components.html(js_code, height=0)

# ================= CSS DYNAMIQUE =================
# (Gardé intact comme demandé, avec ajout du style bannière notif)
bg_color = "#000000" if st.session_state.dark_mode else "#FFFFFF"
card_bg = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
price_color = "#FF0000" if st.session_state.dark_mode else "#700D02"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .notif-banner {{
        background: #700D02; color: white; padding: 15px; border-radius: 10px;
        margin-bottom: 20px; text-align: center; font-family: sans-serif;
    }}
    .notif-btn {{
        background: white; color: #700D02; border: none; padding: 8px 15px;
        border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px;
    }}
    /* ... reste de ton CSS inchangé ... */
    .stButton {{ display: flex; justify-content: flex-end; }}
    .main-title {{ font-size: 2.2rem !important; font-weight: 800 !important; color: {text_color} !important; display: block; margin-top: 10px; }}
    .card {{ position: relative; border-radius: 15px; padding: 20px; margin-bottom: 20px; background: {card_bg}; border: 1px solid {border_color}; box-shadow: 0px 4px 15px rgba(0,0,0,0.4); overflow: hidden; }}
    .card.pending::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #FF0000; box-shadow: 2px 0px 12px #FF0000; }}
    .card.done::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #1FA24A; box-shadow: 2px 0px 12px #1FA24A; }}
    .badge {{ position: absolute; top: 15px; right: 15px; padding: 5px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; color: white; }}
    .badge-pending {{ background-color: #FF0000; box-shadow: 0 0 8px #FF0000; }}
    .badge-done {{ background-color: #1FA24A; box-shadow: 0 0 8px #1FA24A; }}
    .info-line {{ margin-bottom: 6px; font-size: 1.1rem; color: {text_color} !important; width: 85%; }}
    .price {{ font-size: 1.5rem; font-weight: 900; color: {price_color} !important; margin-top: 10px; }}
    div.stButton > button {{ width: 100%; border-radius: 10px !important; height: 50px; font-weight: 700 !important; background-color: #700D02 !important; color: #FFFFFF !important; border: none !important; }}
    .footer {{ margin-top: 50px; padding: 20px; text-align: center; color: {sub_text}; font-size: 0.75rem; border-top: 1px solid {border_color}; }}
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE SYNC =================
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

def fetch_data():
    """Récupération synchronisée et forcée"""
    if "vendeur_phone" in st.session_state:
        res = supabase.table("orders").select("*").eq("phone_vendeur", st.session_state.vendeur_phone).order("created_at", desc=True).execute()
        return res.data or []
    return []

# ================= INTERFACE PRINCIPALE =================
inject_notification_logic()

# Bannière Notification Mobile (Point 3)
if "vendeur_phone" in st.session_state:
    st.markdown("""
        <div id="notif-banner" class="notif-banner">
            📢 Activer les notifications pour ne rater aucune commande ?
            <br><button class="notif-btn" onclick="requestPermission()">AUTORISER</button>
            <button class="notif-btn" style="background:transparent; color:white; border:1px solid white;" onclick="this.parentElement.style.display='none'">FERMER</button>
        </div>
    """, unsafe_allow_html=True)

# Toggle Mode
col_left, col_mid, col_right = st.columns([0.7, 0.1, 0.2])
with col_right:
    label_mode = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(label_mode, key="mode_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ================= LOGIN / DASHBOARD LOGIC =================
if "vendeur_phone" not in st.session_state:
    # (Bloc Login inchangé mais sécurisé)
    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown(f"<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    phone_input = st.text_input("Numéro", placeholder="07XXXXXXXX", label_visibility="collapsed")
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            # Normalisation et injection session
            num = phone_input.replace(" ", "").replace("+", "")
            if len(num) == 10 and num.startswith("0"): num = "225" + num
            st.session_state.vendeur_phone = num
            st.query_params["v"] = num
            st.rerun()
else:
    # Dashboard avec Sync forcée
    orders = fetch_data()
    
    st.markdown(f"<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with tab1:
        for order in pending:
            with st.container():
                st.markdown(f"""
                <div class="card pending">
                    <div class="badge badge-pending">À LIVRER 📦</div>
                    <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                    <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
                    <div class="price">{int(order.get('prix', 0)):,} FCFA</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Update (Point 1)
                if st.button("MARQUER COMME LIVRÉ", key=f"btn_{order['id']}"):
                    supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                    st.toast("Statut mis à jour sur Supabase !")
                    time.sleep(0.5)
                    st.rerun()

    with tab2:
        for order in done:
            st.markdown(f"""
            <div class="card done">
                <div class="badge badge-done">LIVRÉE ✅</div>
                <div class="info-line">👤 <b>Client :</b> {order.get('nom_client','—')}</div>
                <div class="price" style="color:#1FA24A !important;">{int(order.get('prix', 0)):,} FCFA</div>
            </div>
            """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown(f'<div class="footer">MAVA © 2026 • Stable Sync Release</div>', unsafe_allow_html=True)

# Auto-refresh intelligent pour la synchro (Point 4)
if "vendeur_phone" in st.session_state:
    time.sleep(2) # Petite pause pour laisser respirer le serveur
    st.rerun()
