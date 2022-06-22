# Plunet-ApplicationManager---Abby-OCR-Script
Application written to OCR PDF and TIF documents to be used by Plunet BusinessManager module ApplicationManager

## Short Introduction

Original Use Case: [https://community.plunet.com/t/83hkkh6/recommendations-for-ocr-conversion-tasks](https://community.plunet.com/t/83hkkh6/recommendations-for-ocr-conversion-tasks)

Definition: Having an option to create a job that converts an image-based document using OCR in an editable format. Job shall send data to [https://www.abbyy.com/de/cloud-ocr-sdk/](https://www.abbyy.com/de/cloud-ocr-sdk/)

## Application Requirements:

  1. General Requirements

- It shall be possible to configure the specific parameters for the Cloud API:
  - Server, user name, password
  - Profile type
  - Output file type
  - Allowed image formats
  - Language Mapping for Source Language in  Plunet and recognized language in Abby Cloud OCR
- Workflow
  - Starting the application
    - application shall be able to receive source language parameter with ApplicationManager call
    - application shall be able to receive storing location of configuration file with ApplicationManager call
  - Preparation
    - Create a log file in Job \_IN Folder
    - Retrieve configuration
    - Retrieve parameters passed along by application manager
  - Getting the relevant files
    - retrieve source files from Order Source Level (language folder)
    - identify files with the allowed image format
  - Create a task in Abby Cloud OCR with the parameters set in the configuration file PLUS the passed recognition language from ApplicationManager plus files
  - Check for task completion
  - Upon Completion, download files
    - rename completed file to originalfilename\_OCR.OUTPUTFILETYPE
    - store completed file in Order Source Level (language folder)
    - store completed file in \_IN Folder of the Job
  - Delete task in Abby
- Additional requirements
  - it shall be possible to set a debugging level in the config file
  - it shall be possible to have multiple source files
- Currently not implemented:
  - CHECK FILE functionality should be possible since log file is created in Job folder - no option to test yet

## Abby Cloud OCR API

API Documentation: [https://support.abbyy.com/hc/en-us/sections/360004931659-API-v2-JSON-version-](https://support.abbyy.com/hc/en-us/sections/360004931659-API-v2-JSON-version-)

Code Samples: [https://support.abbyy.com/hc/en-us/sections/360004895259-Code-samples](https://support.abbyy.com/hc/en-us/sections/360004895259-Code-samples)


## Solution
### Executable File and Config File

To be found in dist folder
Application was converted into .exe with PYInstaller

### Source
abby_ocr.py (Application written in Python 3.8)

### Configuration
ocr_config.xml (ApplicationID and Password must be set - can be retrieved from ABBY)
Executable and configuration file shall be stored on server where Plunet runs.

#### Further details to be found in PDF
https://github.com/SufiSR/Plunet-ApplicationManager---Abby-OCR-Script/blob/main/Abby%20Cloud%20OCR%20Script%20with%20ApplicationManager_official.pdf

## Testing the integration

Create a project and put a pdf or tif file into the language source folder of the order. Create an Abby OCR Job and run it.

Due to the configuration, it would make sense to choose English as the source language.

Sample File can be obtained from Abby OCR Documentation page.
