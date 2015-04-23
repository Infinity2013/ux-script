import sys
import adbhelper
from clog import clog

ecs_l = {"1": [50, 245],
         "2": [201, 262],
         "3": [315, 217],
         "4": [495, 217]
         }

ecs_kk = {"1": [43, 326],
          "2": [149, 308],
          "3": [276, 294],
          "4": [370, 304]
          }

malata_l = {"1":[287, 738],
            "2":[1051, 704],
            "3":[1752, 703],
            "4":[2385, 749]
            }

ecs2_8a_l = {"1" :[241, 760],
           "2" :[238, 597],
           "3" :[238, 487],
           "4" :[271, 366],
           }
one695_1_coho_l = {"1" :[43, 165],
                   "2" :[139, 184],
                   "3" :[240, 165],
                   "4" :[350, 165],
            }      
chiphd8_0_coho_l = {"4" :[738, 140],
                    "3" :[549, 143],
                    "2" :[330, 140],
                    "1" :[130, 140],
            }       
ecs27b_0_coho_l = {"4" :[365, 167],
            }   
one7_0_4_coho_l = {"4" :[467, 184],
            }
productDic = {
    "st70408_4_coho_l": ecs_l,
    "ecs_e7_l": ecs_l,
    "ecs28a_0_coho_l": ecs2_8a_l,
    "one695_1_coho_l": one695_1_coho_l,
    "chiphd8_0_coho_l": chiphd8_0_coho_l,
    "ecs27b_0_coho_l" :ecs27b_0_coho_l,
    "one7_0_4_coho_l" : one7_0_4_coho_l,
    }

clog = clog()
clog.setLevel("e")
def getLocation(index):
    ver = adbhelper.getAndroidVer()
    product = adbhelper.getProp("ro.build.product")
    position_selector = "%s_%s" % (product, ver)
    if position_selector not in productDic.keys():
        clog.e("Error: %s is not supported, please contact xiaoliang!" % position_selector)
        sys.exit()
    pair = productDic.get(position_selector).get(index)
    clog.d("getLocation: \n \
    position_selector: %s\n \
    index: %s, pair: %s" % (position_selector, index, pair))
    return pair
