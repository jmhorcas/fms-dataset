import sys
import argparse
import csv
import statistics


def main(filepath: str) -> None:
    for column in ['Features', 'Configurations']:
        data = []
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row[column]:
                    try:
                        data.append(int(row[column]))
                    except:
                        data.append(float(row[column]))
                
        data.sort()
        q1 = statistics.quantiles(data, n=4)[0]  # 0.25 quantile
        q2 = statistics.median(data)  # 0.5 quantile (median)
        q3 = statistics.quantiles(data, n=4)[2]  # 0.75 quantile
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        lower_whisker = min(x for x in data if x >= lower_bound)
        upper_whisker = max(x for x in data if x <= upper_bound)
        avg = statistics.mean(data)

        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        print(f'Column: {column}')
        print(f" |-Lower quartile (Q1): {q1}")
        print(f" |-Median (Q2): {q2}")
        print(f" |-Upper quartile (Q3): {q3}")
        print(f" |-Lower whisker: {lower_whisker}")
        print(f" |-Upper whisker: {upper_whisker}")
        print(f" |-Average: {avg}")
        print(f" |-Outliers: {outliers}")
        print()


if __name__ == '__main__':
    sys.set_int_max_str_digits(100000)

    parser = argparse.ArgumentParser(description='Get boxplot statistics.')
    parser.add_argument(metavar='path', dest='path', type=str, help='csvfile')
    args = parser.parse_args()

    main(args.path)

