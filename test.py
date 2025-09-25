from global_config import goes_dict

# for sat in goes_dict:
#     print(goes_dict[sat]['false_colour'])
#     print(goes_dict[sat]['false_diffs'])

for sat in goes_dict:
    for key in goes_dict[sat]['wavelengths']:
        diffs = goes_dict[sat]['wavelengths'][key]['diffs']
        store = goes_dict[sat]['wavelengths'][key]['store']
        print( sat, key, diffs, store)
    # print(goes_dict[sat]['false_colour'])
