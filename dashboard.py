import streamlit as st
from supabase import create_client
import urllib.parse

# ---------------- CONFIG PAGE ----------------
st.set_page_config(
    page_title="MAVA • Mes Commandes",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- CSS GLOBAL ----------------
st.markdown("""
<style>
.stApp {
    background-color: #050505;
    color: #FFFFFF;
}

.card {
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 18px;
}

.card.pending {
    border-left: 6px solid #B11205;
    background: #120202;
}

.card.done {
    border-left: 6px solid #1FA24A;
    background: #03140A;
}

.badge {
    font-weight: 700;
    margin-bottom: 6px;
}

.price {
    font-size: 1.2rem;
    font-weight: 800;
}

button {
    width: 100%;
    border-radius: 10px !important;
}

input {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SUPABASE ----------------
@st.cache_resource
def supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = supabase_client()

# ---------------- UTILS ----------------
def format_price(val):
    try:
        return f"{int(val):,}".replace(",", ".") + " FCFA"
    except:
        return "—"

# ---------------- LOGIN ----------------
if "vendeur_phone" not in st.session_state:

    st.markdown("<h2 style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    phone = st.text_input("Numéro WhatsApp", placeholder="07XXXXXXXX")

    if st.button("Accéder à mes commandes"):
        if phone.strip():
            st.session_state.vendeur_phone = phone.strip()
            st.rerun()

    st.stop()

# ---------------- DASHBOARD ----------------
vendeur_phone = st.session_state.vendeur_phone

st.markdown("## 🔗 MES COMMANDES")

# Fetch commandes
res = supabase.table("orders") \
    .select("*") \
    .eq("phone_vendeur", vendeur_phone) \
    .order("created_at", desc=True) \
    .execute()

orders = res.data or []

if not orders:
    st.info("Aucune commande pour le moment.")
    st.stop()

# ---------------- DISPLAY COMMANDES ----------------
for order in orders:
    is_done = order["statut"] == "Livré"
    card_class = "done" if is_done else "pending"
    badge = "✅ LIVRÉ" if is_done else "⏳ À LIVRER"

    st.markdown(f"""
    <div class="card {card_class}">
        <div class="badge">{badge}</div>
        <b>👤 {order.get('nom_client','Client')}</b><br>
        📍 {order.get('quartier','—')}<br>
        🛍️ {order.get('articles','—')}<br><br>
        <div class="price">💰 {format_price(order.get('prix'))}</div>
    </div>
    """, unsafe_allow_html=True)

    # Boutons
    col1, col2 = st.columns(2)

    with col1:
        phone_client = str(order.get("telephone","")).replace(" ", "")
        msg = urllib.parse.quote("Bonjour, je vous contacte pour votre livraison.")
        st.markdown(
            f'<a href="https://wa.me/{phone_client}?text={msg}" target="_blank">💬 WhatsApp Client</a>',
            unsafe_allow_html=True
        )

    with col2:
        if not is_done:
            if st.button("Livraison effectuée ✅", key=f"done_{order['id']}"):
                supabase.table("orders") \
                    .update({"statut": "Livré"}) \
                    .eq("id", order["id"]) \
                    .execute()
                st.rerun()
        else:
            if st.button("Annuler 🔄", key=f"undo_{order['id']}"):
                supabase.table("orders") \
                    .update({"statut": "À livrer"}) \
                    .eq("id", order["id"]) \
                    .execute()
                st.rerun()
