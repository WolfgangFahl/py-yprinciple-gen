'''
Created on 2022-12-02

@author: wf
'''
from tests.basetest import Basetest
from meta.metamodel import Property
from yprinciple.smw_targets import PythonTarget

class TestPython(Basetest):
    """
    test python handling
    """
    
    def test_Types(self):
        """
        test the type conversion
        """
        pt=PythonTarget(None)
        prop=Property()
        prop.type="Types/Number"
        ptype=pt.pythonPropType(prop)
        self.assertEqual("float",ptype)