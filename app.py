import random
import sqlite3
from sqlite3 import Error
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import time

# Configuration de la page
st.set_page_config(
    page_title="SQL Révision App",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Fonction pour créer une connexion à une base de données SQLite en mémoire
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        return conn
    except Error as e:
        st.error(f"Erreur de connexion SQLite: {e}")
    return conn

# Initialisation de la base de données avec des données d'exemple
def init_database(conn):
    cursor = conn.cursor()

    # Table des employés
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            department TEXT,
            salary REAL
        )
        """
    )

    # Table des départements
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manager_id INTEGER,
            budget REAL,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
        """
    )

    # Insertion de données d'exemple
    cursor.execute(
        """
        INSERT INTO employees (id, name, age, department, salary)
        VALUES
            (1, 'Jean Dupont', 35, 'IT', 55000),
            (2, 'Marie Lefebvre', 42, 'Marketing', 62000),
            (3, 'Pierre Martin', 28, 'IT', 48000),
            (4, 'Sophie Bernard', 31, 'RH', 51000),
            (5, 'Thomas Dubois', 45, 'Finance', 75000)
        """
    )

    cursor.execute(
        """
        INSERT INTO departments (id, name, manager_id, budget)
        VALUES
            (1, 'IT', 1, 500000),
            (2, 'Marketing', 2, 350000),
            (3, 'RH', 4, 200000),
            (4, 'Finance', 5, 750000)
        """
    )

    conn.commit()

# Questions pour le quiz SQL
quiz_questions = [
    {
        "question": "Quelle commande SQL est utilisée pour récupérer des données d'une table?",
        "options": ["SELECT", "UPDATE", "DELETE", "INSERT"],
        "correct": "SELECT",
        "explanation": "La commande `SELECT` est utilisée pour interroger et récupérer des données d'une ou plusieurs tables."
    },
    {
        "question": "Comment joindre deux tables en SQL?",
        "options": ["MERGE", "COMBINE", "JOIN", "CONNECT"],
        "correct": "JOIN",
        "explanation": "La clause `JOIN` permet de combiner les lignes de deux ou plusieurs tables en fonction d'une colonne commune."
    },
    {
        "question": "Quelle clause est utilisée pour filtrer les résultats d'une requête SQL?",
        "options": ["FILTER", "HAVING", "GROUP", "WHERE"],
        "correct": "WHERE",
        "explanation": "La clause `WHERE` permet de filtrer les résultats d'une requête en spécifiant une condition."
    },
    {
        "question": "Comment trier les résultats d'une requête SQL par ordre croissant?",
        "options": ["SORT BY", "ORDER BY ... ASC", "ORDER ASC", "ARRANGE BY"],
        "correct": "ORDER BY ... ASC",
        "explanation": "La clause `ORDER BY ... ASC` trie les résultats par ordre croissant. `ASC` est optionnel car c'est le comportement par défaut."
    },
    {
        "question": "Quelle fonction SQL est utilisée pour compter le nombre d'enregistrements?",
        "options": ["SUM()", "COUNT()", "TOTAL()", "NUM()"],
        "correct": "COUNT()",
        "explanation": "La fonction `COUNT()` retourne le nombre d'enregistrements dans une table ou une colonne."
    },
]

