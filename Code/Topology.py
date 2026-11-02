#Opretter og konfigurerer det virtuelle Mininet-netværk
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_network(num_clients=2): #hardcoded number of clients
    net = Mininet(controller=None, switch=OVSBridge)

    #Create server
    server = net.addHost("server", ip="10.0.0.1")

    #Create switch
    switch = net.addSwitch("s1")

    #Connect server to switch
    net.addLink(server, switch)

    #Create legitimate clients
    for i in range(1, num_clients + 1):
        client = net.addHost(
            f"client{i}",
            ip=f"10.0.0.{i + 1}"
        )
        net.addLink(client, switch)

    #Start network
    net.start()

    print("Network started!")
    net.pingAll()

    #Open Mininet CLI
    CLI(net)

    #Stop network
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_network(num_clients=2)
