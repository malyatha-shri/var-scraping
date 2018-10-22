import requests
import pandas as pd

start_url = "https://www.sec.gov/Archives/"


def get_10k_path(q_start, q_end, y_start, y_end):

    sample_10K = pd.DataFrame()

    for year in range(y_start, y_end + 1):

        for quarter in range(q_start, q_end + 1):

            try:
                # requests.models.Response object
                idx_page = requests.get(
                    start_url + "edgar/full-index/" + str(year) + "/QTR" + str(quarter) + "/master.idx")

                data = pd.read_table(io.StringIO(idx_page.content.encode('utf-8').decode('cp1252')), skiprows=11,
                                     header=None, sep="|")
                data.columns = ['CIK', 'Company_Name', 'Form_Type', 'Date_Filed', 'FileName']

                filtered_10K = data[data["Form_Type"].isin(["10-Q"])]
                filtered_10K['Year_Quarter'] = "Y" + str(year) + "Q" + str(quarter)

                sample_10K = sample_10K.append(filtered_10K)

            except Exception as e:
                print 'Exception'
                print e
                continue

    sample_10K.to_csv("sample_10K.csv", index=False)

    print 'DONE SAMPLING 10-K!'

    return sample_10K


if __name__ == '__main__':

    q_start = 1
    q_end = 4
    y_start = 2002
    y_end = 2018

    sample_10K = get_10k_path(q_start, q_end, y_start, y_end)