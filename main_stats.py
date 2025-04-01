import os
import sys
import argparse
import logging
import csv
import math
import pathlib
import itertools
import statistics
from enum import Enum
from typing import Any

from flamapy.core.discover import DiscoverMetamodels
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.models import Feature, Relation

from fm_secure_features_names import FMSecureFeaturesNames


def main(filepath: str, column: str) -> None:
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

    print(f"Lower quartile (Q1): {q1}")
    print(f"Median (Q2): {q2}")
    print(f"Upper quartile (Q3): {q3}")
    print(f"Lower whisker: {lower_whisker}")
    print(f"Upper whisker: {upper_whisker}")
    print(f"Average: {avg}")
    print(f"Outliers: {outliers}")


if __name__ == '__main__':
    sys.set_int_max_str_digits(100000)

    parser = argparse.ArgumentParser(description='Get boxplot statistics.')
    parser.add_argument(metavar='path', dest='path', type=str, help='csvfile')
    parser.add_argument(metavar='column', dest='column', type=str, help='column')
    args = parser.parse_args()

    main(args.path, args.column)

