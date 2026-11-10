#her kommer vi til at lave angribsklienter
#i første omgang tager vi bare packetbuilder.py og kopiere herind
#der bliver kun sendt én pakke i starten så vi kan teste om det virker
#topologi skal ændres så den understøtter attacker.py
#linje 10 i topology skal ændres til:
#def create_network(num_clients=2, num_attackers=1):
#vi tilføjer denne løkke i topologi linje 28:
"""
for i in range(1, num_attackers + 1):
attacker = net.addHost(
    f"attacker{i}",
    ip=f"10.0.0.{i + 101}/24"
)
net.addLink(attacker, switch)
"""

from scapy.all import send
from PacketBuilder import build_syn_packet

SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000

def send_one_syn():
    packet = build_syn_packet(
        SERVER_IP,
        SERVER_PORT,
        12345
    )

    send(packet, count=1, verbose=True)


