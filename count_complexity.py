import os
import sys
import argparse
import logging
import csv
import math
import pathlib
import itertools
from enum import Enum
from typing import Any

from flamapy.core.discover import DiscoverMetamodels
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.models import Feature

from utils.fm_secure_features_names import FMSecureFeaturesNames


LOG_FILE = 'complexity.log'
CSV_FILE_RESULTS = 'complexity.csv'
ERROR_STR = 'Error'


logging.basicConfig(filename=LOG_FILE, filemode="w", encoding='utf-8', level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)   
LOGGER.addHandler(logging.StreamHandler())


class CSVHeader(Enum):
    MODEL = 'Model'
    FEATURES = 'Features'
    CONSTRAINTS = 'Constraints'
    CONFIGURATIONS = 'Configurations'
    HOMOGENEITY = 'Homogeneity'


class CSVWriter():

    def __init__(self, filepath: str, header: list[str]) -> None:
        self._filepath = filepath
        self._header = header
        if not pathlib.Path(filepath).exists():
            with open(self._filepath, 'a+', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self._header)
                writer.writeheader()
        
    def write_row(self, row: dict[str, Any], autocomplete: bool = True) -> None:
        with open(self._filepath, 'a+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self._header)
            writer.writerow(row)


def get_filepaths(dir: str, extensions_filter: list[str] = []) -> list[str]:
    """Get all filepaths of files with the given extensions from the given directory."""
    filepaths = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if not extensions_filter or any(file.endswith(ext) for ext in extensions_filter):
                filepath = os.path.join(root, file)
                filepaths.append(filepath)
    return filepaths


def int2sci(n: int, precision: int = 2) -> str:
    """Convert a large int into scientific notation."""
    if n == 0:
        return '0e0'
    exp = len(str(abs(n))) - 1
    mantissa = n / (10 ** exp)
    return f'{mantissa:.{precision}f}e{exp}'


def count_configurations_rec(feature: Feature) -> int:
    if feature.is_leaf():
        return 1
    counts = []
    for relation in feature.get_relations():
        if relation.is_mandatory():
            counts.append(count_configurations_rec(relation.children[0]))
        elif relation.is_optional():
            counts.append(count_configurations_rec(relation.children[0]) + 1)
        elif relation.is_alternative():
            counts.append(sum((count_configurations_rec(f) for f in relation.children)))
        elif relation.is_or():
            children_counts = [count_configurations_rec(f) + 1 for f in relation.children]
            counts.append(math.prod(children_counts) - 1)
        elif relation.is_cardinal():
            children_counts = [count_configurations_rec(f) for f in relation.children]
            cardinal_configs = []
            card_min = relation.card_min
            card_max = len(children_counts) if relation.card_max == -1 else relation.card_max
            for k in range(card_min, card_max + 1):
                combi_k = list(itertools.combinations(children_counts, k))
                for combi in combi_k:
                    cardinal_configs.append(math.prod(combi))
            counts.append(sum(cardinal_configs))
    feature_cardinality = 1
    if feature.is_multifeature():
        if feature.feature_cardinality.max == -1:
            feature_cardinality = float('inf')
        else:
            feature_cardinality = feature.feature_cardinality.max - feature.feature_cardinality.min + 1
    return math.prod(counts) * feature_cardinality


def main(fm_filepath: str) -> dict[str, Any]:
    path = pathlib.Path(fm_filepath)
    filename = path.stem

    csv_entry = {}
    csv_entry[CSVHeader.MODEL.value] = filename

    dm = DiscoverMetamodels()

    # Read the feature model
    try:
        LOGGER.debug(f'Reading feature model {path}')
        fm = dm.use_transformation_t2m(fm_filepath, 'fm')
        fm = FMSecureFeaturesNames(fm).transform()
    except FlamaException as e:
        LOGGER.error(f'Error reading feature model {path}: {e}')
        return csv_entry
    
    n_configs = count_configurations_rec(fm.root)

    # Get configurations number and homogeneity
    # try:
    #     LOGGER.debug(f'Converting FM to BDD...')
    #     bdd_model = dm.use_transformation_m2m(fm, 'bdd')
        
    #     # Get configurations number
    #     operation = dm.get_operation(bdd_model, 'BDDConfigurationsNumber')
    #     operation.execute(bdd_model)
    #     n_configs = operation.get_result()
    #     csv_entry[CSVHeader.CONFIGURATIONS.value] = n_configs

    #     # Get homogeneity
    #     operation = dm.get_operation(bdd_model, 'BDDHomogeneity')
    #     operation.execute(bdd_model)
    #     homogeneity = operation.get_result()
    #     csv_entry[CSVHeader.HOMOGENEITY.value] = homogeneity
    # except Exception as e:
    #     LOGGER.error(f'Error converting FM to BDD {path}: {e}')
    #     csv_entry[CSVHeader.CONFIGURATIONS.value] = ERROR_STR
    #     csv_entry[CSVHeader.HOMOGENEITY.value] = ERROR_STR

    csv_entry[CSVHeader.FEATURES.value] = len(fm.get_features())
    csv_entry[CSVHeader.CONSTRAINTS.value] = len(fm.get_constraints())
    csv_entry[CSVHeader.CONFIGURATIONS.value] = int2sci(n_configs) if n_configs >= 1e6 else n_configs
    LOGGER.debug(f'Done for model {fm_filepath}.')
    return csv_entry


def main_dir(dirpath: str) -> None:
    csv_writer = CSVWriter(CSV_FILE_RESULTS, [h.value for h in CSVHeader])
    with open(CSV_FILE_RESULTS, 'r') as results_file:
        content = results_file.read()
    total_models = 0
    models_filepaths = get_filepaths(dirpath, ['uvl'])
    n_models = len(models_filepaths)
    LOGGER.info(f'#Models to be processed: {n_models}')
    for i, uvl_filepath in enumerate(models_filepaths, 1):
        path = pathlib.Path(uvl_filepath)
        filename = path.stem
        if filename in content:
            LOGGER.info(f'Skipped model {uvl_filepath} ({i}/{n_models}, {round(i/n_models*100,2)}%).')    
        else:
            LOGGER.debug(f'Processing model {uvl_filepath} ({i}/{n_models}, {round(i/n_models*100,2)}%).')
            total_models += 1
            csv_entry = main(uvl_filepath)
            csv_writer.write_row(csv_entry)
    LOGGER.info(f'#Models processed: {total_models}.')


if __name__ == '__main__':
    sys.set_int_max_str_digits(100000)

    parser = argparse.ArgumentParser(description='Measure the complexity of an FM dataset.')
    parser.add_argument(metavar='path', dest='path', type=str, help='Input feature model (.uvl) or directory with models.')
    args = parser.parse_args()

    if os.path.isdir(args.path):
        main_dir(args.path)
    else:
        csv_writer = CSVWriter(CSV_FILE_RESULTS, [h.value for h in CSVHeader])
        csv_entry = main(args.path)
        csv_writer.write_row(csv_entry)
