# DNS Query Tool

A Python-based DNS query tool that allows you to perform different types of DNS queries (recursive, iterative, and single-step) to explore how DNS resolution works. This tool provides functionality similar to the `dig` command but with more verbose output.

## Features

- Full recursive DNS queries starting from root servers
- Full iterative DNS queries showing step-by-step resolution
- Single-step queries to specific nameservers
- Built-in list of root DNS servers
- Detailed output showing answer, authority, and additional sections
- Query time measurement
- Support for custom nameserver specification

## Requirements

- Python 3.x
- dnspython library (`pip install dnspython`)

## Installation

1. Install the required dependency:
```bash
pip install dnspython
```

2. Save the script to a file (e.g., `dns_tool.py`)

## Usage

Run the script (python3 main.py) and use one of the following commands:

```
dig <domain>                    - Full recursive query from default root server 198.41.0.4
dig <domain> -i                 - Full iterative query from default root server 198.41.0.4
dig <domain> @<server> -r       - Full recursive query from specific server
dig <domain> @<server> -i       - Full iterative query from specific server
dig <domain> @<server>          - Single step query to specific server
ls                             - List the 13 root servers
q                              - Quit the program
```

### Examples

1. Perform a recursive query for example.com:
```
> dig example.com
```

2. Perform an iterative query for example.com:
```
> dig example.com -i
```

3. Query a specific root nameserver:
```
> dig example.com @198.41.0.4
```

4. Perform a recursive query from a specific root nameserver:
```
> dig example.com @192.33.4.12 -r
```

## Output

The tool provides detailed output for each query, including:
- Answer section (if available)
- Authority section (showing referrals to other nameservers)
- Additional section (containing glue records)
- Query time in seconds

## Functions

- `single_step_query(domain, server)`: Performs a single DNS query to a specific server
- `full_iterative_query(domain, start_server)`: Performs a full iterative resolution showing all steps
- `recursive_query(domain, server)`: Performs a recursive DNS query
- `get_next_nameserver(response)`: Extracts the next nameserver IP from a DNS response

## Error Handling

The tool includes error handling for:
- DNS query timeouts (2-second timeout)
- Failed nameserver resolutions
- General DNS query errors

Each error is logged to the console with an appropriate error message.
