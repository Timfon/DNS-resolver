import dns.message
import dns.query
import dns.resolver
import dns.rdatatype
import time

ROOT_SERVERS = (
    "198.41.0.4",
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
    "202.12.27.33",
)

def get_next_nameserver(response):
    """Extract next nameserver IP from response."""
    if response.additional:
        for rrset in response.additional:
            if rrset.rdtype == dns.rdatatype.A:
                return str(rrset[0])
    
    if response.authority:
        for rrset in response.authority:
            if rrset.rdtype == dns.rdatatype.NS:
                try:
                    ns_name = str(rrset[0])
                    resolver = dns.resolver.Resolver()
                    resolver.timeout = 2
                    answers = resolver.resolve(ns_name, 'A')
                    return str(answers[0])
                except Exception as e:
                    print(f"Error resolving NS record: {e}")
                    continue
    return None

def single_step_query(domain, server):
    """Perform a single DNS query step without following referrals."""
    print(f"\nQuerying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    
    try:
        response = dns.query.udp(query, server, timeout=2)
        
        if response.answer:
            print("\nAnswer section:")
            for rrset in response.answer:
                print(rrset)
        
        if response.authority:
            print("\nAuthority section:")
            for rrset in response.authority:
                print(rrset)
        
        if response.additional:
            print("\nAdditional section:")
            for rrset in response.additional:
                print(rrset)
                
        return response
        
    except Exception as e:
        print(f"Error querying {server}: {e}")
        return None

def full_iterative_query(domain, start_server):
    """Perform a full iterative DNS query, showing all steps."""
    print(f"\nStarting iterative resolution for {domain}")
    print(f"Step 1: Querying root server {start_server}")
    
    current_server = start_server
    step = 1
    
    while True:
        print(f"\nQuerying server: {current_server}")
        query = dns.message.make_query(domain, "A")
        
        try:
            response = dns.query.udp(query, current_server, timeout=2)
            
            if response.answer:
                print("Got final answer:")
                for rrset in response.answer:
                    print(rrset)
                return response
            
            if response.authority:
                print("Authority section:")
                for rrset in response.authority:
                    print(rrset)
            
            if response.additional:
                print("Additional section:")
                for rrset in response.additional:
                    print(rrset)
            
            next_server = get_next_nameserver(response)
            if next_server:
                step += 1
                print(f"\nStep {step}: Following referral to {next_server}")
                current_server = next_server
            else:
                print("No next nameserver found in referral")
                return None
                
        except Exception as e:
            print(f"Error querying {current_server}: {e}")
            return None

def recursive_query(domain, server):
    """Perform a recursive DNS query."""
    print(f"Recursively querying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    try:
        response = dns.query.udp(query, server, timeout=2)
        
        if response.answer:
            print("Answer section:")
            for rr in response.answer:
                print(rr)
            return response
        
        next_server = get_next_nameserver(response)
        if next_server:
            print(f"Following referral to {next_server}")
            return recursive_query(domain, next_server)
        else:
            print("No next nameserver found in referral")
            return None
            
    except Exception as e:
        print(f"Error during recursive query: {e}")
        return None

def print_usage():
    """Print usage instructions."""
    print("\nUsage:")
    print("  dig <domain>                    - Full iterative query from root")
    print("  dig @<server> <domain>          - Single step query to specific server")
    print("  dig @<server> <domain> -r       - Recursive query from specific server")
    print("  q                               - Quit the program")

if __name__ == "__main__":
    print_usage()
    while True:
        user_input = input("> ")
        if user_input.strip().lower() == "q":
            print("Exiting")
            break
        elif user_input.startswith("dig"):
            query_start = time.time()
            query_components = user_input.split()
            
            if len(query_components) == 2:
                # Full iterative query from root
                domain = query_components[1]
                full_iterative_query(domain, ROOT_SERVERS[0])
            elif len(query_components) >= 3 and query_components[1].startswith("@"):
                server = query_components[1][1:]  # remove @
                domain = query_components[2]
                
                if len(query_components) == 4 and query_components[3] == "-r":
                    # Recursive query from specific server
                    recursive_query(domain, server)
                else:
                    # Single step query to specific server
                    single_step_query(domain, server)
            else:
                print_usage()
                continue
            print(f";; Query time: {time.time() - query_start:.3f} seconds")
        else:
            print_usage()
