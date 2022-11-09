#!/usr/bin/env python3
import os
import glob
from zipfile import ZipFile
import subprocess
import urllib
import toml

# configure this values
parentDir = "/home/pradeepk/Documents/Tasks/base_prodcut_tasks/script-for-410/pack_generate_try4/product"
axpProductZipPath = "/home/pradeepk/Documents/Tasks/base_prodcut_tasks/script-for-410/pack_generate_try4/wso2am-4.1.0.zip"
kmProductZipPath = "/home/pradeepk/Documents/Tasks/base_prodcut_tasks/script-for-410/pack_generate_try4/wso2is-5.11.0.zip"
dbUsername = 'root'
dbPassword = 'root123'
apiMgtDb = 'test_apimgtdb'
sharedDb = 'test_shareddb'
userStoreDb = 'test_userstoredb'
WSO2TELCO_DEP_DB = 'test_proddepdb'
ACTIVITI_DB = 'test_activitidb'
WSO2TELCO_RATE_DB = 'test_rateDb'
WSO2AM_STATS_DB = 'test_apistatsdb'
# configuration end


kmDirectory = os.path.join(parentDir, "KM")
tmDirectory = os.path.join(parentDir, "TM")
gwDirectory = os.path.join(parentDir, "GATEWAY")
cpDirectory = os.path.join(parentDir, "CP")

GW_HOME_DIR = None
TM_HOME_DIR = None
CP_HOME_DIR = None
KM_HOME_DIR = None


def createProductDirectories():
    os.mkdir(kmDirectory)
    os.mkdir(tmDirectory)
    os.mkdir(gwDirectory)
    os.mkdir(cpDirectory)


def unzipProduct(zipFilePath, productDir):
    proc = subprocess.Popen(['unzip', zipFilePath, '-d', productDir])
    proc.communicate()
    proc.wait()


def setProductHomeDirectories():
    global TM_HOME_DIR
    global GW_HOME_DIR
    global CP_HOME_DIR
    global KM_HOME_DIR
    TM_HOME_DIR = glob.glob(tmDirectory + "/*")[0]
    GW_HOME_DIR = glob.glob(gwDirectory + "/*")[0]
    CP_HOME_DIR = glob.glob(cpDirectory + "/*")[0]
    KM_HOME_DIR = glob.glob(kmDirectory + "/*")[0]


def printHomeDirs():
    print("TM HOME DIR : ", TM_HOME_DIR)
    print("KM HOME DIR : ", KM_HOME_DIR)
    print("GW HOME DIR : ", GW_HOME_DIR)
    print("CP HOME DIR : ", CP_HOME_DIR)


