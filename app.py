import random
import sqlite3
from sqlite3 import Error

import pandas as pd
import streamlit as st

# --- Configuration de la page ---
st.set_page_config(page_title="SQL Révision App", layout="wide")

# --- Fonctions de Base de Données ---

def create_connection():
    """Crée une connexion à une base de données SQLite en mémoire."""
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        return conn
    except Error as e:
        st.error(f"Erreur de connexion SQLite: {e}")
    return conn

def init_database(conn, db_type="employees"):
    """Initialisation de la base de données selon le type sélectionné."""
    cursor = conn.cursor()
    
    # Suppression des tables existantes pour s'assurer d'un état propre
    cursor.execute("DROP TABLE IF EXISTS employees;")
    cursor.execute("DROP TABLE IF EXISTS departments;")
    cursor.execute("DROP TABLE IF EXISTS books;")
    cursor.execute("DROP TABLE IF EXISTS members;")
    cursor.execute("DROP TABLE IF EXISTS loans;")

    if db_type == "employees":
        # Table des employés
        employees_data = [
            (1, 'Jean Dupont', 35, 'IT', 55000),
            (2, 'Marie Lefebvre', 42, 'Marketing', 62000),
            (3, 'Pierre Martin', 28, 'IT', 48000),
            (4, 'Sophie Bernard', 31, 'RH', 51000),
            (5, 'Thomas Dubois', 45, 'Finance', 75000),
            (6, 'Lucie Moreau', 29, 'Marketing', 59000),
            (7, 'David Petit', 50, 'Finance', 80000),
            (8, 'Laura Simon', 33, 'IT', 55000)
        ]
        
        # Utilisation de Pandas pour une insertion plus propre
        df_employees = pd.DataFrame(employees_data, columns=['id', 'name', 'age', 'department', 'salary'])
        df_employees.to_sql('employees', conn, if_exists='replace', index=False)

        # Table des départements
        departments_data = [
            (1, 'IT', 1, 500000),
            (2, 'Marketing', 2, 350000),
            (3, 'RH', 4, 200000),
            (4, 'Finance', 5, 750000)
        ]
        df_departments = pd.DataFrame(departments_data, columns=['id', 'name', 'manager_id', 'budget'])
        df_departments.to_sql('departments', conn, if_exists='replace', index=False)
        
        # Recréer la clé étrangère pour des raisons de référence (SQLite en mémoire ne force pas les FK par défaut)
        # Mais pour la simplicité, on se contente des données chargées.
        
    elif db_type == "library":
        # Schéma Bibliothèque (exemple pour les exercices)
        df_books = pd.DataFrame({
            'id': [101, 102, 103, 104],
            'title': ['Data Science 101', 'SQL Mastery', 'Python Basics', 'Deep Learning'],
            'author': ['A. Smith', 'B. Jones', 'C. Hall', 'D. King'],
            'category': ['Science', 'Informatique', 'Informatique', 'Science']
        })
        df_members = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alex Durand', 'Emma Leroy', 'Marc Riviere']
        })
        df_loans = pd.DataFrame({
            'id': [1, 2, 3],
            'book_id': [101, 103, 102],
            'member_id': [1, 2, 1],
            'loan_date': ['2023-01-01', '2023-01-05', '2023-01-10'],
            'return_date': ['2023-01-15', '2023-01-20', None]
        })
        
        df_books.to_sql('books', conn, if_exists='replace', index=False)
        df_members.to_sql('members', conn, if_exists='replace', index=False)
        df_loans.to_sql('loans', conn, if_exists='replace', index=False)
        
    conn.commit()


# --- Questions et Exercices ---

