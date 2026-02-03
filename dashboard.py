import streamlit as st
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

# ================= PERSISTANCE & ÉTAT =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 

if "vendeur_phone" not in st.session_state and "v" in st.query_params:
    st.session_state.vendeur_phone = st.query_params["v"]

# ================= COULEURS DYNAMIQUES =================
bg_color = "#000000" if st.session_state.dark_mode else "#FFFFFF"
card_bg = "#121212" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"
sub_text = "#BBBBBB" if st.session_state.dark_mode else "#666666"
border_color = "#333333" if st.session_state.dark_mode else "#EEEEEE"
price_color = "#FF0000" if st.session_state.dark_mode else "#700D02"

# ================= CSS DYNAMIQUE =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .main-title {{ font-size: 2.2rem !important; font-weight: 800 !important; color: {text_color} !important; display: block; margin-top: 10px; }}
    .card {{ position: relative; border-radius: 15px; padding: 20px; margin-bottom: 20px; background: {card_bg}; border: 1px solid {border_color}; box-shadow: 0px 4px 15px rgba(0,0,0,0.4); overflow: hidden; }}
    .card.pending::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #FF0000; }}
    .card.done::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #1FA24A; }}
    .badge {{ position: absolute; top: 15px; right: 15px; padding: 5px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; color: white; }}
    .badge-pending {{ background-color: #FF0000; }}
    .badge-done {{ background-color: #1FA24A; }}
    .info-line {{ margin-bottom: 6px; font-size: 1.1rem; color: {text_color} !important; }}
    .price {{ font-size: 1.5rem; font-weight: 900; color: {price_color} !important; margin-top: 10px; }}
    .stTabs [data-baseweb="tab"] p {{ color: {text_color} !important; }}
    div.stButton > button {{ width: 100%; border-radius: 10px !important; height: 50px; font-weight: 700 !important; background-color: #700D02 !important; color: #FFFFFF !important; border: none !important; }}
    .login-text {{ color: {text_color} !important; font-weight: 600; text-align: left !important; }}
    .footer {{ margin-top: 50px; padding: 20px; text-align: center; color: {sub_text}; font-size: 0.75rem; border-top: 1px solid {border_color}; }}
</style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = get_supabase()

# ================= TOP BAR =================
col_left, col_mid, col_right = st.columns([0.7, 0.1, 0.2])
with col_right:
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ================= LOGIQUE D'AFFICHAGE =================
if "vendeur_phone" not in st.session_state:
    # Récupération automatique du numéro sauvegardé
    components.html("""
        <script>
            const saved = localStorage.getItem('mava_saved_num');
            if (saved && !window.location.search.includes('v=')) {
                window.parent.location.search = '?v=' + saved;
            }
        </script>
    """, height=0)

    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    
    # Champ pré-rempli via l'URL (v=...)
    default_num = st.query_params.get("v", "")
    phone_input = st.text_input("Numéro", value=default_num, placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = phone_input.replace(" ", "").replace("+", "")
            if len(num) == 10 and num.startswith("0"): num = "225" + num
            
            # Vérification si le vendeur existe
            check = supabase.table("orders").select("phone_vendeur").eq("phone_vendeur", num).limit(1).execute()
            
            if check.data:
                st.session_state.vendeur_phone = num
                st.query_params["v"] = num
                components.html(f"<script>localStorage.setItem('mava_saved_num', '{num}');</script>", height=0)
                st.rerun()
            else:
                st.error("Numéro non reconnu.")
else:
    # ================= DASHBOARD =================
    vendeur_phone = st.session_state.vendeur_phone
    
    if st.button("Se déconnecter 🚪", key="logout"):
        components.html("<script>localStorage.removeItem('mava_saved_num');</script>", height=0)
        del st.session_state.vendeur_phone
        st.query_params.clear()
        st.rerun()

    st.markdown("<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    res = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order("created_at", desc=True).execute()
    orders = res.data or []

    pending = [o for o in orders if o["statut"] != "Livré"]
    done = [o for o in orders if o["statut"] == "Livré"]

    tab1, tab2 = st.tabs([f"🔔 En cours ({len(pending)})", f"✅ Livrées ({len(done)})"])

    with tab1:
        if not pending:
            st.markdown(f"<p style='text-align:center; color:{sub_text};'>Aucune commande.</p>", unsafe_allow_html=True)
        for order in pending:
            # Correction prix : float puis int pour éviter le crash
            prix_brut = order.get('prix', 0)
            prix_clean = int(float(prix_brut)) if prix_brut else 0
            
            st.markdown(f"""
            <div class="card pending">
                <div class="badge badge-pending">À LIVRER 📦</div>
                <div class="info-line">🔢 <b>Commande :</b> #{order.get('order_number','—')}</div>
                <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
                <div class="price">{prix_clean:,} FCFA</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("MARQUER COMME LIVRÉ", key=f"p_{order['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                st.rerun()

    with tab2:
        for order in done:
            prix_brut = order.get('prix', 0)
            prix_clean = int(float(prix_brut)) if prix_brut else 0
            
            st.markdown(f"""
            <div class="card done">
                <div class="badge badge-done">LIVRÉE ✅</div>
                <div class="info-line">🔢 <b>Commande :</b> #{order.get('order_number','—')}</div>
                <div class="price" style="color:#1FA24A !important;">{prix_clean:,} FCFA</div>
            </div>
            """, unsafe_allow_html=True)

# ================= FOOTER UNIQUE =================
st.markdown(f'<div class="footer">MAVA © 2026 • Stable Sync Release</div>', unsafe_allow_html=True)
# ================= FOOTER UNIQUE =================
st.markdown(f'<div class="footer">MAVA © 2026 • Stable Sync Release</div>', unsafe_allow_html=True)
