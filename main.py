# project instructions link: https://learn.365datascience.com/projects/calculating-free-to-paid-conversion-rate-with-sql/

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

    # call configuration file and method
    config = load_config()

    try: 
        # connect to database
        with psycopg2.connect(**config) as conn:
            print("Connection Established")

            #create cursors
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()


                # Print table
                # print("The number of parts: ", cur.rowcount)
                # for row in rows:
                #     print(row)

                # Separating x and y data
                date_diff_reg_watch = [row[4] for row in rows]
                date_diff_watch_purch = [row[5] for row in rows]
                
                # Calculate mean, median, mode for difference date between student registration and watching video
                mean = numpy.mean(date_diff_reg_watch)
                medium = numpy.median(date_diff_reg_watch)
                mode = stats.mode(date_diff_reg_watch)
                print('date_diff_reg_watch')
                print(mean)
                print(medium)
                print(mode)

                # Create array from column data and remove NoneType using filter
                a = numpy.array(date_diff_watch_purch)
                b = list(filter(lambda item: item is not None, a))
                # print(b)

                # Calculate mean, median, mode for difference date between watching video and purchasing 365
                mean_wp = numpy.mean(b)
                medium_wp = numpy.median(b)
                mode_wp = stats.mode(b)
                print('date_diff_watch_purch')
                print(mean_wp)
                print(medium_wp)
                print(mode_wp)

                fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
                axs[0].hist(date_diff_reg_watch)
                axs[1].hist(b, color='lightgreen', ec='black')
                plt.show()
                # Plotting the graph
                # plt.bar(locotype, code)
                # plt.xlabel('Locotype')
                # plt.ylabel('Code')
                # plt.title('Bar Graph of Categories')
                # plt.xticks(rotation=45)
                # plt.show()

                # # Separating x and y data
                # locotype = [row[0] for row in rows]
                # code = [row[1] for row in rows]

                # # Plotting the graph
                # plt.bar(locotype, code)
                # plt.xlabel('Locotype')
                # plt.ylabel('Code')
                # plt.title('Bar Graph of Categories')
                # plt.xticks(rotation=45)
                # plt.show()


    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

if __name__ == '__main__':
    plot_data()