def tmSetup():
    runShell(['chmod', '777', TM_HOME_DIR + "/bin/profileSetup.sh", TM_HOME_DIR + "/bin/axpserver.sh"])
    runShell(['cp', TM_HOME_DIR + "/repository/deployment/server/webapps/internal#data#v1.war", TM_HOME_DIR])
    runShell(['sh', TM_HOME_DIR + "/bin" + "/profileSetup.sh", '-Dprofile=traffic-manager'])
    runShell(['mv', TM_HOME_DIR + "/internal#data#v1.war", TM_HOME_DIR + "/repository/deployment/server/webapps/"])
    runShell(['rm', '-rf', TM_HOME_DIR + "/repository/conf/deployment.toml"])
    runShell(
        ['mv', TM_HOME_DIR + "/repository/conf/deployment_TM.toml", TM_HOME_DIR + "/repository/conf/deployment.toml"])

    downloadMysqlConnector(TM_HOME_DIR)

    data = toml.load(TM_HOME_DIR + "/repository/conf/deployment.toml")
    updateDBToml(data, 'apim_db', apiMgtDb)
    updateDBToml(data, 'shared_db', sharedDb)
    f = open(TM_HOME_DIR + "/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()


def gwSetup():
    runShell(['chmod', '777', GW_HOME_DIR + "/bin/profileSetup.sh", GW_HOME_DIR + "/bin/axpserver.sh"])
    runShell(['cp', GW_HOME_DIR + "/repository/deployment/server/webapps/internal#data#v1.war", GW_HOME_DIR])
    runShell(['sh', GW_HOME_DIR + "/bin" + "/profileSetup.sh", '-Dprofile=gateway-worker'])
    runShell(['mv', GW_HOME_DIR + "/internal#data#v1.war", GW_HOME_DIR + "/repository/deployment/server/webapps/"])
    runShell(['rm', '-rf', GW_HOME_DIR + "/repository/conf/deployment.toml"])
    runShell(
        ['mv', GW_HOME_DIR + "/repository/conf/deployment_GW.toml", GW_HOME_DIR + "/repository/conf/deployment.toml"])

    downloadMysqlConnector(GW_HOME_DIR)

    data = toml.load(GW_HOME_DIR + "/repository/conf/deployment.toml")
    updateDBToml(data, 'shared_db', sharedDb)
    f = open(GW_HOME_DIR + "/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    # updateDatasourceDbToml('WSO2TELCO_DEP_DB', GW_HOME_DIR, WSO2TELCO_DEP_DB)


def controlPlaneSetup():
    runShell(['chmod', '777', CP_HOME_DIR + "/bin/profileSetup.sh", CP_HOME_DIR + "/bin/axpserver.sh"])
    runShell(['cp', CP_HOME_DIR + "/repository/deployment/server/webapps/internal#data#v1.war", CP_HOME_DIR])
    runShell(['sh', CP_HOME_DIR + "/bin" + "/profileSetup.sh", '-Dprofile=control-plane'])
    runShell(['mv', CP_HOME_DIR + "/internal#data#v1.war", CP_HOME_DIR + "/repository/deployment/server/webapps/"])

    runShell(['rm', '-rf', CP_HOME_DIR + "/repository/conf/deployment.toml"])
    runShell(['mv', CP_HOME_DIR + "/repository/conf/deployment_CP.toml",
              CP_HOME_DIR + "/repository/conf/deployment.toml"])

    downloadMysqlConnector(CP_HOME_DIR)

    data = toml.load(CP_HOME_DIR + "/repository/conf/deployment.toml")
    updateDBToml(data, 'apim_db', apiMgtDb)
    updateDBToml(data, 'shared_db', sharedDb)
    updateDBToml(data, 'user', userStoreDb)
    f = open(CP_HOME_DIR + "/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    # updateDatasourceDbToml('WSO2TELCO_DEP_DB', CP_HOME_DIR, WSO2TELCO_DEP_DB)
    # updateDatasourceDbToml('ACTIVITI_DB', CP_HOME_DIR, ACTIVITI_DB)
    # updateDatasourceDbToml('WSO2TELCO_RATE_DB', CP_HOME_DIR, WSO2TELCO_RATE_DB)
    # updateDatasourceDbToml('WSO2AM_STATS_DB', CP_HOME_DIR, WSO2AM_STATS_DB)


def kmSetup():
    downloadKeyManagerConnector(KM_HOME_DIR)

    runShell(['rm', '-rf', KM_HOME_DIR + "/repository/conf/deployment.toml"])
    runShell(
        ['mv', TM_HOME_DIR + "/repository/conf/deployment_KM.toml", KM_HOME_DIR + "/repository/conf/deployment.toml"])

    data = toml.load(KM_HOME_DIR + "/repository/conf/deployment.toml")
    updateDBToml(data, 'identity_db', apiMgtDb)
    updateDBToml(data, 'shared_db', sharedDb)
    updateDBToml(data, 'apim_db', apiMgtDb)
    updateDBToml(data, 'user', userStoreDb)
    f = open(KM_HOME_DIR + "/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    downloadMysqlConnector(KM_HOME_DIR)


def runShell(cmdArray):
    proc = subprocess.Popen(cmdArray)
    proc.communicate()
    proc.wait()


def downloadMysqlConnector(packDir):
    #if you using openjdk 8 use this link istead of mysql connector 8 https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/5.1.40/mysql-connector-java-5.1.40.jar
    mysqlConnectorUrl = "https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/8.0.30/mysql-connector-java-8.0.30.jar"
    runShell(['wget', '-P', packDir + "/lib", mysqlConnectorUrl])


def downloadKeyManagerConnector(packDir):
    kmConnectorUrl = "https://apim.docs.wso2.com/en/4.1.0/assets/attachments/administer/wso2is-extensions-1.4.2.zip"
    runShell(['wget', '-P', packDir, kmConnectorUrl])
    runShell(['unzip', packDir + "/wso2is-extensions-1.4.2.zip", '-d', packDir])
    runShell(
        ['cp', '-r', packDir + '/wso2is-extensions-1.4.2/dropins/.', KM_HOME_DIR + "/repository/components/dropins"])
    runShell(['cp', '-r', packDir + '/wso2is-extensions-1.4.2/webapps/.',
              KM_HOME_DIR + "/repository/deployment/server/webapps"])


def updateDBToml(data, dbpropertyName, dbName):
    data['database'][dbpropertyName][
        'url'] = "jdbc:mysql://localhost:3306/" + dbName + "?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
    data['database'][dbpropertyName]['username'] = dbUsername
    data['database'][dbpropertyName]['password'] = dbPassword


def updateDatasourceDbToml(datasourceId, tomlPackHome, dbName):
    data = toml.load(tomlPackHome + "/repository/conf/deployment.toml")
    for i in data['datasource']:
        print(i['id'])
        if (i['id'] == "ACTIVITI_DB"):
            i[
                'url'] = "jdbc:mysql://localhost:3306/" + ACTIVITI_DB + "?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif (i['id'] == "WSO2TELCO_DEP_DB"):
            i[
                'url'] = "jdbc:mysql://localhost:3306/" + WSO2TELCO_DEP_DB + "?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif (i['id'] == "WSO2TELCO_RATE_DB"):
            i[
                'url'] = "jdbc:mysql://localhost:3306/" + WSO2TELCO_RATE_DB + "?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif (i['id'] == "WSO2AM_STATS_DB"):
            i[
                'url'] = "jdbc:mysql://localhost:3306/" + WSO2AM_STATS_DB + "?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        i['username'] = dbUsername
        i['password'] = dbPassword
    f = open(tomlPackHome + "/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()


def main():
    print("starting automation ----")
    createProductDirectories()
    unzipProduct(axpProductZipPath, tmDirectory)
    unzipProduct(axpProductZipPath, gwDirectory)
    unzipProduct(axpProductZipPath, cpDirectory)
    unzipProduct(kmProductZipPath, kmDirectory)
    setProductHomeDirectories()
    printHomeDirs()

    # setting up packs
    tmSetup()
    gwSetup()
    controlPlaneSetup()
    kmSetup()

    print("process completed!")


if __name__ == "__main__":
    main()
