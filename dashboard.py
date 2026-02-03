import streamlit as st
from supabase import create_client
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
hr_color = "#FFFFFF" if st.session_state.dark_mode else "#000000"

# ================= CSS DYNAMIQUE =================
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .main-title {{ font-size: 2.2rem !important; font-weight: 800 !important; color: {text_color} !important; display: block; margin-top: 10px; }}
    .card {{ position: relative; border-radius: 15px; padding: 15px; margin-bottom: 5px; background: {card_bg}; border: 1px solid {border_color}; overflow: hidden; }}
    .info-line {{ margin-bottom: 8px; font-size: 1.05rem; color: {text_color} !important; }}
    .price {{ font-size: 1.4rem; font-weight: 900; color: {price_color} !important; margin-top: 10px; }}
    .stTabs [data-baseweb="tab"] p {{ color: {text_color} !important; }}
    
    /* Bouton Livrée */
    div.stButton > button {{ width: 100%; border-radius: 10px !important; height: 45px; font-weight: 700 !important; background-color: #700D02 !important; color: #FFFFFF !important; border: none !important; }}
    
    /* Bouton WhatsApp */
    .wa-btn {{ display: flex; align-items: center; justify-content: center; background-color: #25D366; color: white !important; text-decoration: none; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 8px; text-align: center; }}
    
    .separator {{ border: 0; height: 1px; background: {hr_color}; margin: 25px 0; opacity: 0.3; }}
    .login-text {{ color: {text_color} !important; font-weight: 600; }}
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
    # FORCE LE PRÉ-REMPLISSAGE PAR LE DISQUE DUR
    components.html("""
        <script>
            const saved = localStorage.getItem('mava_v_phone');
            const params = new URLSearchParams(window.location.search);
            if (saved && params.get('v') !== saved) {
                params.set('v', saved);
                window.parent.location.search = params.toString();
            }
        </script>
    """, height=0)

    st.image("https://raw.githubusercontent.com/Romyse226/mon-dashboard-livraison/main/mon%20logo%20mava.png", width=140)
    st.markdown("<h2 class='login-text'>Bienvenue</h2>", unsafe_allow_html=True)
    
    default_num = st.query_params.get("v", "")
    phone_input = st.text_input("Numéro", value=default_num, placeholder="07XXXXXXXX", label_visibility="collapsed")
    
    if st.button("Suivre mes commandes"):
        if phone_input.strip():
            num = phone_input.replace(" ", "").replace("+", "")
            if len(num) == 10 and num.startswith("0"): num = "225" + num
            
            check = supabase.table("orders").select("phone_vendeur").eq("phone_vendeur", num).limit(1).execute()
            if check.data:
                st.session_state.vendeur_phone = num
                st.query_params["v"] = num
                # Sauvegarde immédiate
                components.html(f"<script>localStorage.setItem('mava_v_phone', '{num}');</script>", height=0)
                st.rerun()
            else:
                st.error("Numéro non autorisé.")
else:
    # ================= DASHBOARD =================
    v_phone = st.session_state.vendeur_phone
    
    if st.button("Se déconnecter 🚪"):
        components.html("<script>localStorage.removeItem('mava_v_phone');</script>", height=0)
        del st.session_state.vendeur_phone
        st.query_params.clear()
        st.rerun()

    st.markdown("<span class='main-title'>Mes Commandes</span>", unsafe_allow_html=True)

    res = supabase.table("orders").select("*").eq("phone_vendeur", v_phone).order("created_at", desc=True).execute()
    orders = res.data or []

    tab1, tab2 = st.tabs([f"🔔 En cours", f"✅ Livrées"])

    def display_order(order, is_pending):
        try:
            prix_clean = int(float(order.get('prix', 0)))
        except:
            prix_clean = 0
            
        st.markdown(f"""
        <div class="card">
            <div class="info-line" style="font-weight:bold; font-size:1.2rem;">Commande N°{order.get('order_number','—')}</div>
            <div class="info-line">🛍️ <b>Article :</b> {order.get('product','—')}</div>
            <div class="info-line">📍 <b>Lieu :</b> {order.get('quartier','—')}</div>
            <div class="info-line">💰 <b>Prix :</b> <span style="color:{price_color}; font-weight:bold;">{prix_clean:,} FCFA</span></div>
            <div class="info-line">📞 <b>Tel :</b> {order.get('telephone','—')}</div>
        """, unsafe_allow_html=True)
        
        if is_pending:
            # Bouton Marquer comme livrée
            if st.button("Marquer comme livrée", key=f"btn_{order['id']}"):
                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                st.rerun()
            
            # Bouton WhatsApp
            wa_num = str(order.get('phone_client', '')).replace(" ", "").replace("+", "")
            if wa_num:
                st.markdown(f'<a href="https://wa.me/{wa_num}" target="_blank" class="wa-btn">💬 Contacter le client</a>', unsafe_allow_html=True)
        
        st.markdown('</div><div class="separator"></div>', unsafe_allow_html=True)

    with tab1:
        pending = [o for o in orders if o["statut"] != "Livré"]
        if not pending: st.info("Aucune commande en cours.")
        for o in pending: display_order(o, True)

    with tab2:
        done = [o for o in orders if o["statut"] == "Livré"]
        for o in done: display_order(o, False)

# ================= FOOTER UNIQUE =================
st.markdown('<div class="footer">MAVA © 2026 • Stable Sync Release</div>', unsafe_allow_html=True)
