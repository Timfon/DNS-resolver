import dns.message
import dns.query
import dns.resolver
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

def recursive_query(domain, server):
    """
    Perform a recursive DNS query by following referrals until an answer is found.
    The resolver does the work of following the chain of nameservers.
    """
    print(f"Recursively querying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    # Set recursion desired flag to true
    query.flags |= dns.flags.RD
    
    try:
        response = dns.query.udp(query, server, timeout=2)
        if response.answer:
            for rr in response.answer:
                print("Response answer:", rr)
            return response
            
        # If no answer and recursion available flag is not set,
        # the server doesn't support recursion
        if not (response.flags & dns.flags.RA):
            print(f"Server {server} does not support recursion")
            return None
            
        # Handle referrals by following authority/additional records
        if response.authority or response.additional:
            next_server = get_next_server(response)
            print(f"Referral to {next_server}")
            if next_server:
                return recursive_query(domain, next_server)
                
        print("No answer or referral found")
        return None
        
    except Exception as e:
        print(f"Error during recursive query: {e}")
        return None

def iterative_query(domain, server):
    """
    Perform an iterative DNS query where the client does the work.
    The server returns either an answer or a referral to other nameservers.
    """
    print(f"Iteratively querying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    # Set recursion desired flag to false
    query.flags &= ~dns.flags.RD
    
    try:
        response = dns.query.udp(query, server, timeout=2)
        
        # If we got an answer, we're done
        if response.answer:
            for rr in response.answer:
                print("Answer:", rr)
            return response
            
        # If we got a referral, return it so the caller can query the next server
        if response.authority or response.additional:
            print("Received referral to:")
            if response.authority:
                for rr in response.authority:
                    print(f"Authority: {rr}")
            if response.additional:
                for rr in response.additional:
                    print(f"Additional: {rr}")
            return response
            
        print("No answer or referral received")
        return None
        
    except Exception as e:
        print(f"Error during iterative query: {e}")
        return None
<D-x>
def get_next_server(response):
    """Helper function to extract next server from authority/additional records."""
    # First check additional records for glue records
    if response.additional:
        for rr in response.additional:
            for item in rr.items:
                if item.rdtype == dns.rdatatype.A:
                    return item.address

    # Then check authority records and resolve NS records
    if response.authority:
        for rr in response.authority:
            for item in rr.items:
                if item.rdtype == dns.rdatatype.NS:
                    ns_name = str(item)
                    try:
                        # Resolve the nameserver to get its IP
                        answers = dns.resolver.resolve(ns_name, 'A')
                        return str(answers[0])  # Return the first IP address
                    except Exception as e:
                        print(f"Could not resolve NS {ns_name}: {e}")
                        continue
    return None

def resolve_iteratively(domain, root_servers):
    """
    Resolve a domain iteratively by starting at root servers and following referrals.
    This demonstrates true iterative resolution.
    """
    current_servers = root_servers
    
    while current_servers:
        for server in current_servers:
            response = iterative_query(domain, server)
            if response and response.answer:
                return response
                
            # Get next set of servers to query from referral
            next_servers = []
            if response and (response.authority or response.additional):
                next_server = get_next_server(response)
                if next_server:
                    next_servers.append(next_server)
            
            if next_servers:
                current_servers = next_servers
                break
        else:
            print("No more servers to query")
            return None
    
    return None


def main():
    while True:
        user_input = input("> ")
        if user_input.strip().lower() == "q":
            print("Exiting")
            break

        if user_input.startswith("dig"):
            query_start = time.time()
            query_components = user_input.split()

            if len(query_components) < 2:
                print("Usage: dig <domain> [@server] [-i/-r]")
                continue

            domain = query_components[1]
            server = None
            query_type = "recursive"  # default to recursive

            # Parse command options
            for comp in query_components[2:]:
                if comp.startswith("@"):
                    server = comp[1:]  # remove @
                elif comp == "-i":
                    query_type = "iterative"
                elif comp == "-r":
                    query_type = "recursive"

            try:
                if query_type == "iterative":
                    if server:
                        # Single iterative query to specified server
                        print(f"Performing iterative query to {server} for {domain}")
                        response = iterative_query(domain, server)
                    else:
                        # Full iterative resolution starting from root
                        print(f"Performing full iterative resolution for {domain}")
                        response = resolve_iteratively(domain, ROOT_SERVERS)
                else:  # recursive
                    if not server:
                        # Default to system's configured DNS server (e.g., 8.8.8.8)
                        server = "8.8.8.8"
                    print(f"Performing recursive query to {server} for {domain}")
                    response = recursive_query(domain, server)

                if response and response.answer:
                    print("\nFinal Answer:")
                    for rr in response.answer:
                        print(rr)
                else:
                    print("No answer found")

            except Exception as e:
                print(f"Error processing query: {e}")

            finally:
                print(f";; Query time: {(time.time() - query_start):.3f} seconds")
        else:
            print("Usage: dig <domain> [@server] [-i/-r]")
            print("Examples:")
            print("  dig example.com @8.8.8.8 -r    # recursive query to 8.8.8.8")
            print("  dig example.com -i             # full iterative resolution from root")
            print("  dig example.com @1.1.1.1 -i    # single iterative query to 1.1.1.1")
            print("  dig example.com                # recursive query to default resolver")

if __name__ == "__main__":
    main()
