from scapy.all import IP, TCP, ls

ls(IP) #tjek IP felter
ls(TCP) #tjek TCP felter


packet = IP(dst="10.0.0.1") / TCP(sport=12345,dport=5000,flags="S") #har ikke source ip

IP(bytes(packet)).show()
packet.show() #check pakken

#mangler at lave attacker klient der prøver dem af