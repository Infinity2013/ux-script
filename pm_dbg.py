#!/usr/bin/env python
import re

import loghelper
import sys

DBG = True
early_start = "noirq resume of devices complete after"
early_end = "early resume of devices complete after"

class pm_dbg_node():
    duration = 0
    device = ""
    def dump(self):
        print "%-10d %s" % (self.duration, self.device)

def findEdge(head, tail, dmesg):
    start = 0
    end = 0
    for i in range(len(dmesg)):
        if head in dmesg[i]:
            start = i
        elif tail in dmesg[i]:
            end = i
    if start == 0 or end == 0:
        print "Error: Can't find the edge"
        sys.exit()
    return [start + 1, end]

def main():
    if len(sys.argv) != 2:
        print "Only one args is supported!"
        sys.exit()

    inpf = open(sys.argv[1], "r")
    rawDmesg = inpf.readlines()
    edge = findEdge(early_start, early_end, rawDmesg)
    elementList = []
    for i in range(edge[0], edge[1]):
        elementList.append(loghelper.parse2Element(rawDmesg[i].strip(), "dmesg"))
    
    pm_dbg_nodeList = []
    for i in range(0, len(elementList) - 1, 2):
        node = pm_dbg_node()
        node.duration = elementList[i + 1].ts - elementList[i].ts
        res = re.findall("device\[\S*\]\sdriver\[\S*\]", elementList[i].content)
        if len(res) == 1:
            node.device = res[0].strip()
        else:
            node.device = elementList[i].content

        pm_dbg_nodeList.append(node)


    inpf.close()
    for node in pm_dbg_nodeList:
        node.dump()


if __name__ == "__main__":
    main()
        


