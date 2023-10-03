from core_tools.data.SQL.connect import set_up_remote_storage
from core_tools.data.gui.qml.data_browser import data_browser
from core_tools.data.ds.data_set import load_by_id, load_by_uuid
from core_tools.data.ds.ds2xarray import ds2xarray
from qtutils.analysis.mgr_utils import calc_mob_dens, calc_dens_mob_Hall_effect
import json
from datetime import datetime


# set_up_remote_storage(server, port, user, passwd, dbname, project, set_up, sample)
setup = 'any'
project = 'any'
sample = 'any'

# set_up_remote_storage('131.180.205.81', 5432, 'nicoh', 'hendrickx', 'veldhorst_data', project, setup, sample)
set_up_remote_storage('131.180.205.81', 5432, 'scappucci_lab', 'Scappucci!', 'veldhorst_data', project, setup, sample)

# data_browser()

def load_ds(uuid, print_info=True):
    set_up_remote_storage('131.180.205.81', 5432, 'scappucci_lab', 'Scappucci!', 'veldhorst_data', project, setup, sample)
    ds = load_by_uuid(uuid)
    if print_info:
        ts = ds._data_set__data_set_raw.UNIX_start_time
        ts_str = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        te = ds._data_set__data_set_raw.UNIX_stop_time
        te_str = datetime.utcfromtimestamp(te).strftime('%Y-%m-%d %H:%M:%S')
        delta_t = te - ts
        print(f'{ds.set_up} | sample: {ds.sample_name} | start : {ts_str} | measurment time: {int(delta_t/60)} min.')
        print('Measurement name: ',ds.name)
    return ds2xarray(ds)

figsize = [10,7]


def get_param_val(ds, param):
    return json.loads(ds.attrs['snapshot'])['station']['parameters'][param]['value']

def get_instr_param_val(ds, instrument, param):
    return json.loads(ds.attrs['snapshot'])['station']['instruments'][instrument]['parameters'][param]['value']

def print_info(ds):
    params = ds.snapshot['station']['instruments']['gates']['parameters']
    sweep_params = ds.m1.x.label.split()
    print(f'\n\nid = {ds.exp_id}')
    print(f'uuid = {ds.exp_uuid}')
    for key in params:
        # print(type(key))
        ds.m1.x.label.split()
        if params[key]['value']!=0 and key!='IDN' and (key not in sweep_params):
            print(f'{key}\t = {round(params[key]["value"])} {params[key]["unit"]}',)