import dns.query
from tabulate import tabulate
import time

def recursive_query(lookup):

    components = lookup.split(".")
    return "woah"

def iterative_query(lookup):
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
                continue
            else:
                #query specific nameserver
                continue
            print(";; TIME: ", time.time() - query_start)
        else:
            print("proper usage: dig @<Dns-server-name> HostName")