from dargs import Argument, Variant
from ..structure.bulk import Bulk
# from aesp.structure.layer import layer
from ..structure.cluster import Cluster


def opt_params_variant():
    doc_type = "Evolutionary algorithms based on different principles."
    doc_std = "Evolutionary algorithms based on each generation."
    inputs_list = []
    inputs_list.append(Argument("std", dict, std_config(), doc=doc_std))
    # inputs_list.append(Argument("pool", dict, pool_config()))
    return Variant("type", inputs_list, optional=True, default_tag='std', doc=doc_type)

def std_config():
    doc_generation = "Evolutionary algorithms are an iterative process, and each iteration is called a generation."
    doc_population = "In a evolutionary algorithm, a population is a collection of individuals."
    doc_operator = "The operator of structure generation."
    doc_cvg_criterion = "Convergence criteria for evolutionary algorithms"
    doc_seeds = "File path of random seed, i.e. the customized initial structure file."
    return[
        Argument("generation", dict, generation_config(), optional=False, doc=doc_generation),
        Argument("population", dict, population_config(), optional=False, doc=doc_population),
        Argument("operator", dict, sub_variants=[operator_variant()], optional=False, doc=doc_operator),
        Argument("cvg_criterion", dict, cvg_criterion_confg(), optional=False, doc=doc_cvg_criterion),
        Argument("seeds", str, optional=True, default=None, doc=doc_seeds)
    ]


# generation ---------------------------------
def generation_config():
    doc_gen_size = "The size of the generated structures in initial generation."
    doc_adaptive_config = 'Adaptive mode'
    return [
        Argument("gen_size", int, optional=True, default=50, doc=doc_gen_size),
        Argument("adaptive", dict, generation_adaptive_config(), optional=False, doc=doc_adaptive_config)
    ]

def generation_adaptive_config():
    doc_size_change_ratio = 'The variable proportion of structure generation in each generation.'
    return [
        Argument("size_change_ratio", float, optional=True, default=0.5, doc=doc_size_change_ratio)
    ]

# population ---------------------------------
def population_config():
    doc_pop_size = "Population size in initial generation."
    doc_adaptive_config = 'Adaptive adjustment configuration'
    return [
        Argument("pop_size", int, optional=True, default=40, doc=doc_pop_size),
        Argument("adaptive", dict, population_adaptive_config(), optional=False, doc=doc_adaptive_config)
    ]

def population_adaptive_config():
    doc_size_change_ratio = 'The variable proportion of population size in each generation.'
    return [
        Argument("size_change_ratio", float, optional=True, default=0.5, doc=doc_size_change_ratio)
    ]


# ----------------------operator ----------------------
def operator_variant():
    doc_type = "The type of the operator, i.e. the type of structure to be predicted."
    doc_bulk = 'Bulk (3D)'
    inputs_list = []
    inputs_list.append(Argument("bulk", dict, Bulk.args(), doc=doc_bulk))
    # inputs_list.append(Argument("layer", dict, operator_layer_config()))
    # inputs_list.append(Argument("cluster", dict, Cluster.args()))
    return Variant("type", inputs_list, default_tag='bulk', doc=doc_type)

# -----------------adaptive-------------------
# def operator_adaptive_variant():
#     doc_adjustment = "Adjustment mode"
#     doc_distribution = "Distribution model"
#     doc_input = "Adaptive mode"
#     inputs_list = []
#     inputs_list.append(Argument("adjustment", dict, adjustment_config(), doc=doc_adjustment))
#     inputs_list.append(Argument("distribution", dict, distribution_config(), doc=doc_distribution))
#     return Variant("type", inputs_list, default_tag='adjustment', doc=doc_input)

# def adjustment_config():
#     doc_use_recent_pop = "Use of information from recent generations"
#     return [
#         Argument("use_recent_pop", int, optional=True, default=2, doc=doc_use_recent_pop),
#     ]

# def distribution_config():
#     doc_use_recent_pop = "Use of information from recent generations"
#     return [
#         Argument("use_recent_pop", int, optional=True, default=2, doc=doc_use_recent_pop)
#     ]

#  --------------cvg_criterion------------------------------------
def cvg_criterion_confg():
    doc_max_gen_num = "Maximum number of generations of evolutionary algorithms"
    doc_continuous_opt_num = "Maximum number of generations for which the optimal structure remains constant"
    return [
        Argument("max_gen_num", int, optional=True, default=10, doc=doc_max_gen_num),
        Argument("continuous_opt_num", int, optional=True, default=None, doc=doc_continuous_opt_num)
    ]
