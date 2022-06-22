import requests
import sys
import os
import time
import logging
import xmltodict
import json
import shutil
from pathlib import Path

def configRetrieval():
    global config
    work_path = sys.argv[1]
    logging.basicConfig(filename=work_path + '\ocr_change.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s', )
    logging.debug("Starting application. Logger set and file saved to Job Folder")
    logging.info("Following arguments have been received: " + str(sys.argv))
    try:
        config_path = sys.argv[3]
    except:
        logging.error("No configuration path found. Aborting...")
    try:
        with open(config_path+'\ocr_config.xml') as fd:
            config_xml = xmltodict.parse(fd.read())
        config = config_xml['Configuration']
        logging.info("Configuration loaded into variable")
        if config['Logging_Mode'] == "INFO":
            logging.getLogger().setLevel(logging.INFO)
        if config['Logging_Mode'] == "DEBUG":
            logging.getLogger().setLevel(logging.DEBUG)
        if config['Logging_Mode'] == "WARNING":
            logging.getLogger().setLevel(logging.WARNING)
        if config['Logging_Mode'] == "ERROR":
            logging.getLogger().setLevel(logging.ERROR)
    except:
        logging.error("Error while loading Configuration File. Aborting...")
        sys.exit()


def sourcefileRetrieval():
    global lang_srcfolder
    source_list = []
    logging.debug("Retrieving the correct IN folder of the order...")
    in_folder = sys.argv[1]
    path = Path(in_folder)
    order_folder = path.parents[2]
    order_folder = order_folder.joinpath("!_In\\source\\")
    logging.debug("The Order folder is located at "+ str(order_folder))

    dir_list = [f.path for f in os.scandir(order_folder) if f.is_dir()]
    lang_srcfolder = dir_list[0]
    logging.debug("The language source folder of the order is " + str(lang_srcfolder))

    src_files = os.listdir(lang_srcfolder)
    logging.debug("The following files have been identified: "+str(src_files)+" for conversion.")
    for src_file in src_files:
        if os.path.splitext(src_file)[1][1:] in config['Allowed_Formats']['format']: ## check if file extension matches requirements
            file_path = os.path.join(lang_srcfolder, src_file)
            source_list.append(file_path)
    if not source_list:
        print("No source file with an allowed extension found. Aborting...")
        sys.exit()
    return source_list

def sendtoOCR(source_file):
    logging.info("Trying OCR Process for:"+str(source_file))
    language_list = config['LanguageMapping']['Language']
    lang_map_pair = (next(item for item in language_list if item["Plunet"] == sys.argv[2]))
    url_params = {
        "language" : lang_map_pair['Abby'], #must optionalized
        "profile" : config['OCR_Profile'],
        "exportFormat" : config['OCR_Output']
    }
    try:
        with open(source_file, 'rb') as image_file:
            image_data = image_file.read()
    except:
        logging.error("It was not possible to read file: "+str(source_file)+" Aborting...")
        return "Error"
    try:
        resp_ocrpost = requests.post(config['Server']+'/v2/processImage', data=image_data, params=url_params,
                                 auth=(config['ApplicationID'], config['Password']))
        task = json.loads(resp_ocrpost.text)
        logging.debug("A Task has been created: "+str(task))
        return task
    except:
        logging.error("An Error occured. No Task created for file")
        return "Error"


def getTaskStatus(task, source_file):
    x = 0
    url_params = {
        "taskId" : task['taskId']
    }
    while x <= 10:
        resp_status = requests.get(config['Server'] + '/v2/getTaskStatus', params=url_params,
                                auth=(config['ApplicationID'], config['Password']))
        task = json.loads(resp_status.text)
        print(task)
        if task['status'] == "Completed":
            logging.debug("File is ready for downloading for task: "+str(task))
            downloadFile(task, source_file)
            return
        else:
            wait_time = int(task['requestStatusDelay'])/1000
            logging.error("Task is still in status: "+task['status']+". Trying again in "+str(wait_time)+" seconds...")
            time.sleep(wait_time)
            x += 1
    logging.warning("10 tries to retrieve the file were not successful. The current status of the task is: "+task['status']+"Trying next file...")
    return

def downloadFile(task, source_file):
    result_url = task['resultUrls'][0]
    logging.info("Downloading target file")
    sf_name = os.path.basename(source_file)
    sf_namenoext = os.path.splitext(sf_name)[0]

    if result_url is None:
        logging.debug("No download URL found. Skipping file...")
        return
    logging.debug("Storing file to file system")
    resp_file = requests.get(result_url, stream=True)
    file_path = os.path.join(lang_srcfolder, sf_namenoext + "_OCR." + config['OCR_Output'])
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(resp_file.raw, output_file)
    shutil.copy2(file_path, sys.argv[1])  # Good to have the file in the inbox of the job.
    deleteTask(task)

def deleteTask(task):
    url_params = {
        "taskId" : task['taskId']
    }
    try:
        resp_del = requests.post(config['Server'] + '/v2/deleteTask', params=url_params,
                      auth=(config['ApplicationID'], config['Password']))
        logging.debug("Task has been successfully deleted from server.")
    except:
        logging.warning("Error while trying to delete the task.")

def runOCRProcess(source_list):
    tasklist = []
    print (source_list)
    starttime = time.time()

    for sourcefile in source_list:
        task = sendtoOCR(sourcefile)
        if not task == "Error":
            tasklist.append((task, sourcefile))

    logging.debug(str(tasklist))
    elapsedtime = time.time() - starttime
    time.sleep(10 - elapsedtime)

    for (task,sourcefile) in tasklist:
        getTaskStatus(task, sourcefile)


configRetrieval()
source_file_list = sourcefileRetrieval()
runOCRProcess(source_file_list)
logging.info("All tasks finished. Closing application...")


