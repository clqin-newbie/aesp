from ..configs.inputs import input_config
from ..configs.step_base import normalize_step_config
from dargs import Argument
from .. import __version__
import dflow
import os
import json
from ..utils.tool import expand_idx
import logging
from ..configs.dflow import workflow_config_from_dict
from art import text2art
from ..constant import dflow_status
import copy
from ..utils.tool import print_in_box
import logging

def write_input(config, config_name):
    file_name = f"input-{config_name}"
    with open(file_name, 'w') as f:
        json.dump(config, f, indent=4)
    

def print_citation():
    print_in_box(width=65, text="Author: C.L. Qin\t\t"+"Email: clqin@foxmail.com\n"+ \
            "Documentation: https://clqin-newbie.github.io/aesp/\n"+\
            "Please cite this paper when using AESP in your research:\n"+\
            "[1] Qin C, Liu J, Ma S, et al. Inverse design of semiconductor materials with deep generative models[J]. Journal of Materials Chemistry A, 2024, 12(34): 22689-22702.")

def change_logger():
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            formatter = logging.Formatter('*AESP* %(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M')
            handler.setFormatter(formatter)

def config_check(config):
     # config文件检查
    with open(config) as fp:
        config = json.load(fp)

    # spgnum解析
    config = normalize(config)
    config['aesp_config']['opt_params']['operator']['generator']['random_gen_params']['spgnum'] = expand_idx(config['aesp_config']['opt_params']['operator']['generator']['random_gen_params']['spgnum'])
    global_config_workflow(config)
    return config

def global_config_workflow(
    wf_config,
):
    # dflow_config, dflow_s3_config
    workflow_config_from_dict(wf_config)

    if os.getenv("DFLOW_DEBUG"):
        dflow.config["mode"] = "debug"
        return None
    # # bohrium configuration
    # if wf_config.get("bohrium_config") is not None:
    #     bohrium_config_from_dict(wf_config["bohrium_config"])

def normalize(data):
    # print(data.get("default_step_config", {}))
    default_step_config = normalize_step_config(data['aesp_config'].get("default_step_config", {}))
    defs = input_config(default_step_config)
    base = Argument("base", dict, defs)
    data = base.normalize_value(data, trim_pattern="_*")
    # not possible to strictly check arguments, dirty hack!
    base.check_value(data, strict=False)
    return data

def print_logo():
     # 打印软件logo
    art_text = text2art("AESP", space=4)
    print(f"{art_text}v{__version__}", end="")
    print("\n")

def get_step_list(step_dict):
# 获取step_list
    step_list = []
    for k, v in step_dict.items():
        for key, value in v.items():
            if isinstance(value, list):
                step_list += value
            else:
                step_list.append(value)
    return step_list

def get_step_dict(wf):
    # steps筛选
    sub_key = 'run'
    step_dict = {k: {} for k in dflow_status}
    idx = 0
    temp_idx = idx
    for phase in dflow_status:
        temp_step_list = []
        steps = wf.query_step(phase=phase, type='Pod')

        steps.sort(key=lambda x: x.startedAt)
        for i, step in enumerate(steps):
            if step.key is not None:
                if sub_key in step.key:
                    temp_step_list.append(step)
                    idx += 1
                    if i != (len(steps)-1):
                        continue
                if idx > temp_idx:
                    step_dict[phase][f"{temp_idx}-{idx-1}"] = temp_step_list
                    temp_step_list = []
                else:
                    step_dict[phase][str(idx)] = step
                    idx += 1
                temp_idx = copy.deepcopy(idx) 
    return step_dict

def get_last_step(wf):
    steps = wf.query_step(type='Pod')
    steps.sort(key=lambda x: x.startedAt)
    for step in reversed(steps):
        if step.key is not None:
            return step
    return None

