# netops-utils

A collection of NetOps utility scripts leveraging typer

## Getting Started

### Installation

While this package is not yet published on pypi, you need to install it from the source code.

```bash
# Use force to get the latest version and overwrite the existing installation
pip install git+https://github.com/ryanmerolle/netops-utils.git --force
```

### Usage

Show the help menu to see the available commands

```bash
$ netops-utils --help
                                                                                                                                    
 Usage: netops-utils [OPTIONS] COMMAND [ARGS]...                                                                                    
                                                                                                                                    
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                          │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                   │
│ --help                        Show this message and exit.                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ tcp-checker                  Runs the TCP port check.                                                                            │
│ welcome                      Default command showing a welcome message.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Show the help menu to see the available commands for tcp-checker

```bash
$ netops-utils tcp-checker --help
                                                                                                                                    
 Usage: netops-utils tcp-checker [OPTIONS] [FILE_NAME]                                                                              
                                                                                                                                    
 Runs the TCP port check.                                                                                                           
                                                                                                                                    
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   file_name      [FILE_NAME]  [default: remote_services.csv]                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --concurrency       -c       INTEGER RANGE [1<=x<=1000]  The maximum number of concurrent checks. [default: 100]                 │
│ --export_log_file   -el      TEXT                        Outputs logs to a log file. [default: tcp_checker.log]                  │
│ --export_json_file  -ej                                  Outputs results to a JSON file in a directory using the name of the     │
│                                                          input file.                                                             │
│ --print_json        -pj                                  Outputs JSON results to stdout.                                         │
│ --print_table       -pt                                  Outputs pretty table results to stdout.                                 │
│ --syslog            -s       TEXT                        Sends logs to a syslog host(IP or FQDN). Port can be provided with a    │
│                                                          :).                                                                     │
│ --utc-time          -u                                   Enables UTC time for the timestamp.                                     │
│ --verbose           -v                                   Enables verbose logging to stdout.                                      │
│ --help                                                   Show this message and exit.                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Run the tcp-checker

```bash
$ netops-utils tcp-checker ./tests/services.csv -v -pt
2024-02-23 02:45:37,774 - INFO     - STARTED - TCP-CHECKER
2024-02-23 02:45:37,781 - INFO     - UNKNOWN PORT - Jira-SSH-NAME - jira.com:UNKNOWN
2024-02-23 02:45:37,816 - INFO     - SUCCESS - Jira-HTTPS-NUM - jira.com:443
2024-02-23 02:45:37,817 - INFO     - SUCCESS - Jira-HTTPS-NAME - jira.com:HTTPS
2024-02-23 02:45:38,782 - INFO     - TIMEOUT - Jira-SSH-NUM - jira.com:22
2024-02-23 02:45:38,783 - INFO     - TIMEOUT - Jira-SSH-NAME - jira.com:SSH
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ host     ┃ ip             ┃ port_name ┃ port_number ┃ result       ┃ timestamp           ┃ service_name    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ jira.com │ 104.192.142.18 │ HTTPS     │ 443         │ SUCCESS      │ 2024-02-23 02:45:37 │ Jira-HTTPS-NAME │
│ jira.com │ 104.192.142.18 │ SSH       │ 22          │ TIMEOUT      │ 2024-02-23 02:45:37 │ Jira-SSH-NAME   │
│ jira.com │ 104.192.142.18 │ UNKNOWN   │ 0           │ UNKNOWN PORT │ 2024-02-23 02:45:37 │ Jira-SSH-NAME   │
└──────────┴────────────────┴───────────┴─────────────┴──────────────┴─────────────────────┴─────────────────┘
2024-02-23 02:45:38,818 - INFO     - Data written to CSV file: ./tests/services.csv
2024-02-23 02:45:38,818 - INFO     - COMPLETED - TCP-CHECKER
```
