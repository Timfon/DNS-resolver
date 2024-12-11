import dns.message
from tabulate import tabulate
import time

def recursive_query(lookup):
    return "woah"

def iterative_query(lookup):
    print(dns.message.make_query(lookup[1]))
    return "woah"


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
                iterative_query(query_components[1:])
                continue
            else:
                #query specific nameserver
                iterative_query(query_components[1:])
                continue
            print(";; TIME: ", time.time() - query_start)
        else:
            print("proper usage: dig @<Dns-server-name> HostName")