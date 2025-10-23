import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Compteur de Clics Simple", layout="centered")

# --- Initialisation de l'état ---
# Si 'count' n'existe pas dans st.session_state, il est initialisé à 0
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- Fonctions de Logique ---
def increment_counter():
    """Fonction appelée lors du clic pour incrémenter le compteur."""
    st.session_state.count += 1

def reset_counter():
    """Fonction pour réinitialiser le compteur."""
    st.session_state.count = 0

# --- Interface Utilisateur ---
st.title("Compteur de Clics Interactif")
st.write("Cliquez sur le bouton ci-dessous pour incrémenter le compteur.")

# Affichage du compteur
st.markdown(
    f"""
    <div style="
        font-size: 4em;
        font-weight: bold;
        color: #007bff;
        padding: 20px;
        border: 3px solid #007bff;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
        background-color: #f0f8ff;
    ">
        {st.session_state.count}
    </div>
    """,
    unsafe_allow_html=True
)

# Bouton d'incrémentation
# Utilisation du paramètre on_click pour lier le bouton à la fonction d'incrémentation
st.button(
    "Cliquez ici pour compter!",
    on_click=increment_counter,
    type="primary",
    use_container_width=True
)

# Bouton de réinitialisation
st.button(
    "Réinitialiser le Compteur",
    on_click=reset_counter,
    type="secondary",
    use_container_width=True
)

st.caption("Ce compteur utilise st.session_state pour maintenir le nombre de clics.")
