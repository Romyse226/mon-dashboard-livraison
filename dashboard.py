import streamlit as st
from supabase import create_client, Client
import urllib.parse

# 1. Config Elite & UI Design
st.set_page_config(page_title="Livreur Pro - Elite", layout="wide", initial_sidebar_state="expanded")

# CSS personnalisé pour le look "Luxe" (Inspiré de l'image)
st.markdown("""
    <style>
    /* Fond principal sombre */
    .stApp {
        background-color: #050505;
        color: #FFFFFF;
    }
    
    /* Barre latérale bordeaux très sombre */
    [data-testid="stSidebar"] {
        background-color: #1a0301;
        border-right: 1px solid #700D02;
    }
    
    /* Cartes de commandes style verre fumé */
    .order-card {
        background: linear-gradient(145deg, #1c1c1c, #0d0d0d);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #333;
        border-left: 8px solid #700D02;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Titre des cartes */
    .card-title {
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Bouton Livré (Bordeaux Néon) */
    .stButton>button {
        background: linear-gradient(90deg, #700D02, #a31403);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(112, 13, 2, 0.4);
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(112, 13, 2, 0.6);
        transform: translateY(-2px);
    }

    /* Bouton WhatsApp (Vert Émeraude) */
    .wa-button {
        background: linear-gradient(90deg, #128C7E, #25D366);
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-decoration: none;
        display: block;
        text-align: center;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    /* Input login */
    input {
        border-radius: 10px !important;
        border: 1px solid #700D02 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initialisation Supabase
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
except Exception as e:
    st.error("Erreur de connexion aux secrets.")

# 3. Sidebar de Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968841.png", width=60)
    st.markdown("### 🔑 Espace Commerçant")
    vendeur_phone = st.text_input("Numéro WhatsApp", placeholder="22507...")
    st.markdown("---")
    st.info("Le statut est mis à jour en temps réel pour vos livreurs.")

# 4. Contenu Principal
if vendeur_phone:
    st.title("📦 Tableau des Livraisons")
    
    try:
        # Requête propre avec 'desc=True'
        response = supabase.table("orders").select("*").eq("phone_vendeur", vendeur_phone).order('created_at', desc=True).execute()
        orders = response.data

        if not orders:
            st.warning("Aucune commande n'est enregistrée pour ce numéro.")
        else:
            for order in orders:
                with st.container():
                    # Utilisation de colonnes pour aligner le contenu et les actions
                    col_info, col_action = st.columns([2.5, 1])
                    
                    with col_info:
                        # Design de la carte via Markdown
                        st.markdown(f"""
                        <div class="order-card">
                            <div class="card-title">👤 {order.get('nom_client', 'Client')}</div>
                            <p style='color:#bbb; margin-bottom:5px;'>📍 <b>Lieu:</b> {order.get('quartier', 'Abidjan')}</p>
                            <p style='color:#bbb; margin-bottom:5px;'>🛍️ <b>Article:</b> {order.get('articles', 'Non précisé')}</p>
                            <p style='font-size:1.2rem; color:#FFFFFF;'>💰 <b>{order.get('prix', 0)} FCFA</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_action:
                        st.write("") # Espacement
                        # Bouton WhatsApp avec numéro client
                        client_phone = order.get('telephone', '').replace(" ", "")
                        msg = urllib.parse.quote(f"Bonjour {order.get('nom_client', '')}, je suis votre livreur...")
                        wa_url = f"https://wa.me/{client_phone}?text={msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">💬 WHATSAPP CLIENT</a>', unsafe_allow_html=True)

                        # Bouton de Statut
                        if order.get('statut') == 'À livrer':
                            if st.button(f"MARQUER LIVRÉ ✅", key=f"btn_{order['id']}"):
                                supabase.table("orders").update({"statut": "Livré"}).eq("id", order['id']).execute()
                                st.rerun()
                        else:
                            st.markdown("<div style='text-align:center; padding:10px; color:#4CAF50; font-weight:700;'>✅ LIVRAISON TERMINÉE</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

else:
    # Page d'accueil si pas de numéro
    st.markdown("""
    <div style='text-align:center; padding-top:100px;'>
        <h1 style='color:#700D02; font-size:3rem;'>LIVREUR PRO ELITE</h1>
        <p style='font-size:1.5rem; color:#777;'>Entrez votre numéro WhatsApp à gauche pour gérer vos ventes.</p>
    </div>
    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erreur de données : {e}")
