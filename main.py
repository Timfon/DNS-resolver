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

class cache_item:
    def __init__(self, answer):
        self.ans = answer
        self.time = time.time()

domain_cache = {}

def cache_answer(domain, answer):
    domain_cache[domain] = cache_item(answer)
    return None

def check_cache(domain):
    if domain in domain_cache:
        for rrset in domain_cache[domain].ans:
            if rrset.ttl < time.time() - domain_cache[domain].time:
                del domain_cache[domain]
                return None
        return domain_cache[domain].ans
    return None

def get_next_nameservers(response):
    """Extract next nameserver IP from response."""
    if response.additional:
        return [str(rr) for rrset in response.additional for rr in rrset if rr.rdtype == dns.rdatatype.A]
    
    if response.authority:
        names = [str(rr.target) for rrset in response.authority for rr in rrset if rr.rdtype == dns.rdatatype.NS]
        search_ip = []
        for name in names:
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 2
                answers = resolver.resolve(name, 'A')
                for answer in answers:
                    search_ip.append(str(answer.address))
            except Exception as e:
                print(f"Error resolving NS record: {e}")
                continue
        return search_ip
    return None

def single_step_query(domain, server):
    """Perform a single DNS query step without following referrals."""
    print(f"\nQuerying {server} for {domain}")
    query = dns.message.make_query(domain, "A")
    
    try:
        response = dns.query.udp(query, server, timeout=2)
        
        if response.answer:
            print("\nAnswer section:")
            cache_answer(domain, response.answer)
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
                
        return
        
    except Exception as e:
        print(f"Error querying {server}: {e}")
        return None

def full_iterative_query(domain, start_servers = ROOT_SERVERS):
    """Perform a full iterative DNS query, showing all steps."""
    print(f"\nStarting iterative resolution for {domain}")
    print(f"Step 1: Querying root servers")
    
    current_servers = start_servers
    step = 1

    cache_check = check_cache(domain)
    
    if cache_check:
        print("Got cached answer:")
        for rrset in cache_check:
            for rr in rrset:
                print(rrset.name, int(rrset.ttl - (time.time() - domain_cache[domain].time)),"IN", dns.rdatatype.to_text(rr.rdtype) , rr.address)
        return
    
    while True:
        for server in current_servers:
            print(f"\nQuerying server: {server}")         
            try:
                response = dns_query(server, domain)  
                if response.answer:
                    print("Got final answer:")
                    for rrset in response.answer:
                        print(rrset)
                    cache_answer(domain, response.answer)
                    return response
                
                if response.authority:
                    print("Authority section:")
                    for rrset in response.authority:
                        print(rrset)
                
                if response.additional:
                    print("Additional section:")
                    for rrset in response.additional:
                        print(rrset)
                
                next_servers = get_next_nameservers(response)
                if next_servers:
                    step += 1
                    print(f"\nStep {step}: Following referral to {next_servers}")
                    current_servers = next_servers
                    break
                else:
                    print("No next nameserver found in referral")
                    
            except Exception as e:
                print(f"Error querying {server}: {e}")
                return None
def dns_query(server, domain):
    query = dns.message.make_query(domain, "A")
    response = dns.query.udp(query, server, timeout=2)
    return response

def recursive_query(domain, servers):
    """Perform a recursive DNS query."""

    cache_check = check_cache(domain)

    if cache_check:
        print("Got cached answer:")
        for rrset in cache_check:
            for rr in rrset:
                print(rrset.name, int(rrset.ttl - (time.time() - domain_cache[domain].time)),"IN", dns.rdatatype.to_text(rr.rdtype) , rr.address)
        return
    for server in servers:
        print(f"Recursively querying {server} for {domain}")
        try:           
            response = dns_query(server, domain)
            if response.answer:
                print("Answer section:")
                for rr in response.answer:
                    print(rr)
                cache_answer(domain, response.answer)
                return response
            
            next_servers = get_next_nameservers(response)
            if next_servers:
                recursion =  recursive_query(domain, next_servers)
                if recursion:
                    return recursion
            else:
                print("No next nameservers found in referral")
                return None
                
        except Exception as e:
            print(f"Error during recursive query: {e}")
            return None

def print_usage():
    """Print usage instructions."""
    print("\nUsage:")
    print("  dig <domain>                    - Full recursive query from default root server 198.41.0.4")
    print("  dig <domain> -i                 - Full iterative query from default root server 198.41.0.4")
    print("  dig <domain> @<server> -r       - Full recursive query from specific server")
    print("  dig <domain> @<server> -i       - Full iterative query from specific server")
    print("  dig <domain> @<server>          - Single step query to specific server")
    print("  q                               - Quit the program")
    print("  ls                              - List the 13 root servers")

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
                #Default is the first root server for now
                recursive_query(domain, ROOT_SERVERS)
            elif len(query_components) == 3 and query_components[2] == "-i":
                # Full iterative query from root
                domain = query_components[1]
                full_iterative_query(domain, ROOT_SERVERS)
            elif len(query_components) >= 3 and query_components[2].startswith("@"):
                server = query_components[2][1:]  # remove @
                domain = query_components[1]
                if len(query_components) == 4 and query_components[3] == "-i":
                    # Recursive query from specific server
                    full_iterative_query(domain, [server])
                elif len(query_components) == 4 and query_components[3] == "-r":
                    # Recursive query from specific server
                    recursive_query(domain, [server])
                else:
                    # Single step query to specific server
                    single_step_query(domain, server)
            else:
                print_usage()
                continue
            print(f";; Query time: {time.time() - query_start:.3f} seconds")
        elif user_input.strip().lower() == "ls":
            print("Root servers:")
            for server in ROOT_SERVERS:
                print(f"  {server}")
        else:
            print_usage()
