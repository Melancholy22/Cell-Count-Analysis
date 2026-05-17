import sqlite3
import pandas as pd

DB_NAME = "cell-count.db"
CSV_NAME = "cell-count.csv"

def create_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS cell_count")
    cursor.execute("DROP TABLE IF EXISTS cell_types")
    cursor.execute("DROP TABLE IF EXISTS samples")
    cursor.execute("DROP TABLE IF EXISTS subjects")
    cursor.execute("DROP TABLE IF EXISTS projects")

    projects_table = """
    CREATE TABLE projects (
        project_id INTEGER PRIMARY KEY,
        project TEXT NOT NULL UNIQUE
    )
    """
    cursor.execute(projects_table)

    subjects_table = """
    CREATE TABLE subjects (
        subject_id INTEGER PRIMARY KEY,
        project_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        condition TEXT NOT NULL,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL,
        treatment TEXT,
        response TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (project_id),
        UNIQUE(project_id, subject)
    )
    """
    cursor.execute(subjects_table)

    samples_table = """
    CREATE TABLE samples (
        sample_id INTEGER PRIMARY KEY,
        subject_id INTEGER NOT NULL,
        sample TEXT NOT NULL,
        sample_type TEXT NOT NULL,
        time_from_treatment_start INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subjects (subject_id),
        UNIQUE(subject_id, sample)
    )
    """
    cursor.execute(samples_table)

    cell_types_table = """
    CREATE TABLE cell_types (
        cell_type_id INTEGER PRIMARY KEY,
        cell_name TEXT NOT NULL UNIQUE
    )
    """
    cursor.execute(cell_types_table)

    cell_count_table = """
    CREATE TABLE cell_count (
        cell_count_id INTEGER PRIMARY KEY,
        sample_id INTEGER NOT NULL,
        cell_type_id INTEGER NOT NULL,
        count_val INTEGER NOT NULL,
        FOREIGN KEY (sample_id) REFERENCES samples (sample_id),
        FOREIGN KEY (cell_type_id) REFERENCES cell_types (cell_type_id),
        UNIQUE(sample_id, cell_type_id)
    )
    """
    cursor.execute(cell_count_table)


def load_data(cursor):
    df = pd.read_csv(CSV_NAME)
    for index, row in df.iterrows():
        cursor.execute(
            """
            INSERT OR IGNORE INTO projects (project)
            VALUES (?)
            """,
            (row["project"],)
        )

        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE project = ?
            """,
            (row["project"],)
        )

        project_id = cursor.fetchone()[0]
        treatment = None if pd.isna(row["treatment"]) else row["treatment"]
        response = None if pd.isna(row["response"]) else row["response"]

        cursor.execute(
            """
            INSERT OR IGNORE INTO subjects (
                project_id,
                subject,
                condition,
                age,
                sex,
                treatment,
                response
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                row["subject"],
                row["condition"],
                int(row["age"]),
                row["sex"],
                treatment,
                response
            )
        )
        cursor.execute(
            """
            SELECT subject_id
            FROM subjects
            WHERE subject = ? AND project_id = ?
            """,
            (row["subject"], project_id)
        )

        subject_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT OR IGNORE INTO samples (
                subject_id,
                sample,
                sample_type,
                time_from_treatment_start
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                subject_id,
                row["sample"],
                row["sample_type"],
                int(row["time_from_treatment_start"])
            )
        )
        cursor.execute(
            """
            SELECT sample_id
            FROM samples
            WHERE sample = ? AND subject_id = ?
            """,
            (row["sample"], subject_id)
        ) 

        sample_id = cursor.fetchone()[0]

        type_of_cell = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"] 	
        for cell in type_of_cell:
            cursor.execute(
                """
                INSERT OR IGNORE INTO cell_types (cell_name)
                VALUES (?)
                """,
                (cell,)
            )
            
            cursor.execute(
                """
                SELECT cell_type_id
                FROM cell_types
                WHERE cell_name = ?
                """,
                (cell,)
            )

            cell_type_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT OR IGNORE INTO cell_count (
                    sample_id,
                    cell_type_id,
                    count_val
                )
                VALUES (?, ?, ?)
                """,
                (
                    sample_id,
                    cell_type_id,
                    int(row[cell])
                )
            )

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_table(cursor)
    load_data(cursor)

    cursor.execute("SELECT COUNT(*) FROM projects")
    print("projects:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM subjects")
    print("subjects:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM samples")
    print("samples:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM cell_types")
    print("cell types:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM cell_count")
    print("cell count rows:", cursor.fetchone()[0])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()