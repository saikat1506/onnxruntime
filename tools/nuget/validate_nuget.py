# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import sys
import os
import zipfile # Available Python 3.2 or higher

def parse_arguments():
    parser = argparse.ArgumentParser(description="ONNX Runtime create nuget spec script",
                                     usage='')
    # Main arguments
    parser.add_argument("--nuget_path", required=True, help="Path containing the Nuget to be validated. Must only contain only one Nuget within this.")
    parser.add_argument("--platforms_supported", required=True, help="Comma separated list (no space). Ex: linux-x64,win-x86,osx-x64")
    
    return parser.parse_args()

def check_exists(path):
    return os.path.exists(path)
   
def is_windows():
    return sys.platform.startswith("win")
   
def check_if_dlls_are_present(platforms_supported, zip_file):
    platforms = platforms_supported.strip().split(",")
    for platform in platforms:
        if platform.startswith("win"):
            path = "runtimes/" + platform + "/native/onnxruntime.dll"
            print('Checking path: ' + path)
            if (not path in zip_file.namelist()):
               print("onnxruntime.dll not found for " + platform)
               print(zip_file.namelist())
               raise Exception("onnxruntime.dll not found for " + platform)

        elif platform.startswith("linux"):
            path = "runtimes/" + platform + "/native/libonnxruntime.so"
            print('Checking path: ' + path)
            if (not path in zip_file.namelist()):
               print("libonnxruntime.so not found for " + platform)
               raise Exception("libonnxruntime.so not found for " + platform)
               
        elif platform.startswith("osx"):
            path = "runtimes/" + platform + "/native/libonnxruntime.dylib"
            print('Checking path: ' + path)        
            if (not path in zip_file.namelist()):
               print("libonnxruntime.dylib not found for " + platform)
               raise Exception("libonnxruntime.dylib not found for " + platform)
               
        else:
            raise Exception("Unsupported platform: " + platform)
            
def main():   
    args = parse_arguments()

    files = os.listdir(args.nuget_path)
    nuget_packages_found_in_path = [i for i in files if i.endswith('.nupkg')]
    if (len(nuget_packages_found_in_path) != 1):
        print('Nuget packages found in path: ')
        print(nuget_packages_found_in_path)
        raise Exception('No Nuget packages / more than one Nuget packages found in the given path.')
    
    nuget_file_name = nuget_packages_found_in_path[0]
    full_nuget_path = os.path.join(args.nuget_path, nuget_file_name)
    
    exit_code = 0
            
    nupkg_copy_name = "NugetCopy" + ".nupkg" 
    zip_copy_name = "NugetCopy" + ".zip"
    zip_file = None

    # Remove any residual files
    if check_exists(nupkg_copy_name):
        os.remove(nupkg_copy_name)
        
    if check_exists(zip_copy_name):
        os.remove(zip_copy_name)
         
    # Do all validations here         
    try: 
        if not is_windows():
            raise Exception('Nuget validation is currently supported only on Windows')
            
        # Make a copy of the Nuget package
        print('Making a copy of the Nuget and extracting its contents') 
        os.system("copy "  + full_nuget_path  + " " + nupkg_copy_name)
        
        # Convert nupkg to zip
        os.rename(nupkg_copy_name, zip_copy_name)
        zip_file = zipfile.ZipFile(zip_copy_name)
        
        # Check if the dlls are present in the Nuget/Zip
        print('Checking if the Nuget contains relevant dlls')
        check_if_dlls_are_present(args.platforms_supported, zip_file)

        # TODO: Add logic to check if Nuget has been signed
        
        print('Nuget validation was successful')
        
    except:
        exit_code = 1
        
    finally:
        print('Cleaning up after Nuget validation')
            
        if zip_file is not None:
            zip_file.close()

        if check_exists(zip_copy_name):
            os.remove(zip_copy_name)

        if exit_code != 0:
            raise Exception('Nuget validation was unsuccessful')
        
if __name__ == "__main__":
    sys.exit(main())