quiz_questions = [
    {
        "question": "Quelle commande SQL est utilisée pour récupérer des données d'une table?",
        "options": ["SELECT", "UPDATE", "DELETE", "INSERT"],
        "correct": "SELECT",
    },
    {
        "question": "Comment joindre deux tables en SQL?",
        "options": ["MERGE", "COMBINE", "JOIN", "CONNECT"],
        "correct": "JOIN",
    },
    {
        "question": "Quelle clause est utilisée pour filtrer les résultats d'une requête SQL?",
        "options": ["FILTER", "HAVING", "GROUP", "WHERE"],
        "correct": "WHERE",
    },
    {
        "question": "Comment trier les résultats d'une requête SQL par ordre croissant?",
        "options": ["SORT BY", "ORDER BY ... ASC", "ORDER ASC", "ARRANGE BY"],
        "correct": "ORDER BY ... ASC",
    },
    {
        "question": "Quelle fonction SQL est utilisée pour compter le nombre d'enregistrements?",
        "options": ["SUM()", "COUNT()", "TOTAL()", "NUM()"],
        "correct": "COUNT()",
    },
    {
        "question": "Quel opérateur est utilisé pour comparer des valeurs partielles (pattern matching)?",
        "options": ["MATCH", "LIKE", "CONTAINS", "PATTERN"],
        "correct": "LIKE",
    },
    {
        "question": "Quelle contrainte garantit que toutes les valeurs dans une colonne sont différentes?",
        "options": ["NOT NULL", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE"],
        "correct": "UNIQUE",
    },
]

# Exercices par niveau de difficulté (ajustement de la requête attendue pour plus de robustesse)
exercises = {
    "Débutant": [
        {
            "title": "Sélection de base",
            "description": "Écrivez une requête pour sélectionner tous les employés du département **IT**.",
            "expected": "SELECT id, name, age, department, salary FROM employees WHERE department = 'IT' ORDER BY id;", # Ajout ORDER BY
            "hint": "Utilisez la clause WHERE pour filtrer les résultats. N'oubliez pas le *.",
            "expected_columns": "id, name, age, department, salary",
        },
        {
            "title": "Calcul d'agrégation",
            "description": "Calculez le salaire moyen des employés, en nommant la colonne **average_salary**.",
            "expected": "SELECT AVG(salary) as average_salary FROM employees;",
            "hint": "Utilisez la fonction AVG() et l'alias 'AS'.",
            "expected_columns": "average_salary",
        },
    ],
    "Intermédiaire": [
        {
            "title": "Jointure de tables",
            "description": "Affichez le nom de chaque employé avec le nom de son département et le budget du département. Triez par nom d'employé.",
            "expected": "SELECT e.name as employee_name, d.name as department_name, d.budget FROM employees e JOIN departments d ON e.department = d.name ORDER BY employee_name;",
            "hint": "Utilisez JOIN pour combiner les données des deux tables sur la colonne de département.",
            "expected_columns": "employee_name, department_name, budget",
        },
        {
            "title": "Groupement et agrégation",
            "description": "Affichez le salaire moyen par département, triés du plus élevé au plus bas. Nommez la colonne 'avg_salary'.",
            "expected": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;",
            "hint": "Utilisez GROUP BY pour regrouper les résultats et ORDER BY DESC pour les trier.",
            "expected_columns": "department, avg_salary",
        },
    ],
    "Avancé": [
        {
            "title": "Sous-requêtes",
            "description": "Trouvez les noms et salaires des employés qui gagnent plus que la moyenne des salaires de **tous** les employés.",
            "expected": "SELECT name, salary FROM employees WHERE salary > (SELECT AVG(salary) FROM employees) ORDER BY salary DESC;",
            "hint": "Utilisez une sous-requête dans la clause WHERE.",
            "expected_columns": "name, salary",
        },
        {
            "title": "Fonctions de fenêtrage",
            "description": "Affichez chaque employé avec son classement de salaire dans son département (du plus élevé au plus bas). Nommez la colonne 'salary_rank'.",
            "expected": "SELECT name, department, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank FROM employees ORDER BY department, salary_rank;",
            "hint": "Utilisez les fonctions de fenêtrage (RANK() OVER...).",
            "expected_columns": "name, department, salary, salary_rank",
        },
    ],
}

# --- Fonctions de Vérification (Amélioration majeure) ---

def compare_query_results(user_query, expected_query, conn):
    """
    Exécute et compare les DataFrames résultants de la requête utilisateur et de la requête attendue.
    Normalise les résultats avant la comparaison.
    """
    
    # 1. Exécution des requêtes
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
        return False, None, f"Erreur d'exécution: {e}"

    # 2. Vérification de la structure (Colonnes et Nombre de lignes)
    if not user_df.columns.tolist() == expected_df.columns.tolist():
        return False, user_df, "Les noms ou l'ordre des colonnes ne correspondent pas."

    if len(user_df) != len(expected_df):
        return False, user_df, "Le nombre de lignes retournées est incorrect."

    # 3. Normalisation et Comparaison des valeurs (plus robuste)
    # Tenter de trier par toutes les colonnes pour une comparaison ligne par ligne
    sort_cols = user_df.columns.tolist()
    
    # Assurer que les types sont cohérents pour la comparaison (utile pour les entiers vs floats, etc.)
    user_df = user_df.astype(expected_df.dtypes) 
    
    # Normaliser l'ordre des lignes en triant les deux DataFrames
    user_df_sorted = user_df.sort_values(by=sort_cols, ignore_index=True)
    expected_df_sorted = expected_df.sort_values(by=sort_cols, ignore_index=True)
    
    # Comparaison des DataFrames
    if user_df_sorted.equals(expected_df_sorted):
        return True, user_df, "Solution Correcte."
    else:
        return False, user_df, "Les données retournées ne correspondent pas (vérifiez les valeurs ou l'ordre des colonnes)."


# --- Fonctions de Vues Streamlit ---

def show_home():
    st.header("Bienvenue dans l'application de révision SQL!")

    st.write(
        """
    Cette application est conçue pour vous aider à réviser et à pratiquer vos compétences en SQL.
    Elle utilise une base de données **SQLite en mémoire** pour garantir que vos modifications sont réinitialisées à chaque session.

    ### Fonctionnalités disponibles:

    - **Quiz SQL**: Testez vos connaissances en SQL avec des questions à choix multiples.
    - **Testeur de Requêtes**: Écrivez et exécutez librement des requêtes SQL sur des bases de données d'exemple.
    - **Schémas de Base de Données**: Explorez les structures de données avec des exemples visuels et des données réelles.
    - **Exercices Pratiques**: Résolvez des problèmes SQL pratiques et vérifiez vos solutions grâce à une comparaison de résultats robuste.

    Utilisez la barre latérale pour naviguer entre les différentes sections.
    """
    )
    st.info(
        "💡 Conseil: Nous avons deux schémas de base de données d'exemple : **Employés/Départements** et **Bibliothèque**."
    )
    

def show_quiz():
    st.header("Quiz SQL")

    st.write("Testez vos connaissances SQL avec ce quiz à choix multiples!")

    # Initialisation de l'état
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.current_question = 0
        st.session_state.questions = random.sample(quiz_questions, len(quiz_questions))
        st.session_state.quiz_submitted = False
        st.session_state.quiz_done = False

    if st.session_state.quiz_done:
        st.success(
            f"Quiz terminé! Votre score est de **{st.session_state.quiz_score}/{len(st.session_state.questions)}**"
        )
        
        # Afficher une évaluation basée sur le score
        score_percentage = (
            st.session_state.quiz_score / len(st.session_state.questions) * 100
        )
        if score_percentage >= 80:
            st.balloons()
            st.write("Excellent travail! 🎉 Vos connaissances SQL sont solides!")
        elif score_percentage >= 60:
            st.write(
                "Bon travail! Continuez à pratiquer pour améliorer vos compétences SQL."
            )
        else:
            st.write(
                "Continuez à apprendre et à pratiquer. Les bases de données SQL demandent de la pratique!"
            )
            
        if st.button("Recommencer le quiz"):
            st.session_state.quiz_score = 0
            st.session_state.current_question = 0
            st.session_state.questions = random.sample(
                quiz_questions, len(quiz_questions)
            )
            st.session_state.quiz_submitted = False
            st.session_state.quiz_done = False
            st.rerun()

    else:
        current_q = st.session_state.questions[st.session_state.current_question]
        
        st.subheader(
            f"Question {st.session_state.current_question + 1} sur {len(st.session_state.questions)}"
        )
        st.write(f"**{current_q['question']}**")

        # Utiliser un formulaire pour gérer l'état de soumission sans reruns inutiles
        with st.form(key=f"quiz_form_{st.session_state.current_question}"):
            user_answer = st.radio(
                "Sélectionnez votre réponse:",
                current_q["options"],
                key=f"q_radio_{st.session_state.current_question}",
            )
            submitted = st.form_submit_button("Soumettre")
            
            if submitted and not st.session_state.quiz_submitted:
                st.session_state.quiz_submitted = True
                
                if user_answer == current_q["correct"]:
                    st.session_state.quiz_score += 1
                    st.success("Correct! ✅")
                else:
                    st.error(
                        f"Incorrect! La bonne réponse est: **{current_q['correct']}** ❌"
                    )

        if st.session_state.quiz_submitted:
            
            # Gestion du bouton "Suivant" ou "Terminer"
            if st.session_state.current_question < len(st.session_state.questions) - 1:
                if st.button("Question suivante"):
                    st.session_state.current_question += 1
                    st.session_state.quiz_submitted = False
                    st.rerun()
            else:
                # Dernière question
                if st.button("Terminer le quiz"):
                    st.session_state.quiz_done = True
                    st.rerun()


def show_query_tester(conn, db_type):
    st.header("Testeur de Requêtes SQL")
    
    # Afficher le schéma en cours d'utilisation
    st.info(f"Base de données actuelle : **{db_type.capitalize()}** (en mémoire).")

    st.write(
        """
    Écrivez vos requêtes SQL et exécutez-les sur notre base de données d'exemple.
    """
    )

    # Afficher le schéma de la base de données (version dynamique)
    with st.expander("Voir le schéma de la base de données et les données"):
        if db_type == "employees":
            st.subheader("Tables 'employees' et 'departments'")
            
            # Afficher le code DDL pour référence
            st.code(
                """
            CREATE TABLE employees (id INTEGER, name TEXT, age INTEGER, department TEXT, salary REAL);
            CREATE TABLE departments (id INTEGER, name TEXT, manager_id INTEGER, budget REAL);
            """
            )
            
            # Afficher les données
            tab1, tab2 = st.tabs(["Table 'employees'", "Table 'departments'"])
            with tab1:
                df_employees = pd.read_sql_query("SELECT * FROM employees", conn)
                st.dataframe(df_employees)
            with tab2:
                df_departments = pd.read_sql_query("SELECT * FROM departments", conn)
                st.dataframe(df_departments)
                
        elif db_type == "library":
            st.subheader("Tables 'books', 'members', et 'loans'")
            st.code(
                """
            CREATE TABLE books (id INTEGER, title TEXT, author TEXT, category TEXT);
            CREATE TABLE members (id INTEGER, name TEXT, email TEXT);
            CREATE TABLE loans (id INTEGER, book_id INTEGER, member_id INTEGER, loan_date TEXT, return_date TEXT);
            """
            )
            tab1, tab2, tab3 = st.tabs(["Table 'books'", "Table 'members'", "Table 'loans'"])
            with tab1:
                st.dataframe(pd.read_sql_query("SELECT * FROM books", conn))
            with tab2:
                st.dataframe(pd.read_sql_query("SELECT * FROM members", conn))
            with tab3:
                st.dataframe(pd.read_sql_query("SELECT * FROM loans", conn))


    # Zone de saisie pour la requête SQL
    query_placeholder = "SELECT * FROM employees;" if db_type == "employees" else "SELECT * FROM books;"
    query = st.text_area(
        "Écrivez votre requête SQL ici:", height=150, value=query_placeholder
    )

    # Exécution de la requête
    if st.button("Exécuter la requête"):
        try:
            cursor = conn.cursor()
            
            # Exécuter et récupérer les résultats (limitation des résultats)
            cursor.execute(query)
            
            # Si c'est une requête DML, afficher un message de succès
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                conn.commit()
                st.success(f"Requête DML exécutée. {cursor.rowcount} ligne(s) affectée(s).")
            else:
                results = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]

                # Convertir les résultats en DataFrame pandas
                df = pd.DataFrame(results, columns=column_names)

                # Afficher les résultats
                st.subheader("Résultats:")
                st.dataframe(df)

                # Afficher le nombre de lignes retournées
                st.info(f"La requête a retourné **{len(df)}** enregistrement(s).")

        except Exception as e:
            st.error(f"Erreur d'exécution de la requête: {e}")

    # Exemples de requêtes
    with st.expander("Exemples de requêtes communes"):
        st.code("SELECT name, salary FROM employees WHERE department = 'IT';")
        st.code(
            "SELECT department, COUNT(id) FROM employees GROUP BY department HAVING COUNT(id) > 1;"
        )


