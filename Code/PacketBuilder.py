from scapy.all import IP, TCP, ls, wrpcap, rdpcap

ls(IP) #tjek IP felter
ls(TCP) #tjek TCP felter


packet = IP(dst="10.0.0.1") / TCP(sport=12345,dport=5000,flags="S") #har ikke source ip

IP(bytes(packet)).show()
packet.show() #check pakken

#Gemmer pakken i en pcap fil
wrpcap("packet.pcap", packet)
print("Packet saved to packet.pcap")

#Indlæs pakken fra pcap filen
loaded_packets = rdpcap("packet.pcap")

#Visualiserer de indlæste pakke
for p in loaded_packets:
    if IP in p and TCP in p:
        print(f"Source IP: {p[IP].src}")
        print(f"Destination IP: {p[IP].dst}")
        print(f"Source port: {p[TCP].sport}")
        print(f"Destination port: {p[TCP].dport}")
        print(f"TCP flags: {p[TCP].flags}")


#mangler at lave attacker klient der prøver dem af