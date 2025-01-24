import numpy as np
from deap import base, creator, tools, algorithms
from utils.XML_Parser import XMLParser
import pandas as pd
from pyBADA.bada4 import PTD
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser

def reinit_bada_xml():
    badaVersion = "DUMMY"
    allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="reference_dummy_extracted")
    # Create BADA Aircraft instance
    return Bada4Aircraft(
        badaVersion=badaVersion,
        acName="Dummy-TWIN-plus",
        allData=allData,
    )

def update_xml_coefficients(coefficients, tags, xml_parser):
    # for each tag updates it with the list of coefficients
    # right now only used for 1 tag (CD_Clean)
    for tag in tags:
        xml_parser.modify_tag(tag, coefficients)


# Define the RMSE cost function (to minimize)
def rmse_cost_function(coefficients):
    """
    Cost function to calculate RMSE after updating coefficients in the XML.

    Args:
        coefficients (list): Coefficients to update in the XML.

    Returns:
        float: Calculated RMSE.
    """
    # Update XML coefficients (use your existing method)
    update_xml_coefficients(coefficients, tags, xml_parser)

    ac = reinit_bada_xml()
    ptd = PTD(ac)

    # Recalculate Drag_BADA using the updated coefficients
    drag_bada_updated = []
    for m, c in zip(mass_list, cas):
        result = ptd.PTD_cruise_SKYCONSEIL([m], [30000], c, 0)  # Example usage
        drag_bada_updated.append(result[0][0])

    # Calculate RMSE
    rmse = np.sqrt(np.mean((np.array(drag_bada_updated) - np.array(drag_prn)) ** 2))
    return (rmse,)

# Load XML and prepare initial data
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
tags = ["CD_clean/d"]
initial_guess = xml_parser.find_tag_coefficients(tags[0])

# Load data
results_df = pd.read_csv("results.csv")
mass_list = results_df["Mass"].to_numpy()
cas = results_df["CAS"].to_numpy()
drag_prn = results_df["Drag_PRN"].to_numpy()

# Genetic Algorithm setup
NUM_COFFS = len(initial_guess)  # Number of coefficients to optimize
BOUND_LOW, BOUND_HIGH = -1813663.0, 2092064.0  # Bounds for coefficients

# DEAP setup
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimize RMSE
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", np.random.uniform, BOUND_LOW, BOUND_HIGH)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=NUM_COFFS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Register GA operators
toolbox.register("evaluate", rmse_cost_function)
toolbox.register("mate", tools.cxBlend, alpha=0.5)  # Blend crossover
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)  # Gaussian mutation
toolbox.register("select", tools.selTournament, tournsize=3)

# Genetic Algorithm execution
def genetic_algorithm():
    # Initialize population
    population = toolbox.population(n=200)  # Population size

    # Run the genetic algorithm
    result_population, log = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=0.7,  # Crossover probability
        mutpb=0.2,  # Mutation probability
        ngen=100,  # Number of generations
        verbose=True
    )

    # Extract the best individual
    best_individual = tools.selBest(result_population, k=1)[0]
    return best_individual

# Run GA
best_coefficients = genetic_algorithm()
print("Optimal Coefficients:", best_coefficients)