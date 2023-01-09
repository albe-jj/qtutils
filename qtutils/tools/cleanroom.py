import requests
import datetime
import pytz
import time
import pandas as pd


json_data = {
        'selected_subs': [],
        'reservation': {
            'id': 0,
            'equipment_id': 0,
            'parent_reservation': None,
            'parent_reservation_id': None,
            'sub_equipment_reservation': False,
            'selected_sub': None,
        }
}


albo_json = {
    'project_number': {
                'display_value': 'Technische Universiteit Delft (TUD)/Scappucci Lab/Scappucci123/Scappucci Dummy code',
                'organisation_id': 6,
                'department_id': 76,
                'number': 'Scappucci123',
                'name': 'Scappucci Dummy code',
                'blocked': False,
                'id': 36,
                'start_date': '2021-11-30',
                'end_date': None,
            },
    'type_data': None,
    'notes': '',
    'public_notes': '',
    'is_own': True,
    'user': {
        'id': 682,
        'full_name': 'Alberto Tosato',
        'given_name': 'Alberto',
    },
}

json_data['reservation'].update(albo_json)


instruments = {
    'MBaja' : "89",
    'QTaja' : "90",
    'ALD' : "96",
    'AFM': "88",
    'temescal': '231'
    
    
}

holder_BW0177 = {
    'A':'171',
    'B':'172',
    'C':'173',
    'D':'174',
}

def time_to_tz_naive(t, tz_in, tz_out):
    return tz_in.localize(t).astimezone(tz_out)
    
def book_ebeam(holder_id, PHPSESSID, personal_data, ebpg_start, ebpg_end, holder_start, holder_end):
    ebpg_start = time_to_tz_naive(ebpg_start, pytz.timezone('Europe/Berlin'), pytz.utc)
    ebpg_end = time_to_tz_naive(ebpg_end, pytz.timezone('Europe/Berlin'), pytz.utc)
    holder_start = time_to_tz_naive(holder_start, pytz.timezone('Europe/Berlin'), pytz.utc)
    holder_end = time_to_tz_naive(holder_end, pytz.timezone('Europe/Berlin'), pytz.utc)
#     for i in [ebpg_start, ebpg_end, holder_start, holder_end]:
#         print(i)
    cookies = {
        'PHPSESSID': PHPSESSID,
        'SIDEBAR_COLLAPSED_V2': 'true',
    }

    headers = {
        'authority': 'nis.nanolabnl.nl',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,it;q=0.7',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'PHPSESSID=2ivva9mdnf5vs1dorcuv6kq8at; SIDEBAR_COLLAPSED_V2=true',
        'dnt': '1',
        'origin': 'https://nis.nanolabnl.nl',
        'referer': 'https://nis.nanolabnl.nl/equipment/overview/'+ holder_id,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'validate': 'false',
    }

    json_data = {
        'selected_subs': [],
        'sub_start_date_time': holder_start.strftime('%Y-%m-%dT%XZ'),
        'sub_end_date_time': holder_end.strftime('%Y-%m-%dT%XZ'),
        'reservation': {
            'id': 0,
            'equipment_id': 0,
            'parent_reservation': None,
            'parent_reservation_id': None,
            'sub_equipment_reservation': False,
            'selected_sub': None,
            'start_date_time': ebpg_start.strftime('%Y-%m-%dT%XZ'), #ebpg slot time start
            'end_date_time': ebpg_end.strftime('%Y-%m-%dT%XZ'),
#             'project_number': {
#                 'display_value': 'Technische Universiteit Delft (TUD)/Scappucci Lab/Scappucci123/Scappucci Dummy code',
#                 'organisation_id': 6,
#                 'department_id': 76,
#                 'number': 'Scappucci123',
#                 'name': 'Scappucci Dummy code',
#                 'blocked': False,
#                 'id': 36,
#                 'start_date': '2021-11-30',
#                 'end_date': None,
#             },
#             'type_data': None,
#             'notes': '',
#             'public_notes': '',
#             'is_own': True,
#             'user': {
#                 'id': 682,
#                 'full_name': 'Alberto Tosato',
#                 'given_name': 'Alberto',
#             },

        },
    }
        
    json_data['reservation'].update(personal_data)
    
    link = f'https://nis.nanolabnl.nl/api/equipment/{holder_id}/reservation'
    response = requests.post(link, params=params, cookies=cookies, headers=headers, json=json_data)
    
    return response



