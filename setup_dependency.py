import os, sys, io
from io import StringIO

fileName = "environment.yml"
userCreateNew = str(input("Do you want to create a new environment? ([y]/n) ")).lower().strip()
if(userCreateNew == "y"):
    newEnvName = str(input("Environment name: "))
    os.system("conda env create --name {} --file=./env/{}".format(newEnvName, fileName))
else:
    os.system("conda env list")
    envName = str(input("Choose the environment (INPUT AS IS!): ")).strip()
    while(envName == "base"):
        print("Cannot update base!, please choose another or create new!")
        envName = str(input("Choose the environment (INPUT WORD BY WORD!): ")).strip()
    print("This file will update \"{}\" environment with the packages in {}".format(envName, fileName))
    userChoice = str(input("([y]/n) ")).lower().strip()
    if(userChoice == "y"):
        os.system("conda env update --name {} --file ./env/{}".format(envName, fileName))