# Exercices par niveau de difficulté
exercises = {
    "Débutant": [
        {
            "title": "Sélection de base",
            "description": "Écrivez une requête pour sélectionner tous les employés du département IT.",
            "expected": "SELECT * FROM employees WHERE department = 'IT';",
            "hint": "Utilisez la clause WHERE pour filtrer les résultats.",
            "expected_columns": "id, name, age, department, salary",
        },
        {
            "title": "Calcul d'agrégation",
            "description": "Calculez le salaire moyen des employés.",
            "expected": "SELECT AVG(salary) as average_salary FROM employees;",
            "hint": "Utilisez la fonction AVG() pour calculer la moyenne.",
            "expected_columns": "average_salary",
        },
    ],
    "Intermédiaire": [
        {
            "title": "Jointure de tables",
            "description": "Affichez le nom de chaque employé avec le nom de son département et le budget du département.",
            "expected": "SELECT e.name as employee_name, d.name as department_name, d.budget FROM employees e JOIN departments d ON e.department = d.name;",
            "hint": "Utilisez JOIN pour combiner les données des deux tables.",
            "expected_columns": "employee_name, department_name, budget",
        },
        {
            "title": "Groupement et agrégation",
            "description": "Affichez le salaire moyen par département, triés du plus élevé au plus bas.",
            "expected": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;",
            "hint": "Utilisez GROUP BY pour regrouper les résultats et ORDER BY pour les trier.",
            "expected_columns": "department, avg_salary",
        },
    ],
    "Avancé": [
        {
            "title": "Sous-requêtes",
            "description": "Trouvez les employés qui gagnent plus que la moyenne des salaires de leur département.",
            "expected": "SELECT e1.name, e1.salary, e1.department FROM employees e1 WHERE e1.salary > (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e1.department);",
            "hint": "Utilisez une sous-requête pour calculer la moyenne par département.",
            "expected_columns": "name, salary, department",
        },
        {
            "title": "Fonctions de fenêtrage",
            "description": "Affichez chaque employé avec son classement de salaire dans son département (du plus élevé au plus bas).",
            "expected": "SELECT name, department, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank FROM employees;",
            "hint": "Utilisez les fonctions de fenêtrage (RANK, PARTITION BY) pour créer des classements.",
            "expected_columns": "name, department, salary, salary_rank",
        },
    ],
}

# Fonction pour afficher la page d'accueil
def show_home():
    st.header("Bienvenue dans l'application de révision SQL! 🎓")
    st.write(
        """
        Cette application est conçue pour vous aider à réviser et à pratiquer vos compétences en SQL.

        ### Fonctionnalités disponibles:
        - **📝 Quiz SQL**: Testez vos connaissances en SQL avec des questions à choix multiples.
        - **🔍 Testeur de Requêtes**: Écrivez et exécutez des requêtes SQL sur des bases de données d'exemple.
        - **🗺️ Schémas de Base de Données**: Explorez les structures de base de données disponibles.
        - **💪 Exercices Pratiques**: Résolvez des problèmes SQL pratiques et vérifiez vos solutions.
        - **📚 Tutoriels**: Apprenez les concepts SQL pas à pas.

        Utilisez la barre latérale pour naviguer entre les différentes sections.
        """
    )
    st.info(
        "💡 **Conseil**: SQL (Structured Query Language) est un langage standard pour la gestion des bases de données relationnelles. Pratiquez régulièrement pour maîtriser ses concepts!"
    )

