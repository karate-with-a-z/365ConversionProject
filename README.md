# Student Engagement and Purchase Analysis

## Overview

This project aims to analyze student engagement and purchase behaviors for the 365 DataScience platform using PostgreSQL queries and a Python script. The PostgreSQL queries extract data about student interactions and calculate key metrics, while the Python script performs further analysis and visualization.

## Setup Instructions

### 1. Database Setup

To set up the database, execute the SQL script provided in the `db_course_conversions.sql` file in your PostgreSQL environment. This will create the necessary tables and sample data.

### 2. PostgreSQL Queries

#### Original Query

This query extracts detailed information about student engagement and purchase behavior.

```sql
SELECT 
    i.student_id,
    i.date_registered,
    MIN(e.date_watched) AS first_date_watched,
    MIN(p.date_purchased) as first_date_purchased,
    (MIN(e.date_watched) - i.date_registered) as date_diff_reg_watch,
    (MIN(p.date_purchased) - MIN(e.date_watched)) as date_diff_watch_purch
FROM 
    student_info i
    INNER JOIN student_engagement e ON i.student_id = e.student_id
    LEFT JOIN student_purchases p ON  i.student_id = p.student_id
GROUP BY
    i.student_id
HAVING
    MIN(e.date_watched) <= MIN(p.date_purchased) OR MIN(p.date_purchased) IS NULL;
```

#### Metrics Query

This query calculates conversion rates and average days between different student interactions.

```sql
SELECT 
    ROUND((COUNT(CASE WHEN date_diff_watch_purch >=0 THEN student_id END)*1.0/COUNT(*))*100,2) AS conversion_rate,
    ROUND(SUM(date_diff_reg_watch)*1.0/COUNT(CASE WHEN date_diff_reg_watch >=0 THEN student_id END), 2) AS av_reg_watch_days,
    ROUND(SUM(date_diff_watch_purch)*1.0/COUNT(CASE WHEN date_diff_watch_purch >=0 THEN student_id END), 2) AS av_watch_purch_days
FROM
    (SELECT 
        i.student_id,
        i.date_registered,
        MIN(e.date_watched) AS first_date_watched,
        MIN(p.date_purchased) as first_date_purchased,
        (MIN(e.date_watched) - i.date_registered) as date_diff_reg_watch,
        (MIN(p.date_purchased) - MIN(e.date_watched)) as date_diff_watch_purch
    FROM 
        student_info i
        INNER JOIN student_engagement e ON i.student_id = e.student_id
        LEFT JOIN student_purchases p ON  i.student_id = p.student_id
    GROUP BY
        i.student_id
    HAVING
        MIN(e.date_watched) <= MIN(p.date_purchased) OR MIN(p.date_purchased) IS NULL
        ) a;
```

#### AGE() Function Query

This query uses the `AGE()` function to calculate date differences, though it is less suitable for further statistical analysis.

```sql
SELECT 
    i.student_id,
    i.date_registered,
    MIN(e.date_watched) AS first_date_watched,
    MIN(p.date_purchased) as first_date_purchased,
    AGE(e.date_watched, i.date_registered) as date_diff_reg_watch,
    AGE(p.date_purchased, MIN(e.date_watched)) as date_diff_watch_purch
FROM 
    student_engagement e 
    JOIN student_info i ON i.student_id = e.student_id
    JOIN student_purchases p ON  p.student_id = i.student_id
GROUP BY
    i.student_id,
    e.date_watched,
    p.date_purchased
HAVING
    MIN(e.date_watched) <= MIN(p.date_purchased);
```

### 3. Python Script

The Python script connects to the PostgreSQL database, executes the query, and performs analysis and visualization. Ensure you have the required libraries installed (`psycopg2`, `matplotlib`, `numpy`, `scipy`).

Save the following Python script as `analyze_data.py`.

```python
import psycopg2
import matplotlib.pyplot as plt
import numpy
from scipy import stats
from config import load_config

def plot_data():

    query = """\
SELECT 
    i.student_id,
    i.date_registered,
    MIN(e.date_watched) AS first_date_watched,
    MIN(p.date_purchased) as first_date_purchased,
    (MIN(e.date_watched) - i.date_registered) as date_diff_reg_watch,
    (MIN(p.date_purchased) - MIN(e.date_watched)) as date_diff_watch_purch
FROM 
    student_info i
    INNER JOIN student_engagement e ON i.student_id = e.student_id
    LEFT JOIN student_purchases p ON  i.student_id = p.student_id
GROUP BY
    i.student_id
HAVING
    MIN(e.date_watched) <= MIN(p.date_purchased) OR MIN(p.date_purchased) IS NULL;
"""

    # Load configuration from file
    config = load_config()

    try: 
        # Connect to the database
        with psycopg2.connect(**config) as conn:
            print("Connection Established")

            # Create a cursor and execute the query
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                # Extract and process data
                date_diff_reg_watch = [row[4] for row in rows]
                date_diff_watch_purch = [row[5] for row in rows]
                
                # Calculate statistics
                mean = numpy.mean(date_diff_reg_watch)
                median = numpy.median(date_diff_reg_watch)
                mode = stats.mode(date_diff_reg_watch)
                print('date_diff_reg_watch')
                print(f"Mean: {mean}")
                print(f"Median: {median}")
                print(f"Mode: {mode.mode[0]} with count {mode.count[0]}")

                # Clean and calculate statistics for purchase data
                filtered_watch_purch = list(filter(lambda item: item is not None, date_diff_watch_purch))
                mean_wp = numpy.mean(filtered_watch_purch)
                median_wp = numpy.median(filtered_watch_purch)
                mode_wp = stats.mode(filtered_watch_purch)
                print('date_diff_watch_purch')
                print(f"Mean: {mean_wp}")
                print(f"Median: {median_wp}")
                print(f"Mode: {mode_wp.mode[0]} with count {mode_wp.count[0]}")

                # Plot histograms
                fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
                axs[0].hist(date_diff_reg_watch, bins=30, color='skyblue', edgecolor='black')
                axs[0].set_title('Days between Registration and Watching')
                axs[0].set_xlabel('Days')
                axs[0].set_ylabel('Frequency')

                axs[1].hist(filtered_watch_purch, bins=30, color='lightgreen', edgecolor='black')
                axs[1].set_title('Days between Watching and Purchase')
                axs[1].set_xlabel('Days')

                plt.show()
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

if __name__ == '__main__':
    plot_data()
```

### Configuration File

Create a configuration file named `config.py` to store your database connection details.

```python
def load_config():
    return {
        'dbname': 'your_db_name',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'your_host',
        'port': 'your_port'
    }
```

## Usage

1. **Set Up the Database:** Run the `db_course_conversions.sql` script to create and populate the database.
2. **Run the Python Script:** Execute the `main.py` script to connect to the database, fetch the data, perform analysis, and generate visualizations.

```bash
python analyze_data.py
```

## Project Instructions

For further details and project instructions, refer to the [project instructions link](https://learn.365datascience.com/projects/calculating-free-to-paid-conversion-rate-with-sql/).
