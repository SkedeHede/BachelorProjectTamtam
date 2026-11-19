#Opretter og konfigurerer det virtuelle Mininet-netværk
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel

import argparse

#fået af chat, ændrer opstarten så porte bliver tilføjet enkeltvis, så der ikke er problemer med at tilføje for mange porte på en gang
class ScalableOVSBridge(OVSBridge):

    def start(self, controllers):
        # Opret switchen
        self.cmd("ovs-vsctl --may-exist add-br", self.name)

        # Brug switchen uden controller
        self.cmd("ovs-vsctl set-fail-mode", self.name, "standalone")

        # Tilføj hver port separat
        for intf in self.intfList():
            if self.ports[intf] and not intf.IP():
                self.attach(intf)

def create_network(num_clients=100, num_attackers=1, interactive=True): #hardcoded number of clients
    net = Mininet(
    topo=None,
    build=False,
    controller=None,
    switch=ScalableOVSBridge 
)

    #Create server
    #server = net.addHost("server", ip="10.0.0.1")
    server = net.addHost("server", ip="10.0.0.1/24") #ovenfor fik fejl, tester med anden subnet maske
    
    #Create switch
    switch = net.addSwitch("s1")
    print("Switch type:", type(switch)) #test for at se om korrekt

    #Connect server to switch
    net.addLink(server, switch)

    #Create legitimate clients
    for i in range(1, num_clients + 1):
        client = net.addHost(
            f"client{i}",
            ip=f"10.0.0.{i + 1}/24" #tilføjet /24 som subnet maske for test
        )
        net.addLink(client, switch)
    for i in range(1, num_attackers + 1):
        attacker = net.addHost(
            f"attacker{i}",
            ip=f"10.0.0.{i + 101}/24"
        )
        net.addLink(attacker, switch)

    #build network
    net.build()
    #Start network
    net.start()

    """
#test af switch og server til 100 klienter
    print("=== SWITCH STATUS ===")
    print(switch.cmd("ovs-vsctl list-ports s1"))

    print("=== ANTAL SWITCH PORTE ===")
    print(switch.cmd("ovs-vsctl list-ports s1 | wc -l"))

    print("=== SWITCH INFORMATION ===")
    print(switch.cmd("ovs-vsctl show"))
    """

    #test 5 klienter for at se om det hele bliver sat op
    print("=== TEST AF NETVÆRK ===")


    server = net.get("server")

    for i in (1, num_clients + 1):
        client = net.get(f"client{i}")
        packet_loss = net.ping(hosts=[client, server])
        print(f"client{i} -> server: {packet_loss}% packet loss")
    
    """
    Kode som testede forbindelse med server + switch + TO klienter:
    print("Network started!") #test
    #test for fejl
    print("=== SWITCH STATUS ===")
    print(switch.cmd("ovs-vsctl show"))

    print("=== SERVER ===")
    print(server.cmd("ip addr show server-eth0"))

    print("=== CLIENT1 ===")
    print(net.get("client1").cmd("ip addr show client1-eth0"))

    print("=== SWITCH PORTS ===")
    print(switch.cmd("ovs-ofctl dump-ports-desc s1"))

    print("Network started!")
    #net.pingAll() #pinger alle, skiftet til kun at pinge klient 1 og server
    print("Testing connection between client1 and server")
    print(net.ping(hosts=[net.get("client1"), net.get("server")]))
    
    #Debugging: Check if the server can reach the clients
    """

    if interactive:
        CLI(net)
        net.stop()

    return net


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mininet network topology"
    )

    parser.add_argument(
        "--amount-of-clients",
        type=int,
        default=2,
        help="Number of clients to create"
    )

    args = parser.parse_args()

    if args.amount_of_clients < 1:
        parser.error("--amount-of-clients must be positive")

    setLogLevel("info")
    create_network(num_clients=args.amount_of_clients)