# Fonction pour afficher le quiz SQL
def show_quiz():
    st.header("Quiz SQL 🧠")
    st.write("Testez vos connaissances SQL avec ce quiz à choix multiples!")

    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.questions_answered = 0
        st.session_state.current_question = 0
        st.session_state.questions = random.sample(quiz_questions, len(quiz_questions))
        st.session_state.submitted = False
        st.session_state.start_time = time.time()

    # Barre de progression
    progress = st.session_state.questions_answered / len(st.session_state.questions)
    st.progress(progress)

    if st.session_state.questions_answered < len(st.session_state.questions):
        current_q = st.session_state.questions[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1} sur {len(st.session_state.questions)}")
        st.write(current_q["question"])

        user_answer = st.radio(
            "Sélectionnez votre réponse:",
            current_q["options"],
            key=f"q_{st.session_state.current_question}",
        )

        if st.session_state.submitted:
            if st.session_state.current_question < len(st.session_state.questions) - 1:
                if st.button("Question suivante"):
                    st.session_state.current_question += 1
                    st.session_state.submitted = False
                    st.rerun()
        else:
            if st.button("Soumettre"):
                st.session_state.submitted = True
                if user_answer == current_q["correct"]:
                    st.session_state.quiz_score += 1
                    st.success(f"Correct! ✅\n\n**Explication**: {current_q['explanation']}")
                else:
                    st.error(f"Incorrect! ❌\n\n**Explication**: {current_q['explanation']}\n\nLa bonne réponse est: **{current_q['correct']}**")

                st.session_state.questions_answered += 1
                if st.session_state.questions_answered < len(st.session_state.questions):
                    st.rerun()
    else:
        elapsed_time = time.time() - st.session_state.start_time
        st.success(f"Quiz terminé en {elapsed_time:.2f} secondes! 🎉\n\nVotre score est de {st.session_state.quiz_score}/{len(st.session_state.questions)}")

        # Afficher une évaluation basée sur le score
        score_percentage = (st.session_state.quiz_score / len(st.session_state.questions)) * 100
        if score_percentage >= 80:
            st.balloons()
            st.write("🎉 **Excellent travail!** Vos connaissances SQL sont solides!")
        elif score_percentage >= 60:
            st.write("👍 **Bon travail!** Continuez à pratiquer pour améliorer vos compétences SQL.")
        else:
            st.write("📚 **Continuez à apprendre et à pratiquer.** Les bases de données SQL demandent de la pratique!")

    if st.button("Recommencer le quiz"):
        st.session_state.quiz_score = 0
        st.session_state.questions_answered = 0
        st.session_state.current_question = 0
        st.session_state.questions = random.sample(quiz_questions, len(quiz_questions))
        st.session_state.submitted = False
        st.rerun()

