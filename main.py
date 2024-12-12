import dns.message
import dns.query
from tabulate import tabulate
import time

ROOT_SERVERS = ( "198.41.0.4", 
                 "170.247.170.2", 
                 "192.33.4.12", 
                 "199.7.91.13", 
                 "192.203.230.10",
                 "192.5.5.241", 
                 "192.112.36.4", 
                 "198.97.190.53", 
                 "192.36.148.17", 
                 "192.58.128.30", 
                 "193.0.14.129", 
                 "199.7.83.42", 
                 "202.12.27.33")

def recursive_query(lookup):
    return "woah"

def domain_lookup(lookup, server):
    query = dns.message.make_query(lookup, "A")
    udp = dns.query.udp(query, server, timeout = 2)
    return udp

def recursive_query(lookup, servers = ROOT_SERVERS):
    answers = []
    next_servers = []
    for server in servers:
        response = domain_lookup(lookup, server)
        if response.answer:
            return response.answer
        if response.additional:
            for add in response.additional:
                for rr in add:
                    if rr.rdtype == dns.rdatatype.A:
                        next_servers.append(str(rr.address))
    if next_servers:
        return recursive_query(lookup, next_servers) 
    else:
        raise Exception("No servers available for resolution") 

#the repl lmfao
if __name__ == "__main__":
    #stuff here
    while True:
        user_input = input("> ")
        if user_input == "q":
            print("Exiting")
            break
        elif user_input[:4] == "dig ":
            query_start = time.time()
            query_components = user_input.split(" ")
            if len(query_components) == 1:
                print("dig @<Dns-server-name> HostName")
                continue
            elif len(query_components) == 2:
                #dns-server-name not included - iterate over all nameservers
                recursive_query(query_components[1])
                continue
            else:
                #query specific nameserver
                #iterative_query(query_components[1:])
                continue
            print(";; TIME: ", time.time() - query_start)
        else:
            print("proper usage: dig @<Dns-server-name> HostName")