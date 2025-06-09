# Table of Contents
- [Table of Contents](#table-of-contents)
- [Challenges of modeling variability in practice with UVL: A Dataset of real-world product lines](#challenges-of-modeling-variability-in-practice-with-uvl-a-dataset-of-real-world-product-lines)
  - [Artifact description](#artifact-description)
  - [Classification of FMs](#classification-of-fms)
  - [How to use it](#how-to-use-it)
    - [Requirements](#requirements)
    - [Download and installation](#download-and-installation)
    - [Execution of the scripts](#execution-of-the-scripts)
  
  
# Challenges of modeling variability in practice with UVL: A Dataset of real-world product lines
This repository contains all the resources and artifacts that support the paper entitled "Dataset of feature models from the real world manually synthesized." accepted at the 29th International Systems and Software Product Line Conference (SPLC 2025).


## Artifact description
We present a dataset of feature models (FMs) of the restaurant business domain using the full expressiveness power of the [Universal Variability Language (UVL)](https://universal-variability-language.github.io/).

The artifact includes:
1. The FM dataset with 53 feature models in UVL extracted from 30 brochures of 11 different real-world business.
2. The Python scripts to replicate the experiments of the paper. This includes the following scripts:
  - [count_complexity.py](count_complexity.py): Read an FM in UVL (.uvl) or a directory with a dataset of FMs and generate a `complexity.csv` file with the number of features and the estimated number of configurations for each model.
  - [stats_complexity.py](stats_complexity.py): Read the .csv file generated with the previous `count_complexity` script, and show the statistical information of the dataset to plot a boxplot graph. That is, the median, the average, the lower and upper quartile, the lower and upper whisker, and the outliers.
  - [count_language_constructs.py](count_language_constructs.py): Read an FM in UVL (.uvl) or a directory with a dataset of FMs and generate a `language_constructs.csv` file with the number of ocurrencies of the language constructs of each language level (major and minor) in UVL for each model.
  - [stats_language_constructs.py](stats_language_constructs.py): Read the .csv file generated with the previous `count_language_constructs` script, and show the statistical information of the dataset. That is, for each language construct level it shows the mean, standard deviation, count and percentage of those constructs according to the number of models in the dataset.
3. The [results of our evaluation](evaluation/) containing all .csv result files and [instructions to replicate the experiments](#execution-of-the-scripts).


## Classification of FMs

| Business   |  Portfolio type                         | #Brochures | #UVL FMs | 
| ---------- | --------------------------------------- | ---------- | -------- | 
| Business01 | Fully customizable menus                | 12         | 14       | 
| Business02 | Fully customizable menus                | 3          | 10       | 
| Business03 | Products with implicit variation points | 1          | 1        |
| Business04 | Product listings                        | 1          | 1        | 
| Business05 | Fully customizable menus                | 4          | 4        | 
| Business06 | Product listings                        | 1          | 1        | 
| Business07 | Product listings                        | 5          | 1        | 
| Business08 | Fully customizable menus                | 3          | 3        | 
| Business09 | Product listings                        | 1          | 1        | 
| Business10 | Product listings                        | 1          | 3        | 
| Business10 | Products with implicit variation points | 1          | 1        | 
| Business11 | Fully customizable menus                | 1          | 13       | 
| **TOTAL: 11 different business**  |                  | **30**     | **53**   | 

## How to use it

### Requirements
We relies on [flamapy](https://flamapy.github.io/) to analyze the datasets.
In particular, the main dependencies are:

- [Python 3.9+](https://www.python.org/)
- [Flamapy](https://flamapy.github.io/)

The framework has been tested in Linux and Windows 11.


### Download and installation
1. Install [Python 3.9+](https://www.python.org/)
2. Download/Clone this repository and enter into the main directory.

    `git clone https://github.com/jmhorcas/restaurant-domain.git`

    `cd restaurant-domain`

3. Create a virtual environment: `python -m venv env`
4. Activate the environment: 
   
   In Linux: `source env/bin/activate`

   In Windows: `.\env\Scripts\Activate`

5. Install dependencies (flamapy): `pip install -r requirements.txt`
     
    ** In case that you are running Ubuntu and get an error installing flamapy, please install the package python3-dev with the command `sudo apt update && sudo apt install python3-dev` and update wheel and setuptools with the command `pip  install --upgrade pip wheel setuptools` before step 5.


### Execution of the scripts
Here we show how to execute the scripts to analyze a dataset and replicate the experiments of the paper.
You can use the restaurant business dataset available in [models folder](models/dataset_RestaurantDomain/) or any other dataset from the literature. Current datasets from the literature are the following:
- [FMBenchmark](models/dataset_FMBenchmark/), originally obtained from [here](https://github.com/SoftVarE-Group/feature-model-benchmark/tree/master).
- [UVLHub](models/dataset_UVLHub_2025_03_31/), originally obtained from [here](https://www.uvlhub.io/).
- [SPLOT](models/dataset_SPLOT/), originally obtained from [here](http://uvlhub.io/doi/10.5281/zenodo.12697473). The SPLOT dataset is available also as part of UVLHub in UVL format.

For each script, we describe its syntaxis, inputs, outputs, and an example of execution.

- **Complexity:** Count the number of features and the estimated number of configurations for each model in the dataset.
  
  - Execution: `python count_complexity.py DATASET_DIR`
  - Inputs: 
    - The `DATASET_DIR` parameter specifies the file path of the folder containing the FMs of the dataset to analyze.
    - Alternatively, the `DATASET_DIR` parameter can specify only one FMs to analyze it in solitary.
  - Outputs:
    - A `complexity.csv` with the results.
    - A `complexity.log` file with warning and errors in case some FMs have syntax errors or other problems.
  - Example: `python count_complexity.py models/dataset_RestaurantDomain/`

- **Complexity Stats:** Show statistical information of the dataset to plot a boxplot graph from the previous `complexity.csv` results file.
  
  - Execution: `python stats_complexity.py CSV_FILE`
  - Inputs: 
    - The `CSV_FILE` parameter specifies the file path of the `complexity.csv` file generated with the previous script.
  - Outputs:
    - The results are shown in the standard output.
  - Example: `python stats_complexity.py complexity.csv`

- **Language constructs:** Count the number of ocurrencies of the language constructs of each language level (major and minor) in UVL for each model in the dataset.
  
  - Execution: `python count_language_constructs.py DATASET_DIR`
  - Inputs: 
    - The `DATASET_DIR` parameter specifies the file path of the folder containing the FMs of the dataset to analyze.
    - Alternatively, the `DATASET_DIR` parameter can specify only one FMs to analyze it in solitary.
  - Outputs:
    - A `language_constructs.csv` with the results.
    - A `language_constructs.log` file with warning and errors in case some FMs have syntax errors or other problems.
  - Example: `python count_language_constructs.py models/dataset_RestaurantDomain/`

- **Language Constructs Stats:** Show statistical information of the dataset from the previous `language_constructs.csv` results file.
  
  - Execution: `python stats_language_constructs.py CSV_FILE`
  - Inputs: 
    - The `CSV_FILE` parameter specifies the file path of the `language_constructs.csv` file generated with the previous script.
  - Outputs:
    - The results are shown in the standard output.
  - Example: `python stats_language_constructs.py language_constructs.csv`