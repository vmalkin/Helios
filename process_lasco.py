import mgr_lasco_analyser
import mgr_lasco_enhancer
import global_config
import time
import os

enhanced_folder = global_config.folder_source_images + os.sep + "enhanced_lasco"
analysis_folder = global_config.folder_source_images + os.sep + "analysis_lasco"
processing_start_date = int(time.time() - (86400 * 1))

if os.path.exists(enhanced_folder) is False:
    os.makedirs(enhanced_folder)
if os.path.exists(analysis_folder) is False:
    os.makedirs(analysis_folder)

mgr_lasco_enhancer.wrapper(processing_start_date, storage_folder, enhanced_folder)
mgr_lasco_analyser.wrapper(storage_folder, analysis_folder)