#!/usr/bin/python 
"""
.. module:: batchFarmServices
   :platform: Unix, Windows, OSX
   :synopsis: Utilities for doing PWA with the Jlab batch system.

.. moduleauthor:: Joshua Pond <jpond@jlab.org>


"""
import os, glob, sys
from subprocess import Popen

indir = os.getcwd().strip("GUI")
keyfileDir=os.path.join(indir,"keyfiles")
dataDir=os.path.join(indir,"fitting")
scriptOutDir=os.path.join(indir,"scripts","submitions")
keyfiles=glob.glob(os.path.join(keyfileDir,'*.keyfile'))
cf = numpy.load(os.path.join(indir,"GUI","Control_List.npy"))
i=1

def submit(jsub_file):
    cmd = 'jsub '+jsub_file
    proc = Popen(cmd,
        shell = True,
        executable = os.environ.get('SHELL', '/bin/tcsh'),
        env = os.environ)
   
BoA = sys.argv[1] 
if BoA == 'n':
    DoM = sys.argv[2]
    if DoM == 'mc':
        dataDir=os.path.join(indir,"simulation")
        AoR = sys.argv[3]
        stri = '/'+DoM+'/'+AoR
        filen = 'events'
    elif DoM == 'data':
        dataDir=os.path.join(indir,"simulation")
        stri = 'data'
        filen = 'events'
elif BoA == 'y':
    DoM = sys.argv[2]
    if DoM == 'mc':
        dataDir=os.path.join(indir,"fitting")
        AoR = sys.argv[3]
        stri = '/'+DoM+'/'+AoR
        filen = 'events'
    elif DoM == 'data':
        dataDir=os.path.join(indir,"fitting")
        stri = 'data'
        filen = 'events'    
for keyfile in keyfiles:
    for path, subdirs, files in os.walk(dataDir):
        if stri in path:         
            for filename in glob.glob(os.path.join(path,'*.gamp')):
                filename = os.path.basename(filename)
                cmd_opts = dict(
    				outfile = os.path.join(path,os.path.basename(keyfile)).replace('.keyfile','.bamp'),
                    keyfile = os.path.join(keyfileDir,keyfile),
                    infile = os.path.join(path, filename))                    
                cmd = '''\
/group/clas/builds/bin/gamp {keyfile} < {infile} > {outfile}
    '''.format(**cmd_opts)
                auger_opts = dict(
                    project = cf[9],
                    track = 'analysis',
                    jobname = 'runGamp',
                    os = 'centos65',
                    time = 360,
                    memory = '1000 MB',
                    cmd = cmd)
                jsub_filename = os.path.join(scriptOutDir,"subGamp"+str(i))
                jsub_file = open(jsub_filename,'w')
                jsub_file.write('''\
PROJECT: {project}
TRACK: {track}
JOBNAME: {jobname}
OS: {os}
TIME: {time}
MEMORY: {memory}
COMMAND: {cmd}
    '''.format(**auger_opts))    
                jsub_file.close()
                print jsub_filename
                #if not os.path.isfile(os.path.join(path,os.path.basename(keyfile)).replace('.keyfile','.bamp')):
                submit(jsub_filename)
                #os.remove(jsub_filename)                    
                i += 1  
