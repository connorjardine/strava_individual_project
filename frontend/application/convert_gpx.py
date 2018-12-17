def convert_gpx(gpx_list):
    list_dict = []
    for i in gpx_list:
        list_dict += [{'lat': i[0], 'lon': i[1]}]
    return list_dict
