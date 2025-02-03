import flask
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import subprocess
import json
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

input_file = None
app = flask.Flask(__name__, static_url_path='', static_folder='../frontend/build')

CORS(app, origins=['http://localhost:3000'])

@app.route("/test", methods={'GET'})
def test():
    return "Success!"

@app.route("/", defaults={'path': ''})
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/input', methods=['POST'])
def upload_files():
    try:
        upload_dir = os.path.join(os.getcwd(), 'inputfile')
        os.makedirs(upload_dir, exist_ok=True)

        # Delete all files in upload_dir
        for file_name in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, file_name)
            if os.path.isfile(file_path):  # Ensure it's a file before deleting
                os.remove(file_path)

        uploaded_files = request.files.getlist('files') 
        file_names = []

        for uploaded_file in uploaded_files:
            if uploaded_file.filename != '':
                file_path = uploaded_file.filename.split("/", 1)[-1]
                file_path = os.path.join(upload_dir, file_path)
                uploaded_file.save(file_path)
                file_names.append(uploaded_file.filename)


        current_dir = os.getcwd()
        input_dir = os.path.dirname(current_dir) + "/inputfile"

        # Copy files from upload_dir to input_dir
        for file_name in os.listdir(upload_dir):
            source_path = os.path.join(upload_dir, file_name)
            destination_path = os.path.join(input_dir, file_name)
            if os.path.isfile(source_path):  # Ensure it's a file before copying
                shutil.copy(source_path, destination_path)



        return {"message": "Files uploaded successfully", "files": file_names}, 200
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

def run_r_script(output_path_fol):
    
    try:
        process = subprocess.run(
            ['Rscript', output_path_fol],
            capture_output=True,  # Capture both stdout and stderr
            text=True
        )
        
        stdout_output = process.stdout.strip()
        stderr_output = process.stderr.strip()

        logging.info(f"Return code: {process.returncode}")
        logging.info(f"STDOUT:\n{stdout_output}")
        logging.error(f"STDERR:\n{stderr_output}")

        # Include both stdout and stderr even if execution was successful
        return jsonify({
            "status": "success" if process.returncode == 0 else "error",
            "stdout": stdout_output,
            "warnings": stderr_output.split("\n") if stderr_output else []  # Capture all warning lines
        }), 200 if process.returncode == 0 else 400

    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



def convert_to_boolean(x):
    if x == "True" or x is True:
        return "TRUE"
    elif x == "False" or x=="FALSE" or x is False:
        return "FALSE"
    elif x is None:  # Replace None (null) with an empty string
        return ""
    return x  

# Apply the function to each item in the dictionary

def getLogFile(output_path, output_file_name):

    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    log_dir = os.path.join(output_path, "logs")

    print(output_path)
    print(log_dir)

    # Check if the log folder exists; if not, create it
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the path for the new CSV file
    log_file_path = os.path.join(log_dir, f"{output_file_name}_logs.csv")

    # Create an empty CSV file
    with open(log_file_path, mode='w', newline='') as csv_file:
        pass

    return log_file_path

