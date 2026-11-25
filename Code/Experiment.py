from Topology import create_network
from Merge import merge_csv
import time
from mininet.log import setLogLevel #for at teste fejl
from pathlib import Path
import json
from datetime import datetime

#===========================================#
#        Experiment configurations          #
#===========================================#

CLIENT_OFFSET = 0.1                                             #Sekunder mellem klienters start (for at undgå synkronisering)
NUM_CLIENTS = 3                                                 #Antal legitime klienter
DURATION = 60  + CLIENT_OFFSET*NUM_CLIENTS                      #Eksperimentets varighed i sekunder
CLIENT_INTERVAL = 0.5                                           #Sekunder mellem klientrequests
CAPTURE_DURATION = DURATION + 15 + CLIENT_OFFSET*NUM_CLIENTS    #Varighed af packet capture


NUM_ATTACKERS = 1                                   #Antal angribere (0 = baseline)
ATTACK_START = 15 + CLIENT_OFFSET*NUM_CLIENTS
ATTACK_DURATION = 30 + CLIENT_OFFSET*NUM_CLIENTS
ATTACK_RATE = 10    #Er dette SYN packets per sekund? 


EXPERIMENT_TYPE = "attack"  #baseline / attack / mitigation

#Network configurations
SERVER_BW = 100       # Mbps
HOST_BW = 100         # Mbps
LINK_DELAY = "5ms"    # Delay per link


#Global counter til eksåerimentforsøg
Counter_file = Path("Experiment_Counter.txt")

def get_next_experiment_ID():
    counter_file = Path("Experiment_Counter.txt")

    if counter_file.exists():
        experiment_id = int(counter_file.read_text().strip())
    else:
        experiment_id = 0

    counter_file.write_text(str(experiment_id + 1))

    return experiment_id

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

        if i < num_clients: #OFFSET
            time.sleep(CLIENT_OFFSET)  #Vent mellem klienter for at undgå synkronisering

    return processes

def start_attacker(attacker, duration, rate, experiment_dir):
    process = attacker.popen(
        "python3",
        "Code/Attacker.py",
        "--attacker-id", attacker.name,
        "--duration", str(duration),
        "--rate", str(rate),
        "--log-dir", str(experiment_dir)
    )

    return process


def start_attackers(net, num_attackers, duration, rate, experiment_dir):
    processes = []

    for i in range(1, num_attackers + 1):
        attacker = net.get(f"attacker{i}")

        process = start_attacker(
            attacker,
            duration,
            rate,
            experiment_dir
        )

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


def save_experiment_config(experiment_dir, experiment_id):
    config = {
        "experiment_id": experiment_id,
        "experiment_type": EXPERIMENT_TYPE,
        "timestamp": datetime.now().isoformat(),
        "num_clients": NUM_CLIENTS,
        "num_attackers": NUM_ATTACKERS,
        "duration_seconds": DURATION,
        "client_interval_seconds": CLIENT_INTERVAL,
        "capture_duration_seconds": CAPTURE_DURATION,
        "attack_start_seconds": ATTACK_START,
        "attack_duration_seconds": ATTACK_DURATION,
        "attack_rate_per_attacker": ATTACK_RATE,
        "server_bandwidth_mbps": SERVER_BW,
        "host_bandwidth_mbps": HOST_BW,
        "link_delay": LINK_DELAY,
    }

    config_path = Path(experiment_dir) / "config.json"

    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

    print(f"Experiment configuration saved to {config_path}")



def main():

    # Kontrollerer konfigurationen
    if NUM_ATTACKERS > 0 and ATTACK_START + ATTACK_DURATION > DURATION:
        raise ValueError("Attack duration exceeds experiment duration")

    experiment_id = get_next_experiment_ID()

    experiment_dir = (
        Path("logs") / "csv" / f"experiment_{experiment_id:03d}"
    )
    experiment_dir.mkdir(parents=True, exist_ok=True)

    pcap_dir = Path("logs") / "pcap"
    pcap_dir.mkdir(parents=True, exist_ok=True)

    pcap_file = pcap_dir / f"experiment_{experiment_id:03d}.pcap"

    save_experiment_config(experiment_dir, experiment_id)

    net = create_network(
        num_clients=NUM_CLIENTS,
        num_attackers=NUM_ATTACKERS,
        interactive=False,
        server_bw=SERVER_BW,
        host_bw=HOST_BW,
        link_delay=LINK_DELAY
    )

    try:
        # Starter serveren
        server = net.get("server")
        start_server(server)
        time.sleep(1)

        # Starter packet capture
        capture_process = start_Capture(
            server,
            pcap_file,
            CAPTURE_DURATION
        )
        time.sleep(1)

        # Starter legitime klienter
        processes = start_clients(
            net,
            num_clients=NUM_CLIENTS,
            duration=DURATION,
            experiment_dir=experiment_dir,
            interval=CLIENT_INTERVAL
        )

        experiment_start = time.perf_counter()

        # Starter attackers efter den angivne forsinkelse
        attacker_processes = []

        if NUM_ATTACKERS > 0:
            remaining = ATTACK_START - (
                time.perf_counter() - experiment_start
            )

            if remaining > 0:
                time.sleep(remaining)

            print("Starting attackers")

            attacker_processes = start_attackers(
                net,
                num_attackers=NUM_ATTACKERS,
                duration=ATTACK_DURATION,
                rate=ATTACK_RATE,
                experiment_dir=experiment_dir
            )

        # Venter på legitime klienter
        for process in processes:
            exit_code = process.wait()
            print(f"Client exit code: {exit_code}")

        # Venter på attackers
        for process in attacker_processes:
            exit_code = process.wait()
            print(f"Attacker exit code: {exit_code}")

        # Venter på packet capture
        capture_exit_code = capture_process.wait()
        print(f"PacketCapture exit code: {capture_exit_code}")

    finally:
        net.stop()
        merge_csv(experiment_dir)


if __name__ == "__main__":
    setLogLevel("debug") #test fejl.
    main()