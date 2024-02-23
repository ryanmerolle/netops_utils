"""
Utility script used by other scripts.
"""

import csv
import json
import logging
import logging.handlers
import os
import re
from datetime import datetime
from typing import Dict, Tuple

from colorlog import ColoredFormatter
from netutils import dns, ip, protocol_mapper
from rich import print_json
from rich.console import Console
from rich.table import Table

# TODO: Add support for writing to a Database - Maybe?
# TODO: Add support for Time series - Maybe?
# TODO: Refactor - possibly using classes
# TODO: Add tests
# TODO: Verify type hints used
# TODO: Verify docstrings are correct
# TODO: Check no duplicate inputs given field names
# TODO: Add support for database input
# TODO: Add support for JSON/YAML input


class RegexColoredFormatter(ColoredFormatter):
    """
    A custom formatter to apply different colors to log messages based on regex patterns.
    """

    def __init__(self, patterns_colors: Dict[str, str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.patterns_colors = {re.compile(pattern): color for pattern, color in patterns_colors.items()}

    def format(self, record: logging.LogRecord) -> str:
        original_message = record.msg
        for pattern, color in self.patterns_colors.items():
            if pattern.search(original_message):
                record.msg = f"{color}{original_message}\033[0m"
                break
        formatted_message = super().format(record)
        record.msg = original_message  # Restore original message
        return formatted_message


def get_ip_address(fqdn: str) -> str:
    """
    Returns the IP address for a given FQDN.
    """
    return dns.fqdn_to_ip(fqdn)


def setup_logging(verbose: bool, log_file_name: str, syslog: str = "", use_utc: bool = False) -> logging.Logger:
    """
    Sets up the logging system with custom formatting based on regex patterns.
    Writes logs to local disk and optionally to a remote syslog server.
    If use_utc is True, logging timestamps are in UTC. Otherwise, they are in local time.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if verbose else logging.WARNING)

    # Determine the time zone for the formatter
    if use_utc:
        logging.Formatter.converter = time.gmtime  # Use UTC time for log records

    patterns_colors = {
        "CREATED": "\033[34m",  # Blue
        "FAIL": "\033[31m",  # Red
        "REFUSED": "\033[92m",  # Light Green
        "SUCCESS": "\033[32m",  # Green
        "TIMEOUT": "\033[31m",  # Red
        "STARTED": "\033[34m",  # Blue
        "COMPLETED": "\033[34m",  # Blue
        "UNKNOWN": "\033[38;5;208m",  # Orange
    }

    colored_formatter = RegexColoredFormatter(
        patterns_colors,
        fmt="%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(colored_formatter)
    logger.addHandler(stream_handler)

    # File handler
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s"))
    logger.addHandler(file_handler)

    if syslog:
        address, port = syslog.split(":")
        syslog_handler = logging.handlers.SysLogHandler(address=(address, int(port)))
        syslog_handler.setFormatter(logging.Formatter("%(name)s: %(levelname)s %(message)s"))
        logger.addHandler(syslog_handler)

    logging.info("STARTED - TCP-CHECKER")

    return logger


def is_ip_address(address: str) -> bool:
    """
    Checks if a given string is a valid IP address.
    """
    return ip.is_ip(address)


def get_tcp_name_from_num(port: int) -> str:
    """
    Returns the protocol name for a given TCP port number.
    """
    return protocol_mapper.TCP_NUM_TO_NAME.get(port, "")


def get_tcp_num_from_name(name: str) -> int:
    """
    Returns the port number for a given protocol name.
    """
    return protocol_mapper.TCP_NAME_TO_NUM.get(name.upper(), 0)


def get_current_timestamp(use_utc: bool = False) -> str:
    """
    Returns the current timestamp in a specified format.
    """
    now = datetime.utcnow() if use_utc else datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def write_to_csv(file_path: str, headers: list, data: list) -> None:
    """
    Writes data to a CSV file.
    """
    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    logging.info(f"Data written to CSV file: {file_path}")


def read_from_csv(file_path: str) -> Tuple[list, list]:
    """
    Reads data from a CSV file and returns it as a list of dictionaries.
    """
    with open(file_path, mode="r", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        return list(csv_reader.fieldnames or []), list(csv_reader)


def ensure_directory_exists(directory: str) -> None:
    """
    Ensures the specified directory exists.
    """
    os.makedirs(directory, exist_ok=True)


def write_to_json(file_path: str, data) -> None:
    """
    Writes data to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

    logging.info(f"Data written to JSON file: {file_path}")


def pretty_print(data, is_json=False) -> None:
    """
    Pretty prints data. If is_json is True, prints as JSON, otherwise prints as a table.
    """
    if is_json:
        print_json(data)
    else:
        console = Console()

        table = Table(show_header=True, header_style="bold magenta")

        for i, header in enumerate(data[0]):
            if i == 0:  # If it's the first column
                table.add_column(header, style="bold")
            else:
                table.add_column(header)

        # Add rows to the table
        for row in data:
            cells = []
            for header, value in row.items():
                str_value = str(value)
                if header == "result":
                    if re.match("SUCCESS", str_value):
                        cells.append("[green]" + str_value + "[/green]")
                    elif re.match("UNKNOWN(.*)", str_value):
                        cells.append("[orange3]" + str_value + "[/orange3]")
                    elif re.match("REFUSED", str_value):
                        cells.append("[light_green]" + str_value + "[/light_green]")
                    elif re.match("TIMEOUT|FAILED|FAILURE", str_value):
                        cells.append("[red]" + str_value + "[/red]")
                    else:
                        cells.append(str_value)
                else:
                    cells.append(str_value)
            table.add_row(*cells)

        # Print the table to the console
        console.print(table)
