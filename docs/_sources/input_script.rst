.. _input_script:

Input script
============

The input file of AESP is a json format file, which is mainly composed of two 
main parts, namely, the configuration files of dflow (dflow_config, dflow_s3_config), 
and some configurations of the algorithms of AESP (aesp_config).

For all the aesp commands, one need to provide `dflow <https://github.com/deepmodeling/dflow>`_ global configurations. 
Generally set to the following mode:

.. code:: json

    "dflow_config" : {
		"mode" : "debug"
	},
    "dflow_s3_config" : {}

The aesp simply pass all keys of "dflow_config" to dflow.config and all keys of "dflow_s3_config" to dflow.s3_config.

There are two main modes of aesp_config, one is the conventional genetic 
algorithm structure prediction process, which utilizes empirical potentials, 
quantum mechanical calculations, and trained machine learning potential functions
for structure prediction; the other is the use of a combination of active 
learning and machine learning potentials to speed up the efficiency of structure
prediction. 

Standard mode
^^^^^^^^^^^^^

.. code:: json

    "aesp_config" : {
        "mode": "std-csp"
    }

First the population as well as the generation parameters

.. code:: json

    "aesp_config" : {
        "opt_params" : {
            "generation" : {
                "gen_size" : 50, 
                "adaptive" : {
                    "type" : "rca",
                    "size_change_ratio" : 0.5
                }
            },
            "population" : {
                "pop_size" : 40,
                "adaptive" : {
                    "type" : "rca",
                    "size_change_ratio" : 0.5
                }	
            }
        }  
    }

The parameters of ``generation`` and ``population`` are basically the same, but 
we'd better keep the ``size`` of ``population`` larger than that of ``generation``
; where ``adaptive`` is the parameter of self-adaptation, and there are also two 
ways. Both ways have the same parameter ``size_change_ratio``, which represents 
the ratio of the change in ``size``; for example, if ``size`` is 50, the range 
of the change in ``size`` is [50*(1-0.5), 50*(1+0.5)].


Next are some operator arguments

.. code:: json

    "aesp_config" : {
        "opt_params" : {
            "type" : "std",
            "operator" : {
                "type" : "bulk",
                "generator" : {
                    "prob" : 0.4,
                    "random_gen_prob" : 1,
                    "random_gen_params" : {
                        "composition" : {"B": 1, "C": 3},
                        "_spgnum" : ["1-230"],
                        "factor" : 1.1,
                        "_thickness" : 2,
                        "max_count" : 50
                    }
                },
                "crossover" : {
                    "prob" : 0.3,
                    "plane_cross_prob" : 0.333,
                    "sphere_cross_prob" : 0.333,
                    "cylinder_cross_prob" : 0.334,
                    "plane_cross_params" : {
                        "stddev" : 0.1,
                        "max_count" : 5
                    },
                    "sphere_cross_params" : {
                        "max_count" : 5
                    },
                    "cylinder_cross_params" : {
                        "max_count" : 5
                    }
                },
                "mutation" : {
                    "prob" : 0.3,
                    "continuous_mut_factor" : 2, 
                    "strain_mut_prob" : 0.333,
                    "permutation_mut_prob" : 0.333,
                    "ripple_mut_prob" : 0.334,
                    "strain_mut_params" : {
                        "stddev" : 0.1,
                        "max_count" : 5
                    },
                    "permutation_mut_params" : {
                        "max_count" : 5
                    },
                    "ripple_mut_params" : {
                        "max_count" : 5,
                        "rho" : 0.3,
                        "miu" : 2,
                        "eta" : 1
                    }
                },
                "adaptive" : {
                    "type": "adjustment",
                    "use_recent_gen" : 2
                },
                "hard_constrains" : {
                    "alpha" : [30, 150],
                    "beta" : [30, 150],
                    "gamma" : [30, 150],
                    "chi" : [0, 180],
                    "psi" : [0, 180],
                    "phi" : [0, 180],
                    "a" : [0, 100],
                    "b" : [0, 100],
                    "c" : [0, 100],
                    "tol_matrix" : {
                        "_tuples" : [["Cl", "Na", 12], ["Cl", "Cl", 12], ["Na", "Na", 12]],
                        "prototype" : "atomic", 
                        "factor" : 1.0
                    }
                }
            }
        }
    }

