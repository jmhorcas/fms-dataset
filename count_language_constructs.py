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
from flamapy.core.models import ASTOperation
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from fm_secure_features_names import FMSecureFeaturesNames


LOG_FILE = 'FMDataset.log'
CSV_FILE_RESULTS = 'results.csv'
ERROR_STR = 'Error'


#logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(filename=LOG_FILE, filemode="w", encoding='utf-8', level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)   
LOGGER.addHandler(logging.StreamHandler())


class CSVHeader(Enum):
    MODEL = 'Model'
    BOOLEAN_FEATURES = 'BooleanFeatures'
    GROUP_KEYWORDS = 'GroupKeywords'
    BOOLEAN_CONSTRAINTS = 'BooleanConstraints'
    FEATURE_ATTRIBUTES = 'FeatureAttributes'
    GROUP_CARDINALITY = 'GroupCardinality'
    NUMERIC_CONSTRAINTS = 'NumericConstraints'
    FEATURE_CARDINALITY = 'FeatureCardinality'
    AGGREGATE_FUNCTIONS = 'AggregateFunctions'
    TYPE_FEATURES = 'TypeFeatures'
    STRING_CONSTRAINTS = 'StringConstraints'


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


def count_language_constructs(fm: FeatureModel, csv_entry: dict[str, int]) -> None:
    csv_entry[CSVHeader.BOOLEAN_FEATURES.value] = len(fm.get_boolean_features())
    csv_entry[CSVHeader.GROUP_KEYWORDS.value] = sum(r.is_optional() or r.is_mandatory() or r.is_alternative() or r.is_or() for r in fm.get_relations())
    csv_entry[CSVHeader.BOOLEAN_CONSTRAINTS.value] = len(fm.get_logical_constraints())
    csv_entry[CSVHeader.FEATURE_ATTRIBUTES.value] = len({a.name for feature in fm.get_features() for a in feature.get_attributes()})
    csv_entry[CSVHeader.GROUP_CARDINALITY.value] = sum(r.is_cardinal() for r in fm.get_relations())
    csv_entry[CSVHeader.NUMERIC_CONSTRAINTS.value] = len(fm.get_arithmetic_constraints())
    csv_entry[CSVHeader.FEATURE_CARDINALITY.value] = sum(feature.is_multifeature() for feature in fm.get_features())
    csv_entry[CSVHeader.AGGREGATE_FUNCTIONS.value] = sum(op not in [ASTOperation.LEN] for ctc in fm.get_aggregations_constraints() for op in ctc.ast.get_operators())
    csv_entry[CSVHeader.TYPE_FEATURES.value] = len(fm.get_string_features()) + len(fm.get_numerical_features())
    csv_entry[CSVHeader.STRING_CONSTRAINTS.value] = sum(op in [ASTOperation.LEN] for ctc in fm.get_aggregations_constraints() for op in ctc.ast.get_operators())


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
    
    count_language_constructs(fm, csv_entry)
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
