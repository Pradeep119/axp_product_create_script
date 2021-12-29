#!/usr/bin/env python3
import os
import glob
from zipfile import ZipFile
import subprocess
import urllib
import toml

#configure this values
parentDir= "/home/pradeepk/Documents/AXP/product_build_script/product"
axpProductZipPath="/home/pradeepk/Documents/AXP/product_build_script/axp-dep-6.0.1-SNAPSHOT.zip"
kmProductZipPath="/home/pradeepk/Documents/AXP/product_build_script/wso2is-km-5.10.0+1605108146035.full.zip"
dbUsername='root'
dbPassword='root123'
apiMgtDb='wl_apimgtdb'
regDb='wl_egdb'
userStoreDb='wl_userstoredb'
WSO2TELCO_DEP_DB='wl_proddepdb'
ACTIVITI_DB='wl_activitidb'
WSO2TELCO_RATE_DB='wl_rateDb'
WSO2AM_STATS_DB='wl_apistatsdb'
#configuration end


kmDirectory = os.path.join(parentDir, "KM")
tmDirectory = os.path.join(parentDir, "TM")
gwDirectory = os.path.join(parentDir, "GATEWAY")
portalDirectory = os.path.join(parentDir, "PORTAL")

GW_HOME_DIR= None
TM_HOME_DIR= None
PTL_HOME_DIR= None
KM_HOME_DIR= None

def createProductDirectories():
    os.mkdir(kmDirectory)
    os.mkdir(tmDirectory)
    os.mkdir(gwDirectory)
    os.mkdir(portalDirectory)

def unzipProduct(zipFilePath,productDir):
    proc = subprocess.Popen(['unzip', zipFilePath, '-d' ,productDir])
    proc.communicate()
    proc.wait()

def setProductHomeDirectories():
    global TM_HOME_DIR
    global GW_HOME_DIR
    global PTL_HOME_DIR
    global KM_HOME_DIR
    TM_HOME_DIR = glob.glob(tmDirectory+"/*")[0]
    GW_HOME_DIR = glob.glob(gwDirectory+"/*")[0]
    PTL_HOME_DIR = glob.glob(portalDirectory+"/*")[0]
    KM_HOME_DIR = glob.glob(kmDirectory+"/*")[0]

def printHomeDirs():
    print("TM HOME DIR : ",TM_HOME_DIR)
    print("KM HOME DIR : ",KM_HOME_DIR)
    print("GW HOME DIR : ",GW_HOME_DIR)
    print("PORTAL HOME DIR : ",PTL_HOME_DIR)

