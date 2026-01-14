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

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background-color: #F7F7F7;
    color: #111;
}

.card {
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
    background: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

.card.pending {
    border-left: 6px solid #700D02;
}

.card.done {
    border-left: 6px solid #1FA24A;
    opacity: 0.9;
}

.badge {
    font-weight: 700;
    margin-bottom: 10px;
    font-size: 0.9rem;
}

.price {
    font-size: 1.3rem;
    font-weight: 800;
    margin-top: 8px;
}

.btn-primary {
    background-color: #700D02 !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}

.btn-whatsapp {
    background-color: #25D366 !important;
    color: white !important;
    border-radius: 10px !important;
    text-align: center;
    padding: 8px;
    display: block;
    font-weight: 600;
}

.login-box {
    max-width: 420px;
    margin: auto;
    margin-top: 80px;
    padding: 30px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    text-align: center;
}
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
    phone = phone.replace(" ", "")
    if phone.startswith("0"):
        return "225" + phone
    return phone

def format_price(val):
    try:
        return f"{int(val):,}".replace(",", ".") + " FCFA"
    except:
        return "—"

# ================= AUTO REFRESH =================
st.experimental_set_query_params(t=int(time.time()))
time.sleep(0.01)

# ================= LOGIN =================
if "vendeur_phone" not in st.session_state:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("mava.png", width=120)
    st.markdown("### Se connecter")

    phone_input = st.text_input(
        "Numéro WhatsApp",
        placeholder="07XXXXXXXX"
    )

    if st.button("Accéder au dashboard", type="primary"):
        if phone_input.strip():
            st.session_state.vendeur_phone = normalize_phone(phone_input.strip())
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= DASHBOARD =================
vendeur_phone = st.session_state.vendeur_phone
dashboard_link = f"https://mava.streamlit.app/?vendeur={vendeur_phone}"

st.markdown("## Mes Commandes")

st.code(dashboard_link, language="text")

# ================= FETCH =================
res = supabase.table("orders") \
    .select("*") \
    .eq("phone_vendeur", vendeur_phone) \
    .order("created_at", desc=True) \
    .execute()

orders = res.data or []

pending = [o for o in orders if o["statut"] != "Livré"]
done = [o for o in orders if o["statut"] == "Livré"]

if pending:
    st.markdown("### 🔔 Nouvelles commandes")

for order in pending + done:

    is_done = order["statut"] == "Livré"
    card_class = "done" if is_done else "pending"
    badge = "LIVRÉ" if is_done else "À LIVRER"

    st.markdown(f"""
    <div class="card {card_class}">
        <div class="badge">{badge}</div>
        <b>Client :</b> {order.get('nom_client','—')}<br>
        <b>Lieu :</b> {order.get('quartier','—')}<br>
        <b>Article :</b> {order.get('articles','—')}
        <div class="price">{format_price(order.get('prix'))}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        phone_client = normalize_phone(order.get("telephone",""))
        msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison.")
        st.markdown(
            f'<a class="btn-whatsapp" href="https://wa.me/{phone_client}?text={msg}" target="_blank">WhatsApp Client</a>',
            unsafe_allow_html=True
        )

    with col2:
        if not is_done:
            if st.button("Livraison effectuée", key=f"done_{order['id']}"):
                supabase.table("orders").update(
                    {"statut": "Livré"}
                ).eq("id", order["id"]).execute()
                st.rerun()
        else:
            if st.button("Annuler livraison", key=f"undo_{order['id']}"):
                supabase.table("orders").update(
                    {"statut": "À livrer"}
                ).eq("id", order["id"]).execute()
                st.rerun()
