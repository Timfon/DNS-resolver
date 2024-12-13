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

def get_nameserver_from_response(response):
    """Extract next nameserver IP from additional records, or resolve NS record if needed."""
    # First check additional records for immediate IP addresses
    if response.additional:
        for rrset in response.additional:
            if rrset.rdtype == dns.rdatatype.A:
                return str(rrset[0])
    
    # If no additional records, check authority section for NS records
    if response.authority:
        for rrset in response.authority:
            if rrset.rdtype == dns.rdatatype.NS:
                # Resolve the NS record to get its IP
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

def recursive_query(domain, server):
    """Perform a recursive DNS query."""
    print(f"Recursively querying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    try:
        response = dns.query.udp(query, server, timeout=2)
        
        # If we have an answer, we're done
        if response.answer:
            for rr in response.answer:
                print(rr)
            return response
        
        # Get next nameserver to query
        next_server = get_nameserver_from_response(response)
        if next_server:
            print(f"Following referral to {next_server}")
            return recursive_query(domain, next_server)
        else:
            print("No next nameserver found in referral")
            return None
            
    except Exception as e:
        print(f"Error during recursive query: {e}")
        return None

def iterative_query(domain, server):
    """Perform an iterative DNS query."""
    print(f"Iteratively querying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    try:
        response = dns.query.udp(query, server, timeout=2)
        if response.answer:
            for rr in response.answer:
                print(rr)
        elif response.authority:
            for rr in response.authority:
                print(rr)
        if response.additional:
            for rr in response.additional:
                print(rr)
        return response
    except Exception as e:
        print(f"Error during iterative query: {e}")
        return None

if __name__ == "__main__":
    while True:
        user_input = input("> ")
        if user_input.strip().lower() == "q":
            print("Exiting")
            break
        elif user_input.startswith("dig"):
            query_start = time.time()
            query_components = user_input.split()
            if len(query_components) == 2:
                # Iteratively query all root servers
                domain = query_components[1]
                for server in ROOT_SERVERS:
                    print(f"\nQuerying root server {server} for {domain}")
                    iterative_query(domain, server)
            elif len(query_components) == 3:
                # Query specific nameserver
                server = query_components[1][1:]  # remove @
                domain = query_components[2]
                print(f"\nQuerying {server} for {domain}")
                recursive_query(domain, server)
            else:
                print("Usage: dig @<server> <domain>")
                continue
            print(f";; Query time: {time.time() - query_start:.3f} seconds")
        else:
            print("Usage: dig @<server> <domain> or dig <domain>")