@app.route('/config', methods=['POST'])
def config():  
    try:
        data={}
        if request.method == 'POST':

            data = request.data.decode('utf-8') 
            data_json = json.loads(data)

            day_night_value = data_json["day_night"]
            time_zone_value = data_json["time_zone"]

            current_dir = os.getcwd()
            input_dir = os.path.dirname(current_dir) + "/inputfile"

            # if input_file is not None:
            #     input_file_name = input_file
            # else:
            #     input_file_name = data_json['input_file_name']    

            # input_file_name = os.getcwd()
            # input_file_name = os.path.dirname(input_file_name)+"/inputfile/input.csv"
            # print(input_file_name)

            data_json = {key: convert_to_boolean(value) for key, value in data_json.items()}
            output_file_name =data_json['output_file_name']
            windows1_value = 5 if (data_json['windows1_value']=="0" or data_json['windows1_value']=="") else data_json['windows1_value']
            windows2_value = 9 if (data_json['windows2_value']=="0" or data_json['windows2_value']=="") else data_json['windows2_value']
            windows3_value = 3600 if (data_json['windows3_value']=="0" or data_json['windows3_value']=="") else data_json['windows3_value']
            auto_calibration_value =data_json['auto_calibration_value'].upper()
            
            pa_enmo_value =data_json['pa_enmo'].upper()
            pa_mad_value =data_json['pa_mad'].upper()
            pa_hfen_value =data_json['pa_hfen'].upper()
            pa_en_value =data_json['pa_en'].upper()
            pa_actilife_value =data_json['pa_actilife'].upper()
            proc_chunk_size_value =data_json['proc_chunk_size_value']
            sleep_analysis_value =data_json['sleep_analysis_value']
            time_window_value =data_json['time_window_value'] if data_json['time_window_value'] != "" else "MM"
            analytical_strategy_value = 1 if data_json['analytical_strategy_value'] in (None, 0, "") else data_json['analytical_strategy_value']
            startofperiod =data_json['startofperiod']
            endOfperiod =data_json['endOfperiod']
            q_win_v1_value =data_json['q_win_v1_value']
            q_win_v2_value =data_json['q_win_v2_value']
            day_crit_value =data_json['day_crit']
            analytical_window_value =data_json['analytical_window_value']
            device_value =data_json['device_value']
            position_value =data_json['position_value']
            age_group_value =data_json['age_group_value']
            cutpoints_value =data_json['cutpoints_value']
            mvpathreshold = "c(1, 5, 10)" if cutpoints_value[1]== "c(0,0,0)" else cutpoints_value[1]
            detection_metric_value =data_json['detection_metric_value']
            boutTolInaAct_value = int(data_json['bout_tollorance_inactive']) if data_json['bout_tollorance_inactive'] != "-" else 0
            boutTolLimAct_value = int(data_json['bout_tollorance_lowactive']) if data_json['bout_tollorance_lowactive'] != "-" else 0
            boutTolMVPA_value = int(data_json['bout_tollorance_mvpa']) if data_json['bout_tollorance_mvpa'] != "-" else 0
            durInaAct1_value = int(data_json['duration_inactive1']) if data_json['duration_inactive1'] != "-" else 0
            durInaAct2_value = int(data_json['duration_inactive2']) if data_json['duration_inactive2'] != "-" else 0
            durInaAct3_value = int(data_json['duration_inactive3']) if data_json['duration_inactive3'] != "-" else 0            
            durLimAct1_value = int(data_json['duration_lowactive1']) if data_json['duration_lowactive1'] != "-" else 0
            durLimAct2_value = int(data_json['duration_lowactive2']) if data_json['duration_lowactive2'] != "-" else 0
            durMVPA1_value = int(data_json['duration_mvpa1']) if data_json['duration_mvpa1'] != "-" else 0
            durMVPA2_value = int(data_json['duration_mvpa2']) if data_json['duration_mvpa2'] != "-" else 0
            time_threshold_value=data_json['time_threshold_value']
            
            angle_threshold_value = 0 if data_json.get('angle_threshold_value')=="" else data_json['angle_threshold_value']
            hasib_value = "vanHees2015" if data_json['hasib'] == "" or data_json['hasib'] is None else data_json['hasib']
            ignore_non_wear_time_value =data_json['ignore_non_wear_time_value'].upper()
            activityreport =data_json['activityreport']
            sleepreport =data_json['sleepreport']
            visualisation =data_json['visualisation']
            epochlevel =data_json['epochlevel']
            overwrite = data_json['overwrite']

            ## Additional conditions
            day_night_value_con = "c(1,2,3,4,5)"#day_night_value_con = "c(1,2,3,4,5)" if day_night_value == 24 else "c(1,2,5)"
            current_dir = os.getcwd()
            current_dir = os.path.dirname(current_dir)
            output_dir = os.path.join(current_dir, "output")
            output_path = os.path.join(output_dir, f"{output_file_name}.R")
            output_path_fol = os.path.join(current_dir, "backend")
            output_path_dir = os.path.join(output_path_fol, "output")
            output_path_file = os.path.join(output_path_dir, f"{output_file_name}.R")
            
            log_file_path = getLogFile(output_dir, output_file_name)
            rScript = f"""
    options(repos = c(CRAN = "https://cloud.r-project.org"))
    if (!requireNamespace("GGIR", quietly = TRUE)) {{
        install.packages("GGIR")
    }}
    library(GGIR)
    GGIR(
        #################################################################################
        #  Part 0 - General                                                             #
        #################################################################################
        datadir = "{input_dir}",
        outputdir = "{output_dir}",
        do.parallel = FALSE,
        mode = {day_night_value_con},
        studyname = "{output_file_name}",
        desiredtz = "{time_zone_value}",
        overwrite = {overwrite},
        storefolderstructure = TRUE,
        idloc = 2,
        print.filename = TRUE,

        #################################################################################
        # Part 1 - Raw data processing/data quality/extracts features/nonwear detection #
        #################################################################################
        windowsizes = c({windows1_value},{windows2_value},{windows3_value}),
        do.cal = {auto_calibration_value},
        do.enmo = {pa_enmo_value},
        do.enmoa = FALSE,

        #################################################################################
        # Part 2 - data quality and descriptives                                        #
        #################################################################################
        strategy = {analytical_strategy_value},
        includedaycrit = {day_crit_value},
        includedaycrit.part5 = 6,
        mvpathreshold = c({mvpathreshold}),
        mvpadur = c({durInaAct1_value},{durInaAct2_value},{durInaAct3_value}),
        boutcriter = {boutTolInaAct_value},

        #################################################################################
        # Part 3 & 4 - sleep                                                            #
        #################################################################################
        do.anglez = TRUE,
        do.anglex = FALSE,
        do.angley = FALSE,
        anglethreshold = {angle_threshold_value},
        includenightcrit = 16,
        HASIB.algo = "{hasib_value}",
        do.zcx = TRUE, do.zcy = TRUE, do.zcz = TRUE,
        acc.metric = "ENMO",
        do.sibreport = TRUE,
        sibreport = c(),
        def.noc.sleep = c(1),
        loglocation = "{log_file_path}",

        #################################################################################
        # Part 5 - full-day time-use analysis                                           #
        ################################################################################# 

        frag.metrics = "all",
        part5_agg2_60seconds = TRUE,
        threshold.lig = {cutpoints_value[0]}, threshold.mod = {cutpoints_value[1]}, threshold.vig = {cutpoints_value[2]},
        boutdur.in = c({durInaAct1_value},{durInaAct2_value},{durInaAct3_value}), boutdur.lig = c({durLimAct1_value},{durLimAct2_value}), boutdur.mvpa = c({durMVPA1_value},{durMVPA2_value}),
        boutcriter.in = {boutTolLimAct_value},boutcriter.lig = {boutTolMVPA_value},boutcriter.mvpa = {boutTolInaAct_value},
        timewindow = c("{time_window_value}"),
        do.report = c(2,5),
        visualreport = {visualisation},
        viewingwindow = 1,
        excludefirstlast.part5 = FALSE,
        dofirstpage = TRUE,
        backup.cal.coef = c(),
        IVIS_windowsize_minutes = 60,
        constrain2range = TRUE,
        window.summary.size = 10,
        save_ms5rawlevels = TRUE,
        save_ms5raw_format = "csv",
        save_ms5raw_without_invalid = TRUE,
        
        #################################################################################
        # Generic Setting                                                               #
        ################################################################################# 
        do.imp = TRUE,
        print.summary = TRUE,
        do.visual = TRUE,
        
        #################################################################################
        # Others                                                                        #
        #################################################################################

        do.mad={pa_mad_value},
        do.hfen={pa_hfen_value},
        do.en={pa_en_value},
        do.neishabouricounts = {pa_actilife_value},
        chunksize={proc_chunk_size_value},
        hrs.del.start = {startofperiod},
        hrs.del.end = {endOfperiod},
        maxdur = 0,
        qwindow=c({q_win_v1_value},{q_win_v2_value}),
        bout.metric = 6,
        closedbout=FALSE,
        M5L5res = 10,
        winhr = c(1,5),
        ilevels = c(0, 50, 100, 150, 200, 250, 300, 350, 700, 8000),
        excludefirstlast = TRUE,
        iglevels = TRUE,
        MX.ig.min.dur = 1,
        qlevels = c( 960/1440, 1320/1440, 1380/1440, 1410/1440, 1425/1440, 1435/1440),
        #timetreshold = {time_threshold_value},
        #ignorenonwear = {ignore_non_wear_time_value},
        outliers.only = FALSE,
        criterror = 4,
        epochvalues2csv = TRUE
        )
        """
            
        print("R Script has been generated :" + output_file_name)
        
        try:
            # Save R script to a file
            with open(output_path, 'w') as f:
                f.write(rScript)

            # Run the R script
            return run_r_script(output_path)  

        except Exception as e:
            logging.error(f"Exception in /config route: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }), 500
    
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return {"error": "Invalid JSON format in request body."}, 400
    except KeyError as e:
        print(f"Missing Key Error: {e}")
        return {"error": f"Missing required key in request: {str(e)}"}, 400
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
        return {"error": f"File not found: {str(e)}"}, 500
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)