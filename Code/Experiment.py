from Topology import create_network
import time
from mininet.log import setLogLevel #for at teste fejl
from pathlib import Path

#===========================================#
#        Experiment configurations          #
#===========================================#

NUM_CLIENTS = 100          #Antal legitime klienter
NUM_ATTACKERS = 0          #Antal angribere (0 = baseline)
DURATION = 300             #Eksperimentets varighed i sekunder
CLIENT_INTERVAL = 0.5      #Sekunder mellem klientrequests
CAPTURE_DURATION = DURATION + 15   #Varighed af packet capture

EXPERIMENT_TYPE = "baseline"  #baseline / attack / mitigation


#Global counter til eksåerimentforsøg
Counter_file = Path("Experiment_Counter.txt")

def get_next_experiment_ID():
    if Counter_file.exists():
        with open(Counter_file, "r") as file:
            counter = int(file.read())
        counter += 1
        
        with open(Counter_file, "w") as file:
            file.write(str(counter))
    else:
        with open(Counter_file, "w") as file:
            counter = 1
            file.write(str(counter))
    return counter

#Udfører kommando til at starte server
def start_server(server):
    server.cmd("python3 Code/Server.py &")

#Udfører kommando til at starte en klient
def start_client(client, duration, experiment_dir, interval):
    process = client.popen(
    "python3",
    "Code/Client.py",
    "--duration", str(duration),
    "--interval", str(interval),
    "--client-id", client.name,
    "--log-dir", str(experiment_dir)
    )
    return process

def start_clients(net, num_clients, duration, experiment_dir, interval):
    processes = []

    for i in range(1, num_clients + 1):
        client = net.get(f"client{i}")
        process = start_client(client, duration, experiment_dir, interval)
        processes.append(process)

    return processes


def start_Capture(server, pcap_file, capture_duration):
    process = server.popen(

    ".venv/bin/python",
    "-u",
    "Code/PacketCapture.py",
    "--output", str(pcap_file),
    "--duration", str(capture_duration)
    )

    return process

def main():

    experiment_id = get_next_experiment_ID()
    experiment_dir = Path("logs") / "csv" / f"experiment_{experiment_id:03d}"

    experiment_dir.mkdir(parents=True, exist_ok=True)


    pcap_dir = Path("logs") / "pcap" 
    pcap_dir.mkdir(parents=True, exist_ok=True)

    pcap_file = pcap_dir / f"experiment_{experiment_id:03d}.pcap"

    net = create_network(
        num_clients=NUM_CLIENTS, #ændret for nu
        num_attackers=NUM_ATTACKERS, #0 for baseline experimentet
        interactive=False
    )
    try:
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        capture_process = start_Capture(server, pcap_file, CAPTURE_DURATION)
        time.sleep(1)

        processes = start_clients(net, num_clients=NUM_CLIENTS, duration=DURATION, experiment_dir=experiment_dir, interval=CLIENT_INTERVAL)

        for process in processes:
            exit_code = process.wait()
            print(f"Client exit code: {exit_code}")

        capture_exit_code = capture_process.wait()
        print(f"PacketCapture exit code: {capture_exit_code}")
    finally:
        net.stop()
    

if __name__ == "__main__":
    setLogLevel("debug") #test fejl.
    main()