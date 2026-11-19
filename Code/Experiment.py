from Topology import create_network
import time
from mininet.log import setLogLevel #for at teste fejl
from pathlib import Path

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
def start_client(client, duration, experiment_dir):
    process = client.popen(
    "python3",
    "Code/Client.py",
    "--duration", str(duration),
    "--interval", "0.5",
    "--client-id", client.name,
    "--log-dir", str(experiment_dir)
    )
    return process

def start_clients(net, num_clients, duration, experiment_dir):
    processes = []

    for i in range(1, num_clients + 1):
        client = net.get(f"client{i}")
        process = start_client(client, duration, experiment_dir)
        processes.append(process)

    return processes


def start_Capture(server, pcap_file):
    process = server.popen(

    ".venv/bin/python",
    "-u",
    "Code/PacketCapture.py",
    "--output", str(pcap_file)
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
        num_clients=100, #ændret for nu
        num_attackers=0, #0 for baseline experimentet
        interactive=False
    )
    try:
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        capture_process = start_Capture(server, pcap_file)
        time.sleep(1)

        processes = start_clients(net, num_clients=100, duration=300, experiment_dir=experiment_dir)

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