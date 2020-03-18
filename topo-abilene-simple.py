#!/usr/bin/env python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from isp_config import *


class ExampleTestTopo(Topo):
    def __init__(self, bw=1e3, **opts):
        super(ExampleTestTopo, self).__init__(**opts)

        # add nodes, switches first...
        NewYork = self.addSwitch( 's1' )
        Chicago = self.addSwitch( 's2' )
        WashingtonDC = self.addSwitch( 's3' )
        Seattle = self.addSwitch( 's4' )
        Sunnyvale = self.addSwitch( 's5' )
        LosAngeles = self.addSwitch( 's6' )
        Denver = self.addSwitch( 's7' )
        KansasCity = self.addSwitch( 's8' )
        Houston = self.addSwitch( 's9' )
        Atlanta = self.addSwitch( 's10' )
        Indianapolis = self.addSwitch( 's11' )

        # ... and now hosts
        NewYork_host = self.addHost( 'h1' )
        Chicago_host = self.addHost( 'h2' )
        WashingtonDC_host = self.addHost( 'h3' )
        Seattle_host = self.addHost( 'h4' )
        Sunnyvale_host = self.addHost( 'h5' )
        LosAngeles_host = self.addHost( 'h6' )
        Denver_host = self.addHost( 'h7' )
        KansasCity_host = self.addHost( 'h8' )
        Houston_host = self.addHost( 'h9' )
        Atlanta_host = self.addHost( 'h10' )
        Indianapolis_host = self.addHost( 'h11' )

        # add edges between switch and corresponding host
        self.addLink( NewYork , NewYork_host )
        self.addLink( Chicago , Chicago_host )
        self.addLink( WashingtonDC , WashingtonDC_host )
        self.addLink( Seattle , Seattle_host )
        self.addLink( Sunnyvale , Sunnyvale_host )
        self.addLink( LosAngeles , LosAngeles_host )
        self.addLink( Denver , Denver_host )
        self.addLink( KansasCity , KansasCity_host )
        self.addLink( Houston , Houston_host )
        self.addLink( Atlanta , Atlanta_host )
        self.addLink( Indianapolis , Indianapolis_host )

        # add edges between switches
        self.addLink( NewYork , Chicago, bw=10, delay='0.806374975652ms')
        self.addLink( NewYork , WashingtonDC, bw=10, delay='0.605826192092ms')
        self.addLink( Chicago , Indianapolis, bw=10, delay='1.34462717203ms')
        self.addLink( WashingtonDC , Atlanta, bw=2.5, delay='0.557636936322ms')
        self.addLink( Seattle , Sunnyvale, bw=10, delay='1.28837123738ms')
        self.addLink( Seattle , Denver, bw=10, delay='1.11169346865ms')
        self.addLink( Sunnyvale , LosAngeles, bw=10, delay='0.590813628707ms')
        self.addLink( Sunnyvale , Denver, bw=2.5, delay='0.997327682281ms')
        self.addLink( LosAngeles , Houston, bw=10, delay='1.20160833263ms')
        self.addLink( Denver , KansasCity, bw=2.5, delay='0.223328790403ms')
        self.addLink( KansasCity , Houston, bw=10, delay='1.71325092726ms')
        self.addLink( KansasCity , Indianapolis, bw=10, delay='0.240899959477ms')
        self.addLink( Houston , Atlanta, bw=2.5, delay='1.34344500256ms')
        self.addLink( Atlanta , Indianapolis, bw=2.5, delay='0.544962634977ms')


if __name__ == '__main__':
    topo = ExampleTestTopo()
    sw = OVSKernelSwitch  # already the default
    c0 = RemoteController('c0', ip=ONOS_IP, port=6633)
    net = Mininet(topo=topo,
                  controller=c0,
                  switch=sw,
                  cleanup=True,
                  autoSetMacs=True,
                  autoStaticArp=False,
                  link=TCLink)
    net.start()
    CLI(net)
    net.stop()
