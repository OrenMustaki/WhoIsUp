#!/usr/bin/env python3
#
import argparse
import multiprocessing as mp
import re
import itertools
import subprocess as sp
import natsort
import sys

delim = ","

class Check:
    def __init__(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='', epilog='')
        parser.add_argument('-n', '--nprocs', help='Run in parallel on <NPROCS> processes', type=int, action='store',
                            default=32)
        parser.add_argument('-s', '--slurm', help='List all slurm nodes using scontrol show node command',
                            action='store_true', default=False)
        args, hosts = parser.parse_known_args()
        self.nprocs = args.nprocs
        self.slurm = args.slurm

        if self.slurm:
            hosts = [line.split()[0].split("=")[-1] for line in sp.getoutput('scontrol show node').splitlines() if
                     "NodeName=" in line]

        if len(hosts) == 0:
            self.usage()

        hosts = [ self.convert(host) if "[" in host else host.split(',') for host in hosts ]
        hosts = list(itertools.chain.from_iterable(hosts))
        hosts = [host for host in hosts if not host == ' ' and not host == '']
        self.hosts = set(hosts)

    def usage(self):
        print(f"""
Usage : {sys.argv[0]} nodeA{{1..33}}
        {sys.argv[0]} nodeA[37-39]
        {sys.argv[0]} nodeA{{1..33}},nodeA{{34..36}}
        {sys.argv[0]} nodeA{{34..36}}, nodeA[37-39] nodeA40
        {sys.argv[0]} nodeA{{1..33}}, nodeA[37-39] nodeA40, nodeA41,nodeA42
        {sys.argv[0]} nodeA{{1..33}} nodeA{{34..36}}, nodeA[37-39] nodeA40, nodeA41,nodeA42
""")

    def ping(self, host):
        cmd = f'ping -w 1 -c 1 {host} > /dev/null 2>&1'
        if sp.getstatusoutput(cmd)[0] == 0:
            return True
        else:
            return False

    def convert(self, string):
        """
        convert slurm node range expression to a list of nodes
        :param string:
        :return:
        """
        nodes = []
        string = re.split(r',\,*(?![^[]*\])', string)
        for i in string:
            if not "[" in i:
                nodes.append(i)
                continue
            j = i.split('[')[1].replace(']', '')
            h = i.split('[')[0]
            j = j.split(',')
            temp = []
            for k in j:
                if not "-" in k:
                    nodes.append(h + k)
                else:
                    start = int(k.split('-')[0])
                    end = int(k.split('-')[1])
                    for l in range(start, end + 1):
                        nodes.append(h + str(l))
        return nodes

    def work(self, host):
        q.put((host, self.ping(host)))

if __name__ == '__main__':
    c = Check()
    q = mp.Queue()

    p1 = mp.Pool(processes=c.nprocs)
    p1.map(c.work, c.hosts)

    replies = []
    while not q.empty():
        replies.append(q.get())

    for reply in natsort.natsorted(replies):
        print(reply)