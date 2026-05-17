import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def initial_analysis(conn):
    query = """
        SELECT
            s.sample AS sample,
            t.total_count AS total_count,
            ct.cell_name AS cell_name,
            cc.count_val AS count,
            ROUND(cc.count_val * 100.00 / t.total_count , 2) AS percentage,
            sub.response AS response
        FROM cell_count cc
        JOIN samples s
            ON cc.sample_id = s.sample_id
        JOIN cell_types ct
            ON cc.cell_type_id = ct.cell_type_id
        JOIN subjects sub
            ON s.subject_id = sub.subject_id
        JOIN (
            SELECT
                sample_id,
                SUM(count_val) AS total_count
            FROM cell_count
            GROUP BY sample_id
        ) t
            ON cc.sample_id = t.sample_id
        WHERE sub.condition = "melanoma"
            AND sub.treatment = "miraclib"
            AND s.sample_type = "PBMC"
            AND sub.response IN ("yes", "no")
        ORDER BY
            ct.cell_name,
            sub.response
    """
    
    df = pd.read_sql(query, conn)
    print(df.head())

    if len(df) > 0:
        print("Cell types found:", df["cell_name"].unique())
    else:
        print("No rows found. Your WHERE filter probably does not match the database.")
    df.to_csv("initial_analysis.csv", index=False)

    return df

def make_boxplot(df):
    cell_name = df["cell_name"].unique()

    for cell in cell_name:
        data = df[df["cell_name"] == cell]

        boxplot = data.boxplot(column="percentage", by="response")

        boxplot.set_title(f"Frequency for {cell}")
        boxplot.set_xlabel("Response")
        boxplot.set_ylabel("Frequency")

        plt.savefig(f"boxplot_{cell}.png")
        plt.close()

def statistical_analysis(df):
    cell_name = df["cell_name"].unique()
    results = []

    for cell in cell_name:
        data = df[df["cell_name"] == cell]

        responders = data[data["response"] == "yes"]["percentage"]
        non_responders = data[data["response"] == "no"]["percentage"]

        print("Respondes:", responders)
        print("Non-responders:", non_responders)

        # Statistical analysis
        print(f"Mean for {cell}: Responders: {responders.mean()} vs Non-responders: {non_responders.mean()}")
        print(f"Median for {cell}: Responders: {responders.median()} vs Non-responders: {non_responders.median()}")
        print(f"Standard Deviation for {cell}: Responders: {responders.std()} vs Non-responders: {non_responders.std()}")
    
        row = {
            "cell_name": cell,
            "mean_responders": responders.mean(),
            "mean_non_responders": non_responders.mean(),
            "median_responders": responders.median(),
            "median_non_responders": non_responders.median(),
            "std_responders": responders.std(),
            "std_non_responders": non_responders.std()
        }
        results.append(row)
    results_df = pd.DataFrame(results)
    results_df.to_csv("statistical_analysis.csv", index=False)
    return results_df

def subset_analysis(conn):
    query = """ 
        SELECT
            p.project AS project,
            sub.subject AS subject,
            sub.sex AS sex,
            sub.response AS response,
            s.sample AS sample,
            s.time_from_treatment_start AS time_from_treatment_start
        FROM samples s
        JOIN subjects sub
            ON s.subject_id = sub.subject_id
        JOIN projects p
            ON sub.project_id = p.project_id
        WHERE sub.condition = "melanoma"
            AND sub.treatment = "miraclib"
            AND s.sample_type = "PBMC"
            AND s.time_from_treatment_start = 0
    """
    
    df = pd.read_sql(query, conn)

    samples_each = df.groupby("project")["sample"].nunique()
    responses_each = df.groupby("response")["subject"].nunique()
    sex_each = df.groupby("sex")["subject"].nunique()

    print("Data Subset Analysis")
    print("Samples each project:", samples_each)
    print("Responses each project:", responses_each)
    print("Sex each project:", sex_each)

def question_1(conn):
    query = """
        SELECT
            ROUND(AVG(cc.count_val), 2) AS average_b_cells
        FROM cell_count cc
        JOIN samples s
            ON cc.sample_id = s.sample_id
        JOIN subjects sub
            ON s.subject_id = sub.subject_id
        JOIN cell_types ct
            ON cc.cell_type_id = ct.cell_type_id
        WHERE sub.condition = "melanoma"
            and sub.sex = "M"
            and sub.response = "yes"
            and s.time_from_treatment_start = 0
            and ct.cell_name = "b_cell"
    """
    
    answer = pd.read_sql(query, conn)
    print("Considering Melanoma males, what is the average number of B cells for responders at time=0? Use two decimals (XXX.XX).")
    print("Answer:", answer)
    return answer

def main():
    conn = sqlite3.connect("cell-count.db")

    df = initial_analysis(conn)
    make_boxplot(df)
    statistical_analysis(df)
    subset_analysis(conn)
    question_1(conn)
    conn.close()

if __name__ == "__main__":
    main()