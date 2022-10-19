#!/usr/bin/env python3
import os
import glob
from zipfile import ZipFile
import subprocess
import urllib
import toml

# configure this values
parentDir = "/home/pradeepk/Documents/Tasks/test_github/product2"
axpProductZipPath = "/home/pradeepk/Documents/Tasks/test_github/zips/wso2telcohub-4.1.0.zip"
kmProductZipPath = "/home/pradeepk/Documents/Tasks/test_github/zips/wso2is-5.6.0.zip"
CONF_FILES_DIR = os.getcwd() + "/axp_product_create_script-wso2am-2.5.0-setup"
# configuration end

km_directory = os.path.join(parentDir, "KM")
gw_directory = os.path.join(parentDir, "GATEWAY")

GW_HOME_DIR = None
KM_HOME_DIR = None


def create_product_directories():
    os.mkdir(km_directory)
    os.mkdir(gw_directory)


def unzip_product(zipFilePath, productDir):
    proc = subprocess.Popen(['unzip', zipFilePath, '-d', productDir])
    proc.communicate()
    proc.wait()


def set_product_home_directories():
    global GW_HOME_DIR
    global KM_HOME_DIR
    GW_HOME_DIR = glob.glob(gw_directory + "/*")[0]
    KM_HOME_DIR = glob.glob(km_directory + "/*")[0]


def print_home_dirs():
    print("KM HOME DIR : ", KM_HOME_DIR)
    print("GW HOME DIR : ", GW_HOME_DIR)


def download_from_github():
    repo_url = "https://github.com/Pradeep119/axp_product_create_script/archive/refs/heads/wso2am-2.5.0-setup.zip"
    run_shell(['wget', repo_url])
    run_shell(['unzip', 'wso2am-2.5.0-setup.zip'])


def copy_files_to_location(file_name, product_dir, product, dest_path):
    source_file_path = CONF_FILES_DIR + '/conf_files/' + product + "/" + file_name
    destination_file_path = product_dir + '/' + dest_path
    run_shell(['cp', source_file_path, destination_file_path])


def gw_setup():
    copy_files_to_location("api-manager.xml", GW_HOME_DIR, "am", "/repository/conf")
    copy_files_to_location("axpserver.sh", GW_HOME_DIR, "am", "/bin")
    copy_files_to_location("registry.xml", GW_HOME_DIR, "am", "/repository/conf")
    copy_files_to_location("user-mgt.xml", GW_HOME_DIR, "am", "/repository/conf")
    copy_files_to_location("identity.xml", GW_HOME_DIR, "am", "/repository/conf/identity")
    copy_files_to_location("master-datasources.xml", GW_HOME_DIR, "am", "/repository/conf/datasources")
    download_mysql_connector(GW_HOME_DIR)


def km_setup():
    copy_files_to_location("api-manager.xml", KM_HOME_DIR, "km", "/repository/conf")
    copy_files_to_location("carbon.xml", KM_HOME_DIR, "km", "/repository/conf")
    copy_files_to_location("registry.xml", KM_HOME_DIR, "km", "/repository/conf")
    copy_files_to_location("user-mgt.xml", KM_HOME_DIR, "km", "/repository/conf")
    copy_files_to_location("identity.xml", KM_HOME_DIR, "km", "/repository/conf/identity")
    copy_files_to_location("master-datasources.xml", KM_HOME_DIR, "am", "/repository/conf/datasources")
    download_mysql_connector(KM_HOME_DIR)


def run_shell(cmdArray):
    proc = subprocess.Popen(cmdArray)
    proc.communicate()
    proc.wait()


def download_mysql_connector(packDir):
    mysql_connector_url_v8 = "https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/8.0.30/mysql-connector-java-8.0.30.jar"
    mysql_connector_url_v5 = "https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/5.1.40/mysql-connector-java-5.1.40.jar"
    run_shell(['wget', '-P', packDir + "/repository/components/lib", mysql_connector_url_v8])
    run_shell(['wget', '-P', packDir + "/repository/components/lib", mysql_connector_url_v5])


def main():
    print("starting automation ----")

    create_product_directories()
    unzip_product(axpProductZipPath, gw_directory)
    unzip_product(kmProductZipPath, km_directory)
    set_product_home_directories()
    print_home_dirs()

    # download conf files from github
    download_from_github()

    # setting up packs
    gw_setup()
    km_setup()

    print("process completed!")


if __name__ == "__main__":
    main()