def book_ebeam_multi_stage(stages, date, personal_data, PHPSESSID):
    for idx, i in enumerate(stages):

        ebpg_start = pd.to_datetime(date + ' 22:00') + datetime.timedelta(minutes=30 * idx)
        ebpg_end = ebpg_start + datetime.timedelta(minutes=30)
        holder_start = pd.to_datetime(date + ' 16:00')
        holder_end = holder_start + datetime.timedelta(hours=16)

        holder_id = holder_BW0177[i]

        r = book_ebeam(holder_id, PHPSESSID, personal_data, ebpg_start, ebpg_end, holder_start, holder_end)

        if r.status_code == 200:
            print(f'reseration for holder {i} done')
        else:
            print(f'reseration for holder {i} failed')
            print(r.text)


def book_instr(PHPSESSID, personal_data, instr, start, end):
    instr_id = instruments[instr]
    start = time_to_tz_naive(start, pytz.timezone('Europe/Berlin'), pytz.utc)
    end = time_to_tz_naive(end, pytz.timezone('Europe/Berlin'), pytz.utc)
    
    
    cookies = {
        'PHPSESSID': PHPSESSID,
        'SIDEBAR_COLLAPSED_V2': 'true',
    }

#     headers = {
#         'authority': 'nis.nanolabnl.nl',
#         'accept': 'application/json, text/plain, */*',
#         'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,it;q=0.7',
#         'dnt': '1',
#         'origin': 'https://nis.nanolabnl.nl',
#         'referer': 'https://nis.nanolabnl.nl/equipment/overview/89',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
#         'sec-ch-ua-mobile': '?1',
#         'sec-ch-ua-platform': '"Android"',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-origin',
#         'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36',
#     }
    headers = {
        'authority': 'nis.nanolabnl.nl',
        'accept': 'application/json, text/plain, /',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'PHPSESSID=jdo0i1p99n1hfq9j9k1vc7pmh3; SIDEBAR_COLLAPSED_V2=true',
        'dnt': '1',
        'origin': 'https://nis.nanolabnl.nl',
        'referer': 'https://nis.nanolabnl.nl/equipment/overview/96',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }


    params = {
        'validate': 'false',
    }

    json_data = {
        'selected_subs': [],
        'sub_start_date_time': '2022-07-12T09:00:00Z',
        'sub_end_date_time': '2022-07-12T11:00:00Z',
        'reservation': {
            'id': 0,
            'equipment_id': 0,
            'parent_reservation': None,
            'parent_reservation_id': None,
            'sub_equipment_reservation': False,
            'selected_sub': None,
            'start_date_time':  start.strftime('%Y-%m-%dT%XZ'),
            'end_date_time': end.strftime('%Y-%m-%dT%XZ'),
'project_number': {
            'display_value': 'Technische Universiteit Delft (TUD)/Veldhorst Lab/Veldhorst123/Veldhorst Dummy code',
            'organisation_id': 6,
            'department_id': 80,
            'number': 'Veldhorst123',
            'name': 'Veldhorst Dummy code',
            'blocked': False,
            'id': 40,
            'start_date': '2021-11-30',
            'end_date': None,
        },
        'type_data': None,
        'notes': '',
        'public_notes': '',
        'is_own': True,
        'user': {
            'id': 677,
            'full_name': 'Hanifa Tidjani',
            'given_name': 'Hanifa',
        },
        },
    }
    
    json_data['reservation'].update(personal_data)
#     print(json_data['reservation'])
    link = f'https://nis.nanolabnl.nl/api/equipment/{instr_id}/reservation'
    response = requests.post(link, params=params, cookies=cookies, headers=headers, json=json_data)
    
    if response.status_code == 200:
        print(f'reseration for instr {instr} done')
    else:
        print(f'reseration for instr {instr} failed')
        print(response.text)
    return response
