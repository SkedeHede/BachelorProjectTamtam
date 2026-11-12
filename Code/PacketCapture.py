from scapy.all import sniff, wrpcap

# Opfang de første 20 TCP-pakker
packets = sniff(
    iface="", #Serverens netværksinterface
    filter="", #tcp, #Filtrer kun TCP-pakker
    count=20 #Antal pakker der skal opfanges
)

#Gem de opfangede pakker
wrpcap("captured_packets.pcap", packets)