def tmSetup():
    runShell(['chmod', '777', TM_HOME_DIR+"/bin/profileSetup.sh" , TM_HOME_DIR+"/bin/axpserver.sh"])
    runShell(['cp', TM_HOME_DIR+"/repository/deployment/server/webapps/internal#data#v1.war" ,TM_HOME_DIR])
    runShell(['sh', TM_HOME_DIR+"/bin"+"/profileSetup.sh" , '-Dprofile=traffic-manager'])
    runShell(['mv' ,TM_HOME_DIR+"/internal#data#v1.war" , TM_HOME_DIR+"/repository/deployment/server/webapps/"])
    runShell(['rm', '-rf', TM_HOME_DIR+"/repository/conf/deployment.toml"])
    runShell(['mv', TM_HOME_DIR+"/repository/conf/deployment_TM.toml" , TM_HOME_DIR+"/repository/conf/deployment.toml"])
    
    downloadMysqlConnector(TM_HOME_DIR)
    
    data = toml.load(TM_HOME_DIR+"/repository/conf/deployment.toml")
    updateDBToml(data,'apim_db', apiMgtDb)
    updateDBToml(data,'shared_db', regDb)
    f = open(TM_HOME_DIR+"/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

def gwSetup():
    runShell(['chmod', '777', GW_HOME_DIR+"/bin/profileSetup.sh" , GW_HOME_DIR+"/bin/axpserver.sh"])
    runShell(['cp', GW_HOME_DIR+"/repository/deployment/server/webapps/internal#data#v1.war" ,GW_HOME_DIR])
    runShell(['sh', GW_HOME_DIR+"/bin"+"/profileSetup.sh" , '-Dprofile=gateway-worker'])
    runShell(['mv' ,GW_HOME_DIR+"/internal#data#v1.war" , GW_HOME_DIR+"/repository/deployment/server/webapps/"])
    runShell(['rm', '-rf', GW_HOME_DIR+"/repository/conf/deployment.toml"])
    runShell(['mv', GW_HOME_DIR+"/repository/conf/deployment_GW.toml" , GW_HOME_DIR+"/repository/conf/deployment.toml"])

    downloadMysqlConnector(GW_HOME_DIR)

    data = toml.load(GW_HOME_DIR+"/repository/conf/deployment.toml")
    updateDBToml(data,'apim_db', apiMgtDb)
    f = open(GW_HOME_DIR+"/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    updateDatasourceDbToml('WSO2TELCO_DEP_DB',GW_HOME_DIR,WSO2TELCO_DEP_DB)

def portalSetup():
    runShell(['rm', '-rf', PTL_HOME_DIR+"/repository/conf/deployment.toml"])
    runShell(['mv', PTL_HOME_DIR+"/repository/conf/deployment_PTL.toml" , PTL_HOME_DIR+"/repository/conf/deployment.toml"])

    downloadMysqlConnector(PTL_HOME_DIR)

    data = toml.load(PTL_HOME_DIR+"/repository/conf/deployment.toml")
    updateDBToml(data,'apim_db', apiMgtDb)
    updateDBToml(data,'shared_db', regDb)
    updateDBToml(data,'user', userStoreDb)
    f = open(PTL_HOME_DIR+"/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    updateDatasourceDbToml('WSO2TELCO_DEP_DB',PTL_HOME_DIR,WSO2TELCO_DEP_DB)
    updateDatasourceDbToml('ACTIVITI_DB',PTL_HOME_DIR,ACTIVITI_DB)
    updateDatasourceDbToml('WSO2TELCO_RATE_DB',PTL_HOME_DIR,WSO2TELCO_RATE_DB)
    updateDatasourceDbToml('WSO2AM_STATS_DB',PTL_HOME_DIR,WSO2AM_STATS_DB)

def kmSetup():
    downloadKeyManagerConnector(KM_HOME_DIR)

    runShell(['rm', '-rf', KM_HOME_DIR+"/repository/conf/deployment.toml"])
    runShell(['mv', TM_HOME_DIR+"/repository/conf/deployment_KM.toml" , KM_HOME_DIR+"/repository/conf/deployment.toml"])

    data = toml.load(KM_HOME_DIR+"/repository/conf/deployment.toml")
    updateDBToml(data,'identity_db', apiMgtDb)
    updateDBToml(data,'shared_db', regDb)
    updateDBToml(data,'apim_db', apiMgtDb)
    updateDBToml(data,'user', userStoreDb)
    f = open(KM_HOME_DIR+"/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

    downloadMysqlConnector(KM_HOME_DIR)

def runShell(cmdArray):
    proc = subprocess.Popen(cmdArray)
    proc.communicate()
    proc.wait()

def downloadMysqlConnector(packDir):
    mysqlConnectorUrl = "https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/5.1.40/mysql-connector-java-5.1.40.jar"
    runShell(['wget', '-P' , packDir+"/lib" , mysqlConnectorUrl])

def downloadKeyManagerConnector(packDir):
    kmConnectorUrl = "https://apim.docs.wso2.com/en/3.2.0/assets/attachments/administer/wso2is-km-connector-1.0.16.zip"
    runShell(['wget', '-P' , packDir , kmConnectorUrl])
    runShell(['unzip', packDir+"/wso2is-km-connector-1.0.16.zip", '-d' ,packDir])
    runShell(['cp', '-r', packDir+'/wso2is-extensions-1.0.16/dropins/.',  KM_HOME_DIR+"/repository/components/dropins"])
    runShell(['cp', '-r', packDir+'/wso2is-extensions-1.0.16/webapps/.',  KM_HOME_DIR+"/repository/deployment/server/webapps"])

def updateDBToml(data, dbpropertyName, dbName):
    data['database'][dbpropertyName]['url']="jdbc:mysql://localhost:3306/"+dbName+"?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
    data['database'][dbpropertyName]['username']=dbUsername
    data['database'][dbpropertyName]['password']=dbPassword

def updateDatasourceDbToml(datasourceId, tomlPackHome, dbName):
    data = toml.load(tomlPackHome+"/repository/conf/deployment.toml")
    for i in data['datasource']:
        print(i['id']) 
        if(i['id'] == "ACTIVITI_DB"):
            i['url']="jdbc:mysql://localhost:3306/"+ACTIVITI_DB+"?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif(i['id'] == "WSO2TELCO_DEP_DB"):
            i['url']="jdbc:mysql://localhost:3306/"+WSO2TELCO_DEP_DB+"?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif(i['id'] == "WSO2TELCO_RATE_DB"):
            i['url']="jdbc:mysql://localhost:3306/"+WSO2TELCO_RATE_DB+"?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        elif(i['id'] == "WSO2AM_STATS_DB"):
            i['url']="jdbc:mysql://localhost:3306/"+WSO2AM_STATS_DB+"?autoReconnect=true&amp;relaxAutoCommit=true&amp;useSSL=false&amp;"
        i['username']=dbUsername
        i['password']=dbPassword
    f = open(tomlPackHome+"/repository/conf/deployment.toml", 'w')
    toml.dump(data, f)
    f.close()

def main():
    print("starting automation ----")
    createProductDirectories()
    unzipProduct(axpProductZipPath,tmDirectory)
    unzipProduct(axpProductZipPath,gwDirectory)
    unzipProduct(axpProductZipPath,portalDirectory)
    unzipProduct(kmProductZipPath,kmDirectory)
    setProductHomeDirectories()
    printHomeDirs()

    #setting up packs
    tmSetup()
    gwSetup()
    portalSetup()
    kmSetup()

    print("process completed!")

if __name__ == "__main__":
    main()
