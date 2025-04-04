import sys
import argparse
import csv
import statistics

from count_language_constructs import CSVHeader


def main(filepath: str) -> None:
    for header in list(CSVHeader)[1:]:
        column = header.value
        data = []
        rows = 0
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows += 1
                if row[column]:
                    data.append(int(row[column]))

        count = sum(d > 0 for d in data)
        avg = statistics.mean(data)
        stdev = statistics.stdev(data)

        print(f"Column: {column}")
        print(f" |-Mean: {avg}")
        print(f" |-StDev: {stdev}")
        print(f" |-Count: {count} ({(count / rows) * 100} %)")
        print()


if __name__ == '__main__':
    sys.set_int_max_str_digits(100000)

    parser = argparse.ArgumentParser(description='Get boxplot statistics.')
    parser.add_argument(metavar='path', dest='path', type=str, help='csvfile')
    args = parser.parse_args()

    main(args.path)

