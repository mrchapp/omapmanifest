#!/bin/bash

magic='--calling-python-from-/bin/sh--'
"""exec" python -E "$0" "$@" """#$magic"
if __name__ == '__main__':
  import sys
  if sys.argv[-1] == '#%s' % magic:
    del sys.argv[-1]
del magic

import os
import sys
import xml.dom.minidom

from manifest import Manifest
from project import Project, R_HEADS, R_M


E_FATAL = "Error"
E_WARN = "Warning"

def error(errStr,severity):
  print severity + ": " + errStr
  if (severity == E_FATAL):
    sys.exit()




# TODO: Fix so this is called from  within repo
# TODO: Figure out how to write manifest back to file
def _Main(argv):
    manifest = Manifest(".repo") 
#    print manifest.projects,"\n\n\n"
#    print manifest.projects['repo/u-boot'].gitdir
    for key,project in manifest.projects.iteritems():
        project.revision = _getProjectLocalRevision(project)

    _WriteBaselineToFile(manifest,argv[0])
        

# Get the revision based on the current sync        
def _getProjectLocalRevision(project):
  remotes_m_dir = project.gitdir+ '/' + R_M
  if not os.path.exists(remotes_m_dir):
    error("Directory %s does not exist" % remotes_m_dir,E_FATAL)

  m_master = open(remotes_m_dir+'master','r')
  temp_key = m_master.read()
  m_master.close()
  if (temp_key[0:4] == "ref:"):
      temp_key = str.splitlines(temp_key)[0]
      split_remote_tag = str.split(temp_key," ")
      reference = project.gitdir + '/' + split_remote_tag[1]

      if not os.path.exists(reference):
        error("Referenced file '%s' does not exist" % reference,E_FATAL)

      tag = open(reference,"r")
      return str.splitlines(tag.read())[0]
      tag.close()
  else:
      return str.splitlines(temp_key)[0]



# Write the Baseline out to a file
def _WriteBaselineToFile(manifest, fileName):
    """
  writes manifest XML object to file
  """
    root = xml.dom.minidom.parse(manifest.manifestFile)
    config = root.childNodes[0]
    
    for node in config.childNodes:
      if node.nodeName == 'project':
        node.setAttribute('revision', manifest._projects[node.getAttribute('name')] .revision)
    fileOut = open(fileName, 'w')
    root.writexml(fileOut,"  ", "  ","",'UTF-8')

# Call _Main
_Main(sys.argv[1:])