The ``operator`` contains various modes depending on the system, namely bulk, 
cluster. The ``operator`` contains three modes, namely ``generator``, ``mutation``
and ``crossover``. The following ``adaptive`` refers to the adaptive parameters 
of the three operators. Among them ``type`` has two ways. The ``hard_constrains``
represent some constraints on the structure generated by each operator. It 
contains some constraints on the angles of the lattice (including dihedral 
angles) and on the lattice constants; ``tol_matrix`` is some constraints on 
the interatomic distances. The ``prob`` in ``generator``, ``mutation``, and 
``crossover`` represents the probability of choosing that mode, and the sum 
of the three probabilities is 1. Each of these operators has separate modes 
of operation, and their probabilities are ``xxx_gen_prob`` (summed to 1), 
``xxx_mut_prob`` (summed to 1), and ``xx_gen_prob`` (summed to 1). mut_prob`` 
(sums to 1) and ``xxx_cross_prob`` (sums to 1). And ``xxx_xxx_params`` 
corresponds to the parameters of the corresponding operation.

At the same time we need to define the convergence conditions for the algorithm, 
that is, ``cvg_criterion`` .

.. code:: json
    
    "aesp_config" : {
        "opt_params" : {
            "cvg_criterion" : {
                "max_gen_num" : 10,
                "continuous_opt_num" : null
            }
        }
    }

We also need to specify how each structure is calculated

.. code:: json
    "aesp_config" : {
        "calc_stages" : [
            {
                "type" : "vasp",
                "task_max" : 1,
                "pstress" : 0.0,
                "inputs_config" : {
                    "incar" : "../1_INCAR",
                    "kspacing": 0.4,
                    "kgamma": false,
                    "pp_files": {"B": "../../POTCAR_B", "C": "../../POTCAR_C"}
                },
                "run_config" : {
                    "command" : "mpirun -np 2 vasp_std",
                    "_command" : "source /opt/intel/oneapi/setvars.sh;mpirun -np 8 vasp_std"
                }
            },
            {
                "type" : "vasp",
                "task_max" : 1,
                "pstress" : 0.0,
                "inputs_config" : {
                    "incar" : "../2_INCAR",
                    "kspacing": 0.25,
                    "kgamma": false,
                    "pp_files": {"B": "../../POTCAR_B", "C": "../../POTCAR_C"}
                },
                "run_config" : {
                    "command" : "mpirun -np 2 vasp_std",
                    "_command" : "source /opt/intel/oneapi/setvars.sh;mpirun -np 8 vasp_std"
                }
            }
        ]
    }
   




The execution units of the aesp are the dflow Steps. How each step is executed is defined by the "step_configs".

.. code:: json

    "aesp_config" : {
        "step_configs" : {}
    }

The configs for prepare training, run training, prepare exploration, run exploration, prepare fp, 
run fp, select configurations, collect data and concurrent learning steps are given correspondingly.

Any of the config in the "step_configs" can be ommitted. If so, the configs of the step is set to the 
default step configs, which is provided by the following section, for example,

.. code:: json

    "aesp_config" : {
        "default_step_config" : {
            "template_slice_config" : {
                "group_size": 8,
                "pool_size" : 1
            },
            "executor" : {
                "type" : "dispatcher",
                "host" : "127.0.0.1",
                "image_pull_policy" : "IfNotPresent",
                "username" : "clqin",
                "password" : "clqin",
                "machine_dict" : {
                    "batch_type" : "Shell",
                    "context_type" : "local",
                    "local_root" : "./",
                    "remote_root" : "/home/zhao/work"
                },
                "resources_dict" : {
                    "cpu_per_node" : 8,
                    "gpu_per_node" : 1,
                    "group_size" : 1
                }
            }
        }
    }

The way of writing the "default_step_config" is the same as any step config in the "step_configs".



active learning
^^^^^^^^^^^^^^^

.. note::

    Under test

