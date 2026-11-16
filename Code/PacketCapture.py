from scapy.all import sniff, wrpcap, IP, TCP

# Opfang de første 20 TCP-pakker
packets = sniff(
    iface="server-eth0", #Serverens netværksinterface (server-eth0 for mininet)
    filter="tcp port 5000", #Filtrer kun TCP-pakker (tcp port 5000)
    count=20 #Antal pakker der skal opfanges
)

#Gem de opfangede pakkerserver .venv/bin/python -u Code/PacketCapture.py &
wrpcap("captured_packets.pcap", packets)


for p in packets:
    if IP in p and TCP in p:
        print(f"Source IP: {p[IP].src}")
        print(f"Destination IP: {p[IP].dst}")
        print(f"Source port: {p[TCP].sport}")
        print(f"Destination port: {p[TCP].dport}")
        print(f"TCP flags: {p[TCP].flags}")