def show_schemas(conn):
    st.header("Schémas de Base de Données")

    db_type = st.selectbox(
        "Sélectionnez le schéma à explorer (et à utiliser dans le testeur/exercices):",
        ["employees", "library"],
        format_func=lambda x: x.capitalize(),
        key="selected_db_type"
    )
    
    # Re-initialiser la base de données avec le schéma sélectionné
    init_database(conn, db_type=db_type)
    st.success(f"Le schéma **{db_type.capitalize()}** a été chargé dans la base de données en mémoire pour la pratique.")


    if db_type == "employees":
        st.subheader("Schéma Employés & Départements")

        st.code(
            """
        +---------------+       +---------------+
        | employees     |       | departments   |
        +---------------+       +---------------+
        | id (PK)       | ----> | id (PK)       |
        | name          |       | name          |
        | age           |       | manager_id (FK -> employees.id)|
        | department    |       | budget        |
        | salary        |       +---------------+
        +---------------+
        """
        )

        st.subheader("Données d'exemple:")
        tab1, tab2 = st.tabs(["Table 'employees'", "Table 'departments'"])

        with tab1:
            df = pd.read_sql_query("SELECT * FROM employees", conn)
            st.dataframe(df)

        with tab2:
            df = pd.read_sql_query("SELECT * FROM departments", conn)
            st.dataframe(df)

    elif db_type == "library":
        st.subheader("Schéma Bibliothèque")

        st.code(
            """
        +---------------+      +----------------+      +---------------+
        | books         |      | loans          |      | members       |
        +---------------+      +----------------+      +---------------+
        | id (PK)       | <----| book_id (FK)   |      | id (PK)       |<--
        | title         |      | id (PK)        |      | name          |  |
        | author        |      | member_id (FK) |----> | email         |  |
        | category      |      | loan_date      |      +---------------+  |
        +---------------+      | return_date    |                         |
                               +----------------+ -------------------------
        """
        )
        st.write("Ce schéma est chargé et prêt à être interrogé.")

        st.subheader("Données d'exemple:")
        tab1, tab2, tab3 = st.tabs(["Table 'books'", "Table 'members'", "Table 'loans'"])

        with tab1:
            df = pd.read_sql_query("SELECT * FROM books", conn)
            st.dataframe(df)
        with tab2:
            df = pd.read_sql_query("SELECT * FROM members", conn)
            st.dataframe(df)
        with tab3:
            df = pd.read_sql_query("SELECT * FROM loans", conn)
            st.dataframe(df)


