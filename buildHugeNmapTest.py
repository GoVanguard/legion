import xml.etree.ElementTree as ET
from random import randint, choice, sample
import datetime

def generate_nmap_xml(num_hosts=1000, base_subnet="172.16"):
    """
    Generate a full sample nmap XML file with session information included.

    Parameters:
    num_hosts (int): Number of hosts to generate.
    base_subnet (str): Base subnet for the hosts.

    Returns:
    str: XML content as a string.
    """
    # XML header
    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<?xml-stylesheet href="file:///C:/Program Files (x86)/Nmap/nmap.xsl" type="text/xsl"?>
<!-- Nmap 7.94 scan initiated as: nmap -sV -oX -->'''

    # Create root element
    nmaprun = ET.Element("nmaprun", {
        "scanner": "nmap",
        "args": "nmap -sV -oX",
        "start": "123456789",
        "startstr": "Mon Nov 20 13:33:54 2023",
        "version": "7.94",
        "xmloutputversion": "1.05"
    })

    # Create scaninfo, verbose, and debugging elements
    scaninfo = ET.SubElement(nmaprun, "scaninfo", {
        "type": "syn",
        "protocol": "tcp",
        "numservices": "1000",
        "services": "1-65535"
    })
    ET.SubElement(nmaprun, "verbose", {"level": "0"})
    ET.SubElement(nmaprun, "debugging", {"level": "0"})

    # OS, services, and port mapping
    os_services = {
        "Linux": {"http": 80, "ssh": 22, "smtp": 25, "ftp": 21, "telnet": 23},
        "Windows": {"http": 80, "msrpc": 135, "netbios-ssn": 139, "rdp": 3389, "smb": 445},
        "Solaris": {"http": 80, "ssh": 22, "telnet": 23, "netbios-ssn": 139, "ftp": 21},
        "Darwin": {"http": 80, "netbios-ssn": 139, "ipp": 631, "afp": 548, "ssh": 22}
    }

    # Service products and versions
    service_info = {
        "http": {"product": "Apache httpd", "version": "2.4.41"},
        "ssh": {"product": "OpenSSH", "version": "8.0"},
        "smtp": {"product": "Postfix SMTP", "version": "3.4.8"},
        "ftp": {"product": "vsftpd", "version": "3.0.3"},
        "telnet": {"product": "Telnet Server", "version": "1.2"},
        "msrpc": {"product": "Microsoft RPC", "version": "5.0"},
        "netbios-ssn": {"product": "Samba smbd", "version": "4.10.10"},
        "rdp": {"product": "Microsoft Terminal Service", "version": "10.0"},
        "smb": {"product": "Microsoft SMB", "version": "3.1.1"},
        "ipp": {"product": "CUPS", "version": "2.3.0"},
        "afp": {"product": "Netatalk AFP", "version": "3.1.12"}
    }

    # Function to create a random IP address within the extended subnet range
    def random_ip(base_subnet, host_number):
        subnet_third_octet = host_number // 254
        host_fourth_octet = host_number % 254 + 1
        return f"{base_subnet}.{subnet_third_octet}.{host_fourth_octet}"

    # Generating hosts with updated IP address method
    for i in range(num_hosts):
        host_os = choice(list(os_services.keys()))

        host = ET.Element("host")
        ET.SubElement(host, "status", {"state": "up", "reason": "arp-response", "reason_ttl": "0"})
        ET.SubElement(host, "address", {"addr": random_ip(base_subnet, i), "addrtype": "ipv4"})
        ET.SubElement(host, "hostnames")

        # Ports
        ports = ET.SubElement(host, "ports")
        open_ports_count = randint(1, 5)  # Random number of open ports (1 to 5)
        services = sample(list(os_services[host_os].items()), open_ports_count)
        for service, port in services:
            port_element = ET.SubElement(ports, "port", {"protocol": "tcp", "portid": str(port)})
            ET.SubElement(port_element, "state", {"state": "open", "reason": "syn-ack", "reason_ttl": "64"})
            service_element = ET.SubElement(port_element, "service", {
                "name": service,
                "product": service_info[service]["product"],
                "version": service_info[service]["version"],
                "ostype": host_os
            })

        # OS element with osmatch
        os = ET.SubElement(host, "os")
        osclass = ET.SubElement(os, "osclass", {
            "type": "general purpose",
            "vendor": host_os,
            "osfamily": host_os,
            "osgen": "Unknown",  # OS generation can be set accordingly
            "accuracy": "98"
        })
        ET.SubElement(osclass, "cpe", text=f"cpe:/o:{host_os.lower()}:{host_os.lower()}")
        osmatch = ET.SubElement(os, "osmatch", {
            "name": f"{host_os} Generic Match",
            "accuracy": str(randint(90, 100)),
            "line": str(randint(1000, 2000))
        })
        ET.SubElement(osmatch, "osclass", {
            "type": "general purpose",
            "vendor": host_os,
            "osfamily": host_os,
            "osgen": "Unknown",
            "accuracy": "98"
        })

        nmaprun.append(host)

    # Runstats
    runstats = ET.SubElement(nmaprun, "runstats")
    ET.SubElement(runstats, "finished", {
        "time": "123456790",
        "timestr": "Mon Nov 20 13:34:10 2023",
        "summary": f"Nmap done; {num_hosts} IP addresses ({num_hosts} hosts up) scanned in 16.42 seconds",
        "elapsed": "16.42",
        "exit": "success"
    })
    ET.SubElement(runstats, "hosts", {
        "up": str(num_hosts),
        "down": "0",
        "total": str(num_hosts)
    })

    # Convert the XML to string
    xml_str = xml_header + '\n' + ET.tostring(nmaprun, encoding='unicode', method='xml')
    return xml_str

def save_nmap_xml(filename, num_hosts=1000, base_subnet="172.16"):
    # Generate the XML content
    xml_content = generate_nmap_xml(num_hosts, base_subnet)

    # Save the content to the specified file
    with open(filename, "w") as file:
        file.write(xml_content)

# Specify the filename and call the function to save the file
filename = "huge_nmap.xml"
save_nmap_xml(filename)
