'''
Created on 2022-04-01

@author: wf
'''
import yprinciple

class Version(object):
    '''
    Version handling for pysotsog
    '''
    name="py-yprinciple-gen"
    description='python Y-Principle generator'
    version=yprinciple.__version__
    date = '2022-11-24'
    updated = '2022-11-27'
    authors='Wolfgang Fahl'
    doc_url="https://wiki.bitplan.com/index.php/Py-yprinciple-gen"
    chat_url="https://github.com/WolfgangFahl/py-yprinciple-gen/discussions"
    cm_url="https://github.com/WolfgangFahl/py-yprinciple-gen"
    license=f'''Copyright 2022 contributors. All rights reserved.
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription=f"""{name} version {version}
{description}
  Created by {authors} on {date} last updated {updated}"""

        