def show_exercises(conn, db_type):
    st.header("Exercices Pratiques SQL")
    
    # S'assurer que le schéma 'employees' est le schéma par défaut pour les exercices pré-écrites
    if db_type != "employees":
        st.warning(f"Les exercices sont conçus pour le schéma **Employés/Départements**. Basculez vers ce schéma pour la pratique.")
        if st.button("Charger le schéma Employés/Départements"):
            init_database(conn, db_type="employees")
            st.session_state["selected_db_type"] = "employees"
            st.rerun()
        return

    st.write(
        """
    Pratiquez vos compétences SQL en résolvant des exercices sur le schéma **Employés/Départements**.
    La vérification de votre solution est **robuste** et compare le résultat final.
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

        st.info(f"Colonnes attendues dans le résultat: **{exercise['expected_columns']}**")

        with st.expander("Voir le schéma de la base de données"):
            st.code(
                """
            -- Table 'employees' : id, name, age, department, salary
            -- Table 'departments' : id, name, manager_id, budget
            """
            )
            # Afficher les données pour référence
            st.dataframe(pd.read_sql_query("SELECT * FROM employees", conn))


        # Zone de saisie pour la solution
        user_solution = st.text_area("Votre solution SQL:", height=100)

        # Vérification de la solution
        if st.button("Vérifier la solution"):
            if user_solution.strip():
                # Utiliser la fonction de comparaison améliorée
                is_correct, user_df, message = compare_query_results(
                    user_solution, exercise["expected"], conn
                )

                if user_df is not None:
                    st.subheader("Votre résultat:")
                    st.dataframe(user_df)

                if is_correct:
                    st.success("Félicitations! Votre solution est correcte! 🎉")
                else:
                    st.error(f"Solution Incorrecte. {message}")

                    # Afficher un indice
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Afficher un indice 💡"):
                            st.info(f"**Indice :** {exercise['hint']}")

                    # Option pour voir la solution
                    with col2:
                        if st.button("Voir la solution 👁️"):
                            st.code(exercise["expected"])

            else:
                st.warning("Veuillez saisir une solution avant de vérifier.")

# --- Fonction principale ---

def main():
    st.title("Application de Révision SQL")
    
    # Initialisation de la base de données par défaut ou chargement de l'état
    if "selected_db_type" not in st.session_state:
        st.session_state["selected_db_type"] = "employees"
        
    conn = create_connection()

    if conn is not None:
        # Initialisation avec le type de BDD sélectionné
        init_database(conn, db_type=st.session_state["selected_db_type"]) 

        # Barre latérale pour la navigation
        menu = st.sidebar.selectbox(
            "Navigation",
            [
                "Accueil",
                "Quiz SQL",
                "Testeur de Requêtes",
                "Schémas de Base de Données",
                "Exercices Pratiques",
            ],
        )
        
        # Affichage des sections
        if menu == "Accueil":
            show_home()
        elif menu == "Quiz SQL":
            show_quiz()
        elif menu == "Testeur de Requêtes":
            show_query_tester(conn, st.session_state["selected_db_type"])
        elif menu == "Schémas de Base de Données":
            show_schemas(conn)
        elif menu == "Exercices Pratiques":
            show_exercises(conn, st.session_state["selected_db_type"])

        conn.close()
    else:
        st.error("Erreur critique lors de la connexion à la base de données.")


if __name__ == "__main__":
    main()
