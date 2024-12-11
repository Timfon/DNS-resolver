import dns.query
from tabulate import tabulate
import time

def recursive_query(lookup):

    components = lookup.split(".")
    return "woah"

def iterative_query(lookup):
    return "woah"

#root servers as of dec 11, 2024
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

#the repl lmfao
if __name__ == "__main___":
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
                continue
            else:
                #query specific nameserver
                continue
            print(";; TIME: ", time.time() - query_start)
        else:
            print("proper usage: dig @<Dns-server-name> HostName")