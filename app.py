import random
import sqlite3
from sqlite3 import Error

import pandas as pd
import streamlit as st

# Assurez-vous que graphviz est disponible si vous utilisez une version locale de Streamlit
# Si ce n'est pas le cas, le diagramme sera affiché en code.

# --- Configuration de la Page et Styles ---
st.set_page_config(
    page_title="SQL Sandbox",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 1. Définitions des Schémas (Graphviz DOT Language) ---

HR_ERD = """
digraph G {
    graph [rankdir=LR, layout=dot, bgcolor="#f0f2f6", fontname="Inter"];
    node [shape=box, style="filled,rounded", color="#0058b8", fontcolor=white, fontname="Inter"];
    edge [color="#4a4a4a", fontname="Inter", fontsize=10];

    subgraph cluster_hr {
        label = "Ressources Humaines (HR)";
        bgcolor="#ffffff";
        
        employees [label="{employees|id (PK)|name|age|department|salary}", fillcolor="#3498db"];
        departments [label="{departments|id (PK)|name|manager_id (FK)|budget}", fillcolor="#2ecc71"];

        employees -> departments [label="gère", taillabel="1", headlabel="1..*"];
        employees -> departments [label="appartient à", taillabel="*..1", headlabel="1"];

        employees:department -> departments:name [dir=none, style=dotted, label="relation logique"];
        departments:manager_id -> employees:id;
    }
}
"""

LIBRARY_ERD = """
digraph G {
    graph [rankdir=LR, layout=dot, bgcolor="#f0f2f6", fontname="Inter"];
    node [shape=box, style="filled,rounded", color="#0058b8", fontcolor=white, fontname="Inter"];
    edge [color="#4a4a4a", fontname="Inter", fontsize=10];

    subgraph cluster_library {
        label = "Système de Bibliothèque";
        bgcolor="#ffffff";

        books [label="{books|id (PK)|title|author|category|publish_year}", fillcolor="#3498db"];
        members [label="{members|id (PK)|name|email|join_date}", fillcolor="#2ecc71"];
        loans [label="{loans|id (PK)|book_id (FK)|member_id (FK)|loan_date|return_date}", fillcolor="#e74c3c"];

        members -> loans [label="emprunte", taillabel="1..*", headlabel="1"];
        books -> loans [label="est emprunté", taillabel="1..*", headlabel="1"];
        
        loans:book_id -> books:id;
        loans:member_id -> members:id;
    }
}
"""

# --- 2. Jeux de Données et Schémas ---

SCHEMAS = {
    "HR": {
        "title": "Ressources Humaines (HR)",
        "erd": HR_ERD,
        "tables": {
            "employees": {
                "ddl": "id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, department TEXT, salary REAL",
                "data": [
                    (1, 'Jean Dupont', 35, 'IT', 55000), (2, 'Marie Lefebvre', 42, 'Marketing', 62000),
                    (3, 'Pierre Martin', 28, 'IT', 48000), (4, 'Sophie Bernard', 31, 'RH', 51000),
                    (5, 'Thomas Dubois', 45, 'Finance', 75000), (6, 'Lucie Moreau', 29, 'Marketing', 59000),
                    (7, 'David Petit', 50, 'Finance', 80000), (8, 'Laura Simon', 33, 'IT', 55000)
                ],
                "columns": ['id', 'name', 'age', 'department', 'salary']
            },
            "departments": {
                "ddl": "id INTEGER PRIMARY KEY, name TEXT NOT NULL, manager_id INTEGER, budget REAL",
                "data": [
                    (1, 'IT', 1, 500000), (2, 'Marketing', 2, 350000),
                    (3, 'RH', 4, 200000), (4, 'Finance', 5, 750000)
                ],
                "columns": ['id', 'name', 'manager_id', 'budget']
            }
        }
    },
    "Library": {
        "title": "Bibliothèque (Library)",
        "erd": LIBRARY_ERD,
        "tables": {
            "books": {
                "ddl": "id INTEGER PRIMARY KEY, title TEXT, author TEXT, category TEXT, publish_year INTEGER",
                "data": [
                    (101, 'Data Science 101', 'A. Smith', 'Science', 2019), (102, 'SQL Mastery', 'B. Jones', 'Informatique', 2022),
                    (103, 'Python Basics', 'C. Hall', 'Informatique', 2020), (104, 'Deep Learning', 'D. King', 'Science', 2023),
                    (105, 'La Peste', 'Albert Camus', 'Fiction', 1947), (106, '1984', 'George Orwell', 'Fiction', 1949)
                ],
                "columns": ['id', 'title', 'author', 'category', 'publish_year']
            },
            "members": {
                "ddl": "id INTEGER PRIMARY KEY, name TEXT, email TEXT, join_date TEXT",
                "data": [
                    (1, 'Alex Durand', 'alex@mail.com', '2023-01-01'), (2, 'Emma Leroy', 'emma@mail.com', '2023-03-15'),
                    (3, 'Marc Riviere', 'marc@mail.com', '2023-05-20')
                ],
                "columns": ['id', 'name', 'email', 'join_date']
            },
            "loans": {
                "ddl": "id INTEGER PRIMARY KEY, book_id INTEGER, member_id INTEGER, loan_date TEXT, return_date TEXT",
                "data": [
                    (1, 101, 1, '2023-10-01', '2023-10-15'), (2, 103, 2, '2023-10-05', '2023-10-20'),
                    (3, 102, 1, '2023-11-01', None), (4, 106, 3, '2023-11-02', None),
                ],
                "columns": ['id', 'book_id', 'member_id', 'loan_date', 'return_date']
            }
        }
    }
}

# --- 3. Questions et Exercices ---

quiz_questions = [
    {"q": "Quelle commande SQL est utilisée pour récupérer des données d'une table?", "o": ["SELECT", "UPDATE", "DELETE", "INSERT"], "c": "SELECT"},
    {"q": "Comment joindre deux tables en SQL?", "o": ["MERGE", "COMBINE", "JOIN", "CONNECT"], "c": "JOIN"},
    {"q": "Quelle clause est utilisée pour filtrer les résultats d'une requête SQL?", "o": ["FILTER", "HAVING", "GROUP", "WHERE"], "c": "WHERE"},
    {"q": "Comment trier les résultats d'une requête SQL par ordre croissant?", "o": ["SORT BY", "ORDER BY ... ASC", "ORDER ASC", "ARRANGE BY"], "c": "ORDER BY ... ASC"},
    {"q": "Quelle fonction SQL est utilisée pour compter le nombre d'enregistrements?", "o": ["SUM()", "COUNT()", "TOTAL()", "NUM()"], "c": "COUNT()"},
    {"q": "Quel opérateur est utilisé pour comparer des valeurs partielles?", "o": ["MATCH", "LIKE", "CONTAINS", "PATTERN"], "c": "LIKE"},
    {"q": "Quelle clause filtre les résultats AGREGÉS?", "o": ["WHERE", "FILTER BY", "GROUP BY", "HAVING"], "c": "HAVING"},
    {"q": "Quel type de JOIN retourne toutes les lignes de la table de GAUCHE?", "o": ["INNER JOIN", "RIGHT JOIN", "FULL JOIN", "LEFT JOIN"], "c": "LEFT JOIN"},
]

exercises = {
    "HR": {
        "Débutant": [
            {"title": "Employés IT", "desc": "Sélectionnez le nom et le salaire de tous les employés du département 'IT'. Triez par salaire croissant.", "expected": "SELECT name, salary FROM employees WHERE department = 'IT' ORDER BY salary ASC;"},
            {"title": "Salaires Élevés", "desc": "Trouvez le nom et l'âge de l'employé avec le salaire le plus élevé.", "expected": "SELECT name, age FROM employees ORDER BY salary DESC LIMIT 1;"},
        ],
        "Intermédiaire": [
            {"title": "Salaire Moyen par Dept", "desc": "Affichez le nom du département et son salaire moyen, mais seulement pour les départements ayant un salaire moyen supérieur à 55000. Nommez la moyenne 'avg_salary'. Triez par salaire moyen décroissant.", "expected": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department HAVING avg_salary > 55000 ORDER BY avg_salary DESC;"},
            {"title": "Managers et Budget", "desc": "Affichez le nom du manager, le nom du département qu'il gère et le budget de ce département. Utilisez la jointure sur l'ID du manager. Triez par budget croissant.", "expected": "SELECT e.name AS manager_name, d.name AS department_name, d.budget FROM employees e JOIN departments d ON e.id = d.manager_id ORDER BY d.budget ASC;"},
        ],
        "Avancé": [
            {"title": "Supérieur à la Moyenne", "desc": "Trouvez le nom et le salaire des employés qui gagnent plus que la moyenne des salaires de leur propre département. Triez par salaire.", "expected": "SELECT e1.name, e1.salary, e1.department FROM employees e1 WHERE e1.salary > (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e1.department) ORDER BY e1.salary DESC;"},
            {"title": "Classement des Salaires", "desc": "Affichez le nom, le département et le salaire de chaque employé, et ajoutez une colonne 'rank' indiquant le rang de leur salaire au sein de leur département (le plus haut salaire est rang 1).", "expected": "SELECT name, department, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank FROM employees ORDER BY department, salary_rank;"},
        ]
    },
    "Library": {
        "Débutant": [
            {"title": "Livres d'Informatique", "desc": "Sélectionnez le titre et l'auteur de tous les livres de la catégorie 'Informatique'.", "expected": "SELECT title, author FROM books WHERE category = 'Informatique';"},
            {"title": "Livres Anciens", "desc": "Comptez le nombre de livres publiés avant 2000. Nommez la colonne 'count_old_books'.", "expected": "SELECT COUNT(id) AS count_old_books FROM books WHERE publish_year < 2000;"},
        ],
        "Intermédiaire": [
            {"title": "Emprunts Actifs", "desc": "Affichez le nom du membre et le titre du livre qu'il a actuellement en prêt (return_date est NULL). Triez par nom du membre.", "expected": "SELECT m.name, b.title FROM members m JOIN loans l ON m.id = l.member_id JOIN books b ON l.book_id = b.id WHERE l.return_date IS NULL ORDER BY m.name;"},
            {"title": "Activité des Membres", "desc": "Comptez le nombre total de prêts (terminés ou non) par membre. Affichez le nom du membre et le compte. Triez par le nombre de prêts décroissant.", "expected": "SELECT m.name, COUNT(l.id) AS total_loans FROM members m JOIN loans l ON m.id = l.member_id GROUP BY m.name ORDER BY total_loans DESC;"},
        ],
        "Avancé": [
            {"title": "Livres Jamais Empruntés", "desc": "Trouvez le titre des livres qui n'ont jamais été empruntés. Triez par titre.", "expected": "SELECT title FROM books WHERE id NOT IN (SELECT DISTINCT book_id FROM loans) ORDER BY title;"},
            {"title": "Membres les Plus Actifs", "desc": "Trouvez le nom du membre ayant le plus grand nombre de prêts actifs (return_date est NULL).", "expected": "SELECT m.name, COUNT(l.id) as active_loans FROM members m JOIN loans l ON m.id = l.member_id WHERE l.return_date IS NULL GROUP BY m.name ORDER BY active_loans DESC LIMIT 1;"},
        ]
    }
}


# --- 4. Fonctions Utilitaires de Base de Données ---

@st.cache_resource
def create_connection():
    """
    Crée une connexion persistante à une base de données SQLite en mémoire.
    AJOUT: check_same_thread=False pour résoudre les problèmes de multi-threading de Streamlit.
    """
    try:
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        # Activer les clés étrangères pour SQLite
        conn.execute("PRAGMA foreign_keys = ON;") 
        return conn
    except Error as e:
        st.error(f"Erreur de connexion SQLite: {e}")
        return None

def init_database(conn, db_type):
    """Initialise le schéma et charge les données pour le type de base de données spécifié."""
    cursor = conn.cursor()
    schema_data = SCHEMAS[db_type]
    
    # Supprimer toutes les tables précédentes
    for table_name in schema_data["tables"].keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

    # Créer les nouvelles tables et insérer les données
    for table_name, data in schema_data["tables"].items():
        # Création de la table
        cursor.execute(f"CREATE TABLE {table_name} ({data['ddl']});")
        
        # Insertion des données (plus robuste)
        placeholders = ', '.join(['?'] * len(data['columns']))
        insert_query = f"INSERT INTO {table_name} ({', '.join(data['columns'])}) VALUES ({placeholders});"
        cursor.executemany(insert_query, data['data'])
        
    conn.commit()


def compare_query_results(user_query, expected_query, conn):
    """Exécute et compare les DataFrames résultants de la requête utilisateur et de la requête attendue."""
    
    def fetch_data(query):
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(data, columns=columns)

    try:
        user_df = fetch_data(user_query)
        expected_df = fetch_data(expected_query)
    except Exception as e:
        return False, None, f"Erreur d'exécution de la requête : {e}"

    # 1. Vérification de la structure (Colonnes et Nombre de lignes)
    if not user_df.columns.tolist() == expected_df.columns.tolist():
        # Tentative de normalisation des noms de colonnes (casse)
        user_cols_lower = [c.lower() for c in user_df.columns]
        expected_cols_lower = [c.lower() for c in expected_df.columns]
        
        if not user_cols_lower == expected_cols_lower:
            return False, user_df, "Les noms ou l'ordre des colonnes ne correspondent pas."

    if len(user_df) != len(expected_df):
        return False, user_df, f"Nombre de lignes incorrect. Attendu: {len(expected_df)}, Obtenu: {len(user_df)}."

    # 2. Normalisation et Comparaison des valeurs
    if user_df.empty and expected_df.empty:
        return True, user_df, "Solution Correcte (résultat vide)."
        
    try:
        # Assurer que les types sont cohérents pour la comparaison
        user_df = user_df.astype(expected_df.dtypes)
        
        # Normaliser l'ordre des lignes en triant les deux DataFrames par toutes les colonnes
        sort_cols = user_df.columns.tolist()
        user_df_sorted = user_df.sort_values(by=sort_cols, ignore_index=True)
        expected_df_sorted = expected_df.sort_values(by=sort_cols, ignore_index=True)
        
        # Comparaison finale
        if user_df_sorted.equals(expected_df_sorted):
            return True, user_df, "Solution Correcte."
        else:
            return False, user_df, "Les données retournées ne correspondent pas (vérifiez les valeurs, l'agrégation ou les alias)."
    except Exception as e:
        return False, user_df, f"Erreur lors de la normalisation/comparaison des résultats : {e}. Votre requête a pu s'exécuter mais le résultat est incorrect."


# --- 5. Fonctions de Vues Streamlit ---

def show_home():
    st.header("Bienvenue dans le SQL Sandbox! 🚀")
    
    st.markdown("""
    Ceci est l'application d'apprentissage SQL que j'aurais aimé avoir. Elle vous permet de pratiquer
    sur des bases de données réelles (en mémoire) sans vous soucier des erreurs.
    """)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Schémas Disponibles", value=len(SCHEMAS))
        st.markdown("🌐 Visualisez la structure de la BDD avec des diagrammes ER.")
    with col2:
        st.metric(label="Questions de Quiz", value=len(quiz_questions))
        st.markdown("🧠 Testez vos connaissances théoriques rapidement.")
    with col3:
        total_exercises = sum(len(e) for db in exercises.values() for e in db.values())
        st.metric(label="Exercices Pratiques", value=total_exercises)
        st.markdown("✍️ Écrivez du SQL, exécutez-le, et obtenez un feedback immédiat.")
        
    st.info("💡 **Conseil :** Commencez par l'onglet **Schémas de Base de Données** pour sélectionner le jeu de données actif (HR par défaut).")


def show_quiz():
    st.header("Quiz SQL : Testez vos Fondamentaux 🧠")

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {
            "score": 0,
            "current_index": 0,
            "questions": random.sample(quiz_questions, len(quiz_questions)),
            "submitted": False,
            "done": False,
        }

    state = st.session_state.quiz_state

    if state["done"]:
        score_percentage = (state["score"] / len(state["questions"])) * 100
        st.success(
            f"Quiz terminé! Votre score final est de **{state['score']}/{len(state['questions'])}** ({score_percentage:.0f}%)"
        )
        if score_percentage >= 80: st.balloons(); st.markdown("## Bravo! Vous maîtrisez le SQL! 🎉")
        elif score_percentage >= 60: st.markdown("## Bien joué! Continuez à pratiquer. 👍")
        else: st.markdown("## Continuez à apprendre! Lisez la documentation pour vous améliorer. 📚")

        if st.button("Recommencer le quiz"):
            st.session_state.quiz_state = {
                "score": 0, "current_index": 0,
                "questions": random.sample(quiz_questions, len(quiz_questions)),
                "submitted": False, "done": False,
            }
            st.rerun()
        return

    current_q = state["questions"][state["current_index"]]
    
    with st.container(border=True):
        st.subheader(f"Question {state['current_index'] + 1} sur {len(state['questions'])}")
        st.markdown(f"**{current_q['q']}**")

        form_key = f"quiz_form_{state['current_index']}"
        with st.form(key=form_key):
            user_answer = st.radio(
                "Sélectionnez votre réponse :",
                current_q["o"],
                key=f"q_radio_{state['current_index']}",
                disabled=state['submitted']
            )
            
            col_sub, col_next = st.columns(2)
            
            with col_sub:
                submit_button = st.form_submit_button("Soumettre la réponse", disabled=state['submitted'])

            if submit_button and not state['submitted']:
                state['submitted'] = True
                if user_answer == current_q["c"]:
                    state["score"] += 1
                    st.session_state.feedback = "Correct! ✅"
                else:
                    st.session_state.feedback = f"Incorrect! La bonne réponse était : **{current_q['c']}** ❌"
                st.rerun() # Rerun pour que le feedback s'affiche dans le conteneur principal

    if state['submitted']:
        st.success(st.session_state.feedback) if "Correct" in st.session_state.feedback else st.error(st.session_state.feedback)
        
        # Afficher le bouton Suivant/Terminer
        if state['current_index'] < len(state['questions']) - 1:
            if st.button("Question suivante >>"):
                state['current_index'] += 1
                state['submitted'] = False
                st.session_state.feedback = ""
                st.rerun()
        else:
            if st.button("Terminer le quiz"):
                state['done'] = True
                st.rerun()

def show_schemas(conn):
    st.header("Schémas de Base de Données 📊")

    st.write("Sélectionnez un schéma pour le visualiser et le charger dans le **SQL Sandbox**.")
    
    # Sélecteur de BDD pour toute l'application
    db_type = st.selectbox(
        "Sélectionnez le Schéma Actif:",
        list(SCHEMAS.keys()),
        format_func=lambda x: SCHEMAS[x]["title"],
        key="active_db_type",
        help="Ceci définit la base de données utilisée pour le Testeur de Requêtes et les Exercices Pratiques."
    )
    
    schema_data = SCHEMAS[db_type]
    
    if st.button(f"Charger/Réinitialiser le Schéma {schema_data['title']}"):
        init_database(conn, db_type)
        st.success(f"Le schéma **{schema_data['title']}** a été chargé dans la base de données en mémoire pour la pratique.")
    
    st.subheader(f"Diagramme Entité-Relation : {schema_data['title']}")
    
    try:
        st.graphviz_chart(schema_data["erd"])
    except Exception:
        # Fallback si graphviz n'est pas bien installé ou supporté dans l'environnement
        st.code(schema_data["erd"], language="mermaid")
        st.warning("Diagramme ER affiché en code Graphviz (Graphviz non disponible pour un rendu graphique).")

    st.subheader("Structure et Données")
    
    # Affichage des tables dans des onglets
    tabs = st.tabs(list(schema_data["tables"].keys()))
    
    for i, table_name in enumerate(schema_data["tables"].keys()):
        with tabs[i]:
            st.markdown(f"#### Table `{table_name}`")
            st.code(f"CREATE TABLE {table_name} ({schema_data['tables'][table_name]['ddl']});", language="sql")
            
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur lors de la récupération des données de la table {table_name}: {e}")
                
                

def show_query_tester(conn, db_type):
    st.header("Testeur de Requêtes SQL 💻")
    st.info(f"Base de données active : **{SCHEMAS[db_type]['title']}**.")

    col_schema, col_query = st.columns([1, 2.5])
    
    with col_schema:
        st.subheader("Schéma Rapide")
        # Afficher toutes les tables disponibles pour ce schéma
        schema_data = SCHEMAS[db_type]
        for table_name, data in schema_data["tables"].items():
            with st.expander(f"Table `{table_name}`"):
                st.caption("Premières lignes:")
                st.code(f"({data['ddl']})", language="sql")
                # Utiliser conn.cursor().execute() plutôt que read_sql_query pour la robustesse après des DML
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                cols = [desc[0] for desc in cursor.description]
                df_sample = pd.DataFrame(cursor.fetchall(), columns=cols)
                st.dataframe(df_sample, use_container_width=True)
    
    with col_query:
        st.subheader("Éditeur de Requêtes")
        
        default_query = f"SELECT * FROM {list(SCHEMAS[db_type]['tables'].keys())[0]} LIMIT 10;"
        
        query = st.text_area(
            "Entrez votre requête SQL (SELECT, INSERT, UPDATE, DELETE):", 
            height=200, 
            value=default_query,
            key="query_tester_input"
        )
        
        if st.button("🚀 Exécuter la Requête"):
            try:
                cursor = conn.cursor()
                
                # Exécuter la requête
                cursor.execute(query)
                
                if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                    conn.commit()
                    st.success(f"Requête DML exécutée avec succès! {cursor.rowcount} ligne(s) affectée(s). N'oubliez pas de vérifier les tables dans l'onglet Schémas.")
                else:
                    results = cursor.fetchall()
                    column_names = [description[0] for description in cursor.description]

                    df = pd.DataFrame(results, columns=column_names)

                    st.subheader("Résultats de la Requête")
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Requête réussie! {len(df)} ligne(s) retournée(s).")

            except Exception as e:
                st.error(f"Erreur d'exécution de la requête : {e}")
                
        # Historique (simple)
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        if query not in st.session_state.query_history and query.strip() not in ["", default_query.strip()]:
            st.session_state.query_history.insert(0, query)
            st.session_state.query_history = st.session_state.query_history[:5] # Limiter à 5

        with st.expander("Historique des 5 dernières requêtes"):
            if st.session_state.query_history:
                for i, hist_q in enumerate(st.session_state.query_history):
                    if st.button(f"Charger Historique {i+1}", key=f"hist_btn_{i}"):
                        st.session_state.query_tester_input = hist_q
                        st.rerun()
                    st.code(hist_q, language="sql")
            else:
                st.write("Aucune requête dans l'historique.")


def show_exercises(conn, db_type):
    st.header("Exercices Pratiques SQL 📝")

    st.markdown(f"**Schéma actif pour la pratique :** **{SCHEMAS[db_type]['title']}**. Les exercices ci-dessous sont adaptés à ce schéma.")
    
    if db_type not in exercises:
        st.warning(f"Aucun exercice spécifique n'est encore disponible pour le schéma **{SCHEMAS[db_type]['title']}**. Veuillez utiliser l'onglet 'Schémas' pour passer à HR ou Library.")
        return

    # Sélection du niveau de difficulté
    difficulty = st.selectbox(
        "Sélectionnez un niveau de difficulté:", list(exercises[db_type].keys())
    )

    # Sélection de l'exercice
    selected_exercises = exercises[db_type][difficulty]
    exercise_titles = [ex["title"] for ex in selected_exercises]
    selected_exercise_title = st.selectbox("Sélectionnez un exercice:", exercise_titles)

    # Trouver l'exercice sélectionné
    exercise = next(
        (ex for ex in selected_exercises if ex["title"] == selected_exercise_title), None
    )

    if exercise:
        with st.container(border=True):
            st.subheader(f"{exercise['title']} ({difficulty})")
            st.markdown(f"**Objectif :** {exercise['desc']}")

            # Affichage rapide du schéma
            with st.expander("Voir les tables et les données pour l'aide"):
                schema_data = SCHEMAS[db_type]
                for table_name, data in schema_data["tables"].items():
                    st.caption(f"Table `{table_name}`")
                    st.code(f"({data['ddl']})", language="sql")
                    # Utiliser conn.cursor().execute() plutôt que read_sql_query pour la robustesse après des DML
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    cols = [desc[0] for desc in cursor.description]
                    df_sample = pd.DataFrame(cursor.fetchall(), columns=cols)
                    st.dataframe(df_sample, use_container_width=True)

        # Zone de saisie pour la solution
        user_solution = st.text_area(f"Votre solution SQL pour '{exercise['title']}' :", height=120, key="exercise_solution_input")

        col_check, col_hint, col_sol = st.columns(3)
        
        solution_check_button = col_check.button("✅ Vérifier la Solution")

        if solution_check_button:
            if user_solution.strip():
                # Utiliser la fonction de comparaison améliorée
                is_correct, user_df, message = compare_query_results(
                    user_solution, exercise["expected"], conn
                )

                if is_correct:
                    st.success("Félicitations! Votre solution est **correcte**! 🎉")
                    st.balloons()
                else:
                    st.error(f"Solution Incorrecte. **{message}**")
                
                # Afficher le résultat de l'utilisateur pour comparaison
                if user_df is not None:
                    st.subheader("Votre Résultat:")
                    st.dataframe(user_df, use_container_width=True)

            else:
                st.warning("Veuillez saisir une solution avant de vérifier.")
        
        # Boutons d'aide
        if col_hint.button("💡 Indice (Requis!)"):
            # L'indice est souvent dans l'expected query elle-même, on peut l'analyser
            parts = exercise['expected'].split()
            hint = f"Pensez aux clauses: `{parts[0]}`, `{parts[1]}`."
            if 'JOIN' in exercise['expected']: hint += " N'oubliez pas la `JOIN`."
            if 'GROUP BY' in exercise['expected']: hint += " Avez-vous besoin de `GROUP BY` et d'une fonction d'agrégation ?"
            if 'WHERE' in exercise['expected']: hint += " Utilisez la clause `WHERE` pour filtrer les lignes."
            st.info(hint)

        if col_sol.button("👁️ Voir la Solution"):
            st.code(exercise["expected"], language="sql")


# --- 6. Fonction Principale et Routage ---

def main():
    # Initialisation de l'état de la BDD si non présent
    if "active_db_type" not in st.session_state:
        st.session_state["active_db_type"] = "HR"
        
    # La connexion à la BDD est stockée en cache et réutilisée
    conn = create_connection()

    if conn is None:
        st.stop() # Arrêter si la connexion échoue

    # Initialisation de la BDD avec le schéma actif
    init_database(conn, st.session_state["active_db_type"])

    # Barre latérale pour la navigation
    st.sidebar.title("Navigation 🧭")
    menu = st.sidebar.radio(
        "Choisissez une section:",
        [
            "Accueil",
            "Schémas de Base de Données",
            "Testeur de Requêtes",
            "Exercices Pratiques",
            "Quiz SQL",
        ],
    )

    # Affichage des sections
    if menu == "Accueil":
        show_home()
    elif menu == "Quiz SQL":
        show_quiz()
    elif menu == "Testeur de Requêtes":
        show_query_tester(conn, st.session_state["active_db_type"])
    elif menu == "Schémas de Base de Données":
        show_schemas(conn)
    elif menu == "Exercices Pratiques":
        show_exercises(conn, st.session_state["active_db_type"])


if __name__ == "__main__":
    main()