# Fonction pour afficher le testeur de requêtes
@st.cache_data
def load_data(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    return pd.DataFrame(results, columns=column_names)

def show_query_tester(conn):
    st.header("Testeur de Requêtes SQL 🔍")
    st.write(
        """
        Écrivez vos requêtes SQL et exécutez-les sur notre base de données d'exemple.
        La base de données contient les tables **'employees'** et **'departments'**.
        """
    )

    # Afficher le schéma de la base de données
    with st.expander("📋 Voir le schéma de la base de données"):
        st.code(
            """
            -- Table 'employees'
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                department TEXT,
                salary REAL
            );

            -- Table 'departments'
            CREATE TABLE departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                manager_id INTEGER,
                budget REAL,
                FOREIGN KEY (manager_id) REFERENCES employees (id)
            );
            """
        )

    # Zone de saisie pour la requête SQL
    query = st.text_area(
        "Écrivez votre requête SQL ici:",
        height=150,
        value="SELECT * FROM employees;"
    )

    # Exécution de la requête
    if st.button("Exécuter la requête"):
        try:
            df = load_data(conn, query)
            st.subheader("📊 Résultats:")
            st.dataframe(df)

            # Visualisation des données
            if "salary" in df.columns:
                st.subheader("📈 Visualisation des salaires")
                fig = px.bar(df, x="name", y="salary", title="Salaire par employé")
                st.plotly_chart(fig)

            st.info(f"✅ La requête a retourné {len(df)} enregistrement(s).")

            # Historique des requêtes
            if "query_history" not in st.session_state:
                st.session_state.query_history = []
            st.session_state.query_history.append(query)

            # Afficher l'historique
            with st.expander("🕰️ Historique des requêtes"):
                for i, q in enumerate(st.session_state.query_history):
                    st.code(q)

        except Exception as e:
            st.error(f"❌ Erreur d'exécution de la requête: {e}")

    # Exemples de requêtes
    with st.expander("💡 Exemples de requêtes"):
        st.code("SELECT * FROM employees WHERE department = 'IT';")
        st.code("SELECT e.name, d.name as department_name FROM employees e JOIN departments d ON e.department = d.name;")
        st.code("SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;")

# Fonction pour afficher les schémas de base de données
def show_schemas(conn):
    st.header("Schémas de Base de Données 🗺️")
    st.write(
        """
        Explorez les schémas de base de données disponibles pour comprendre la structure des données.
        """
    )

    # Sélection du schéma à afficher
    schema_type = st.selectbox(
        "Sélectionnez un schéma:",
        ["Employés & Départements", "Commerce en ligne", "Bibliothèque"],
    )

    if schema_type == "Employés & Départements":
        st.subheader("Schéma Employés & Départements")

        # Description du schéma
        st.write(
            """
            Ce schéma représente une structure simple pour la gestion des employés et des départements d'une entreprise.
            """
        )

        # Afficher le schéma sous forme de diagramme
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Table `employees`**")
            st.code(
                """
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    department TEXT,
                    salary REAL
                );
                """
            )
            # Afficher les données d'exemple
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees")
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            df_employees = pd.DataFrame(results, columns=column_names)
            st.dataframe(df_employees)

        with col2:
            st.markdown("**Table `departments`**")
            st.code(
                """
                CREATE TABLE departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    manager_id INTEGER,
                    budget REAL,
                    FOREIGN KEY (manager_id) REFERENCES employees (id)
                );
                """
            )
            # Afficher les données d'exemple
            cursor.execute("SELECT * FROM departments")
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            df_departments = pd.DataFrame(results, columns=column_names)
            st.dataframe(df_departments)

    elif schema_type == "Commerce en ligne":
        st.subheader("Schéma Commerce en ligne")
        st.write(
            """
            Ce schéma représente une structure typique pour une application de commerce en ligne.
            *(Les données ne sont pas chargées dans la base de données actuelle, ceci est juste un exemple conceptuel.)*
            """
        )
        st.code(
            """
            +---------------+      +---------------+      +----------------+
            | customers     |      | orders        |      | products       |
            +---------------+      +---------------+      +----------------+
            | id (PK)       |      | id (PK)       |      | id (PK)        |
            | name          |      | customer_id (FK)     | name           |
            | email         |      | order_date    |      | description    |
            | address       |      | total_amount  |      | price          |
            | phone         |      | status        |      | category       |
            +---------------+      +---------------+      +----------------+
                     |                      |                       |
                     |                      |                       |
                     +----------------------+-----------------------+
                                            |
                                    +----------------+
                                    | order_items     |
                                    +----------------+
                                    | order_id (FK)   |
                                    | product_id (FK)|
                                    | quantity       |
                                    | unit_price     |
                                    +----------------+
            """
        )

    elif schema_type == "Bibliothèque":
        st.subheader("Schéma Bibliothèque")
        st.write(
            """
            Ce schéma représente une structure pour la gestion d'une bibliothèque.
            *(Les données ne sont pas chargées dans la base de données actuelle, ceci est juste un exemple conceptuel.)*
            """
        )
        st.code(
            """
            +---------------+      +----------------+      +---------------+
            | books         |      | loans          |      | members       |
            +---------------+      +----------------+      +---------------+
            | id (PK)       |      | id (PK)        |      | id (PK)       |
            | title         |      | book_id (FK)   |      | name          |
            | author        |      | member_id (FK) |      | email         |
            | isbn          |      | loan_date      |      | address       |
            | category      |      | return_date    |      | join_date     |
            | publish_year  |      | returned       |      | status        |
            +---------------+      +----------------+      +---------------+
            """
        )

# Fonction pour afficher les exercices pratiques
def show_exercises(conn):
    st.header("Exercices Pratiques SQL 💪")
    st.write(
        """
        Pratiquez vos compétences SQL en résolvant des exercices de difficulté variée.
        Chaque exercice comprend une description du problème et une zone pour écrire votre solution.
        """
    )

    # Sélection du niveau de difficulté
    difficulty = st.selectbox(
        "Sélectionnez un niveau de difficulté:", ["Débutant", "Intermédiaire", "Avancé"]
    )

    # Sélection de l'exercice
    selected_exercises = exercises[difficulty]
    exercise_titles = [ex["title"] for ex in selected_exercises]
    selected_exercise_title = st.selectbox("Sélectionnez un exercice:", exercise_titles)

    # Trouver l'exercice sélectionné
    exercise = next(
        (ex for ex in selected_exercises if ex["title"] == selected_exercise_title),
        None,
    )

    if exercise:
        st.subheader(exercise["title"])
        st.write(exercise["description"])

        # Afficher les colonnes attendues
        st.info(f"📌 Colonnes attendues dans le résultat: **{exercise['expected_columns']}**")

        # Afficher les schémas des tables côte à côte
        st.subheader("🗺️ Schémas des tables :")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Table `employees`**")
            st.code(
                """
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    department TEXT,
                    salary REAL
                );
                """
            )
        with col2:
            st.markdown("**Table `departments`**")
            st.code(
                """
                CREATE TABLE departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    manager_id INTEGER,
                    budget REAL,
                    FOREIGN KEY (manager_id) REFERENCES employees (id)
                );
                """
            )

        # Zone de saisie pour la solution
        user_solution = st.text_area("Votre solution SQL:", height=100)

        # Vérification de la solution
        if st.button("Vérifier la solution"):
            if user_solution.strip():
                try:
                    # Exécuter la requête de l'utilisateur
                    cursor = conn.cursor()
                    cursor.execute(user_solution)
                    user_results = cursor.fetchall()
                    user_column_names = [description[0] for description in cursor.description]

                    # Exécuter la requête attendue
                    cursor.execute(exercise["expected"])
                    expected_results = cursor.fetchall()
                    expected_column_names = [description[0] for description in cursor.description]

                    # Afficher les résultats de l'utilisateur
                    st.subheader("📊 Votre résultat:")
                    user_df = pd.DataFrame(user_results, columns=user_column_names)
                    st.dataframe(user_df)

                    # Vérifier si les résultats correspondent
                    results_match = (
                        user_results == expected_results
                        and user_column_names == expected_column_names
                    )

                    if results_match:
                        st.success("🎉 **Félicitations!** Votre solution est correcte!")
                    else:
                        st.warning(
                            "⚠️ Votre solution ne correspond pas exactement au résultat attendu. Continuez d'essayer!"
                        )

                    # Afficher un indice
                    if st.button("💡 Afficher un indice"):
                        st.info(f"**Indice**: {exercise['hint']}")

                    # Option pour voir la solution
                    if st.button("🔍 Voir la solution"):
                        st.code(exercise["expected"])

                except Exception as e:
                    st.error(f"❌ Erreur d'exécution de la requête: {e}")
            else:
                st.warning("⚠️ Veuillez saisir une solution avant de vérifier.")

# Fonction pour afficher les tutoriels
def show_tutorials():
    st.header("Tutoriels SQL 📚")
    st.write(
        """
        Apprenez les concepts SQL pas à pas avec ces tutoriels interactifs.
        """
    )

    # Sélection du tutoriel
    tutorial_topics = [
        "Introduction à SQL",
        "Les commandes SELECT et WHERE",
        "Les jointures (JOIN)",
        "Les fonctions d'agrégation (GROUP BY, HAVING)",
        "Les sous-requêtes",
        "Les fonctions de fenêtrage"
    ]
    selected_topic = st.selectbox("Sélectionnez un tutoriel:", tutorial_topics)

    if selected_topic == "Introduction à SQL":
        st.subheader("Introduction à SQL")
        st.write(
            """
            SQL (Structured Query Language) est un langage standard pour la gestion des bases de données relationnelles.
            Il permet de créer, modifier et interroger des bases de données.

            ### Concepts clés:
            - **Tables**: Les données sont stockées dans des tables composées de lignes et de colonnes.
            - **Requêtes**: Les commandes SQL permettent d'interroger et de manipuler les données.
            - **Clés primaires et étrangères**: Elles permettent de lier les tables entre elles.
            """
        )

    elif selected_topic == "Les commandes SELECT et WHERE":
        st.subheader("Les commandes SELECT et WHERE")
        st.write(
            """
            La commande `SELECT` est utilisée pour récupérer des données d'une table.
            La clause `WHERE` permet de filtrer les résultats en fonction d'une condition.

            ### Exemple:
            ```sql
            SELECT name, salary FROM employees WHERE department = 'IT';
            ```
            Cette requête sélectionne le nom et le salaire des employés du département IT.
            """
        )

    elif selected_topic == "Les jointures (JOIN)":
        st.subheader("Les jointures (JOIN)")
        st.write(
            """
            Les jointures permettent de combiner les données de deux ou plusieurs tables.
            Il existe plusieurs types de jointures: `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, etc.

            ### Exemple:
            ```sql
            SELECT e.name, d.name as department_name
            FROM employees e
            JOIN departments d ON e.department = d.name;
            ```
            Cette requête affiche le nom des employés avec le nom de leur département.
            """
        )

    elif selected_topic == "Les fonctions d'agrégation (GROUP BY, HAVING)":
        st.subheader("Les fonctions d'agrégation (GROUP BY, HAVING)")
        st.write(
            """
            Les fonctions d'agrégation (`COUNT`, `SUM`, `AVG`, etc.) permettent de calculer des statistiques sur les données.
            La clause `GROUP BY` permet de regrouper les résultats par une ou plusieurs colonnes.
            La clause `HAVING` permet de filtrer les résultats après agrégation.

            ### Exemple:
            ```sql
            SELECT department, AVG(salary) as avg_salary
            FROM employees
            GROUP BY department
            HAVING AVG(salary) > 50000;
            ```
            Cette requête calcule le salaire moyen par département et filtre les départements où le salaire moyen est supérieur à 50000.
            """
        )

    elif selected_topic == "Les sous-requêtes":
        st.subheader("Les sous-requêtes")
        st.write(
            """
            Une sous-requête est une requête imbriquée dans une autre requête.
            Elle permet d'effectuer des calculs intermédiaires ou de filtrer des données en fonction de résultats de requêtes.

            ### Exemple:
            ```sql
            SELECT name, salary
            FROM employees
            WHERE salary > (SELECT AVG(salary) FROM employees);
            ```
            Cette requête sélectionne les employés dont le salaire est supérieur à la moyenne des salaires.
            """
        )

    elif selected_topic == "Les fonctions de fenêtrage":
        st.subheader("Les fonctions de fenêtrage")
        st.write(
            """
            Les fonctions de fenêtrage (`RANK`, `ROW_NUMBER`, `DENSE_RANK`, etc.) permettent d'effectuer des calculs sur des ensembles de lignes liés à la ligne courante.
            Elles sont utiles pour créer des classements ou des calculs cumulatifs.

            ### Exemple:
            ```sql
            SELECT name, department, salary,
                   RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
            FROM employees;
            ```
            Cette requête affiche chaque employé avec son classement de salaire dans son département.
            """
        )

# Fonction principale
def main():
    st.title("Application de Révision SQL")

    # Barre latérale pour la navigation
    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Accueil",
            "Quiz SQL",
            "Testeur de Requêtes",
            "Schémas de Base de Données",
            "Exercices Pratiques",
            "Tutoriels SQL"
        ],
    )

    # Connexion à la base de données
    conn = create_connection()

    if conn is not None:
        init_database(conn)

        if menu == "Accueil":
            show_home()
        elif menu == "Quiz SQL":
            show_quiz()
        elif menu == "Testeur de Requêtes":
            show_query_tester(conn)
        elif menu == "Schémas de Base de Données":
            show_schemas(conn)
        elif menu == "Exercices Pratiques":
            show_exercises(conn)
        elif menu == "Tutoriels SQL":
            show_tutorials()

        conn.close()
    else:
        st.error("Erreur lors de la connexion à la base de données.")

if __name__ == "__main__":
    main()
