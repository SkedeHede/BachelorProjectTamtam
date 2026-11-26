from scapy.all import sniff, wrpcap

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Capture TCP packets from Mininet server"
)

parser.add_argument(
    "--output",
    type=str,
    default="logs/pcap/captured_packets.pcap",
    help="Path to the output PCAP file"
)

parser.add_argument(
    "--duration",
    type=float,
    default=310,
    help="Duration of packet capture in seconds"
)

args = parser.parse_args()

output_file = Path(args.output)
output_file.parent.mkdir(parents=True, exist_ok=True)

# Opfang de første 20 TCP-pakker
packets = sniff(
    iface="server-eth0", #Serverens netværksinterface (server-eth0 for mininet)
    filter="tcp port 5000", #Filtrer kun TCP-pakker (tcp port 5000)
    timeout=args.duration #Tidsgrænse for opfangning. sat til 5 minutter (300 sekunder) + extra til for capture filen til at fungerer
)

#Gem de opfangede pakkerserver .venv/bin/python -u Code/PacketCapture.py &
wrpcap(str(output_file), packets)


print(f"Captured {len(packets)} packets")
print(f"PCAP file saved to {output_file}")
"""
Der er ikke behov for dette længere, da vi allerede har gemt pakkene i en pcap-fil.
derudover gør det vores buffer bliver fuld og programmet ikke lukker ordentligt. Vi bruger i stedet de 2 linjer ovenfor
for p in packets:
    if IP in p and TCP in p:
        print(f"Source IP: {p[IP].src}")
        print(f"Destination IP: {p[IP].dst}")
        print(f"Source port: {p[TCP].sport}")
        print(f"Destination port: {p[TCP].dport}")
        print(f"TCP flags: {p[TCP].flags}")
"""