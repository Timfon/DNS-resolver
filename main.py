import dns.query
from tabulate import tabulate
import time

def recursive_query(lookup):

    components = lookup.split(".")
    return "woah"

def iterative_query(lookup):
    return "woah"


#the repl lmfao
def main():
    #stuff here
    while True:
        user_input = input("Enter Query: ")
        if user_input == "q":
            print("Exiting")
            break
        else:
            query_start = time.time()
            print(";; ANSWER")
            queried = [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]
            print(tabulate(queried, tablefmt="plain"))
            print(";; TIME: ", time.time() - query_start)

            

main()