import os
import subprocess
import random
class VCF:

    def __init__(self, name, number):
        self.name = name
        self.number = number

    def __str__(self):
        return "BEGIN:VCARD\nVERSION:2.1\nN:;%s\nFN:WXL\nTEL;CELL:%s\nEND:VCARD\n" % (self.name, self.number)

alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
def main():
    outfd = open("100.vcf", "w")
    for i in xrange(100):
        number = "-".join([str(random.randint(1, 999)), str(random.randint(1, 999)), str(random.randint(1, 999)) ])
        name = "".join(random.sample(alpha, random.randint(3, 7)))
        vcf = VCF(name, number)
        outfd.write(str(vcf))
    outfd.close()

if __name__ == "__main__":
    main()
