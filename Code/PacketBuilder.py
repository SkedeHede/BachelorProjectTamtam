from scapy.all import IP, TCP, ls, send

#ls(IP) #tjek IP felter
#ls(TCP) #tjek TCP felter
Server_ip = "10.0.0.1"
Server_port = 5000

packet = IP(dst=Server_ip) / TCP(sport=12345,dport=Server_port,flags="S") #S står for "SYN-flag"

IP(bytes(packet)).show()
packet.show() #check pakken

send(packet, count=1, verbose=True)

#mangler at lave attacker klient der prøver dem af