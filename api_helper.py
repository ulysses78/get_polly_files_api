import pandas as pd

def markdown_to_dataframe(md_file):
    device_db = pd.read_table(md_file, sep="|", header=0, skipinitialspace=True).dropna(axis=1, how='all').iloc[1:]
    device_db.columns = device_db.columns.str.strip()
    for number,col in enumerate(device_db):
        device_db[col]=device_db[col].str.strip(' +$')
    return device_db

def convert_db_2_dict(db):

    devices=db

    meta_ls = list(devices['METAINFO'])
    results_dict = {}
    dev0 = ''
    for num,meta in enumerate(meta_ls):
#        print(meta)
#        entry = f'{num}'
        UUID = str(list(devices['UUID'])[num])
        dev = str(list(devices['DEVICE'])[num])
        location = str(list(devices['LOCATION'])[num])
#        location = re.split(r' \(',location)[0]
        sdate = str(list(devices['START DATE'])[num])
        edate = str(list(devices['END DATE'])[num])
        camp = str(list(devices['CAMPAIGN'])[num])

        meta = ''.join(meta)
        meta = '{' + str(meta) + '}'
        meta_dict = eval(meta)
        dev_class = meta_dict['class']
        dev_type = meta_dict['type']
        PID = meta_dict['PID']
        pylarda_camp = meta_dict['pylarda_camp']
        pylarda_system = meta_dict['pylarda_system']
        pylarda_connectorfile = meta_dict['pylarda_connectorfile']
        misc = meta_dict['misc']
        if dev != dev0:
            dev0 = dev
            entry = 0
            results_dict[dev0] = {}
#            results_dict[dev0] = str(dev0)
            results_dict[dev0]['device'] = str(dev0)
            results_dict[dev0]['class'] = dev_class
            results_dict[dev0]['type'] = dev_type
            results_dict[dev0]['pid'] = PID
            results_dict[dev0]['history'] = {}
            results_dict[dev0]['history'][entry] = {}
            results_dict[dev0]['history'][entry]['uuid'] = UUID
            results_dict[dev0]['history'][entry]['location'] = location
            results_dict[dev0]['history'][entry]['startdate'] = sdate
            results_dict[dev0]['history'][entry]['enddate'] = edate
            results_dict[dev0]['history'][entry]['campaign'] = camp
            results_dict[dev0]['history'][entry]['pylarda_camp'] = pylarda_camp
            results_dict[dev0]['history'][entry]['pylarda_system'] = pylarda_system
            results_dict[dev0]['history'][entry]['pylarda_connectorfile'] = pylarda_connectorfile
            results_dict[dev0]['history'][entry]['track_url'] = meta_dict['track_url']
            results_dict[dev0]['history'][entry]['track_pub'] = meta_dict['track_pub']
            results_dict[dev0]['history'][entry]['track_pub_url'] = meta_dict['track_pub_url']
            results_dict[dev0]['history'][entry]['misc'] = misc
        elif dev == dev0:
            entry = entry + 1
            results_dict[dev0]['history'][entry] = {}
            results_dict[dev0]['history'][entry]['uuid'] = UUID
            results_dict[dev0]['history'][entry]['location'] = location
            results_dict[dev0]['history'][entry]['startdate'] = sdate
            results_dict[dev0]['history'][entry]['enddate'] = edate
            results_dict[dev0]['history'][entry]['campaign'] = camp
            results_dict[dev0]['history'][entry]['pylarda_camp'] = pylarda_camp
            results_dict[dev0]['history'][entry]['pylarda_system'] = pylarda_system
            results_dict[dev0]['history'][entry]['pylarda_connectorfile'] = pylarda_connectorfile
            results_dict[dev0]['history'][entry]['track_url'] = meta_dict['track_url']
            results_dict[dev0]['history'][entry]['track_pub'] = meta_dict['track_pub']
            results_dict[dev0]['history'][entry]['track_pub_url'] = meta_dict['track_pub_url']
            results_dict[dev0]['history'][entry]['misc'] = misc

    return results_dict


def device_at_site_timestamp(md_file='',location='all',timestamp='all',device_type='all', device_name='all', campaign='all'):
    #, campaign='all'

#    device_tracking_db=markdown_to_dataframe(md_file)
#    device_tracking_db=markdown_to_dataframe_dict(md_file)
    device_tracking_db=markdown_to_dataframe(md_file=md_file)
    filtered_result=device_tracking_db

    ## check which timestamp-format and convert to YYYY-MM-DD if necessary for filtering the db for dates (between_two_dates)
    if len(str(timestamp)) == 10 and '-' in str(timestamp):
        pass
    elif len(str(timestamp)) == 8 and '-' not in str(timestamp):
        YYYY=timestamp[0:4]
        MM=timestamp[4:6]
        DD=timestamp[6:8]
        timestamp=YYYY+"-"+MM+"-"+DD
    elif len(str(timestamp)) >= 16 and ':' in str(timestamp):
        timestamp_1 = re.split(r':', timestamp)[0]
        timestamp_2 = re.split(r':', timestamp)[1]

        if len(str(timestamp_1)) == 10 and '-' in str(timestamp_1):
            timestamp = [timestamp_1,timestamp_2]
        elif len(str(timestamp_1)) == 8 and '-' not in str(timestamp_1):
            YYYY=timestamp_1[0:4]
            MM=timestamp_1[4:6]
            DD=timestamp_1[6:8]
            timestamp_1=YYYY+"-"+MM+"-"+DD
            YYYY=timestamp_2[0:4]
            MM=timestamp_2[4:6]
            DD=timestamp_2[6:8]
            timestamp_2=YYYY+"-"+MM+"-"+DD

            timestamp = [timestamp_1,timestamp_2]


    ## check for sites
    if str(location) == 'all':
        pass
    else:
        filtered_result = filtered_result.loc[filtered_result.iloc[:,2].str.contains(location, na=False, case=False)]

    ## check for times
    if str(timestamp) == 'all':
        pass
    else:
        if type(timestamp) == str:
            after_start_date = filtered_result["START DATE"] <= timestamp
            before_end_date = filtered_result["END DATE"] >= timestamp
            between_two_dates = after_start_date & before_end_date
            filtered_result = filtered_result.loc[between_two_dates]
        elif type(timestamp) == list:
            before_start_date1 = timestamp[0] <= filtered_result["START DATE"]
            before_start_date2 = timestamp[1] <= filtered_result["START DATE"]
            before_start_date = before_start_date1 & before_start_date2
            before_start_date = ~before_start_date ## negate boolean values
            after_end_date1 = filtered_result["END DATE"] <= timestamp[0]
            after_end_date2 = filtered_result["END DATE"] <= timestamp[1]
            after_end_date = after_end_date1 & after_end_date2
            after_end_date = ~after_end_date ## negate boolean values
            between_two_dates = before_start_date & after_end_date
            filtered_result = filtered_result.loc[between_two_dates]

    ## check for device_types
    if str(device_type)=='all':
        pass
    else:
        filtered_result = filtered_result.loc[filtered_result.iloc[:,6].str.contains(device_type, na=False, case=False)]

    ## check for device_names
    if str(device_name)=='all':
        pass
    else:
        filtered_result = filtered_result.loc[filtered_result.iloc[:,1].str.contains(device_name, na=False, case=False)]

    ## check for campaigns
    if str(campaign)=='all':
        pass
    else:
        filtered_result = filtered_result.loc[filtered_result.iloc[:,5].str.contains(campaign, na=False, case=False)]

    return filtered_result

