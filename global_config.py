import os
filesep = os.sep

copyright = 'DunedinAurora.NZ, (c) 2025.'
folder_source_images = 'source'
folder_output_to_publish = 'publish'
solar_wind_database = 'solarwind.db'
report_string = ""
stored_images_folder = "solar_images"

# in metres
astronomical_unit = 150000000000

# in days
carrington_rotation = 27.2753


goes_dict = {
    'primary': {
        'false_colour': folder_source_images + filesep + 'sv_false_x',
        'false_diffs': folder_source_images + filesep + 'sv_diffs_x',
        'wavelengths': {
            '171': {
                'url': 'https://services.swpc.noaa.gov/images/animations/suvi/primary/171/',
                'store': folder_source_images + filesep + 'goes_x_171',
                'diffs': folder_source_images + filesep + 'goes_x_df_171'
            },
            '195': {
                'url': 'https://services.swpc.noaa.gov/images/animations/suvi/primary/195/',
                'store': folder_source_images + filesep + 'goes_x_195',
                'diffs': folder_source_images + filesep + 'goes_x_df_195'
            },
            '284': {
                'url': 'https://services.swpc.noaa.gov/images/animations/suvi/primary/284/',
                'store': folder_source_images + filesep + 'goes_x_284',
                'diffs': folder_source_images + filesep + 'goes_x_df_284'
            }
        }
    },
    'secondary': {
            'false_colour': folder_source_images + filesep + 'sv_false_y',
            'false_diffs': folder_source_images + filesep + 'sv_diffs_y',
            'wavelengths': {
                '171': {
                    'url': 'https://services.swpc.noaa.gov/images/animations/suvi/secondary/171/',
                    'store': folder_source_images + filesep + 'goes_y_171',
                    'diffs': folder_source_images + filesep + 'goes_y_df_171'
                },
                '195': {
                    'url': 'https://services.swpc.noaa.gov/images/animations/suvi/secondary/195/',
                    'store': folder_source_images + filesep + 'goes_y_195',
                    'diffs': folder_source_images + filesep + 'goes_y_df_195'
                },
                '284': {
                    'url': 'https://services.swpc.noaa.gov/images/animations/suvi/secondary/284/',
                    'store': folder_source_images + filesep + 'goes_y_284',
                    'diffs': folder_source_images + filesep + 'goes_y_df_284'
                }
            }
        }
    }

