#!/usr/bin/env python3
"""
A simple TCP port check script that uses asyncio to check the availability of targets.
"""

import asyncio
from typing import Tuple

import typer
from typing_extensions import Annotated

from src.utils import (
    ensure_directory_exists,
    get_current_timestamp,
    get_ip_address,
    get_tcp_name_from_num,
    get_tcp_num_from_name,
    is_ip_address,
    pretty_print,
    read_from_csv,
    setup_logging,
    write_to_csv,
    write_to_json,
)

# TODO: Record IP, FQDN, etc during async task instead of at the end
# TODO: Refactor - possibly using classes
# TODO: Add tests
# TODO: Verify type hints used
# TODO: Verify docstrings are correct
# TODO: Add an option to loop/interval

INPUT_FILE = "remote_services.csv"
LOG_FILE = "tcp_checker.log"

app = typer.Typer()


async def check_port(service: dict, logging, semaphore: asyncio.Semaphore, duration=1, delay=1) -> Tuple[dict, str]:
    """
    Asynchronously checks the availability of a TCP port for a given service.

    Args:
        service (dict): A dictionary containing service details including service_name, host, and port.
        semaphore (asyncio.Semaphore): A semaphore to limit the number of concurrent tasks.
        duration (int, optional): The duration within which the port check should be completed. Defaults to 1 second.
        delay (int, optional): The delay before retrying in case of failure. Defaults to 1 second.

    Returns:
        tuple: Returns a tuple containing the service dictionary and the status string:
        ("SUCCESS", "TIMEOUT", "REFUSED", or "FAILURE").
    """
    async with semaphore:  # Use the semaphore to limit concurrency
        host = service["host"]
        port = service["port"]
        try:
            port_number = int(port)
        except ValueError:
            port_number = int(get_tcp_num_from_name(port))
            if port_number == 0:
                status = "UNKNOWN PORT"
                if service["service_name"] != "":
                    logging.info(f"{status} - {service['service_name']} - {host}:{port}")
                else:
                    logging.info(f"{status} - {host}:{port}")
                return service, status

        try:
            await asyncio.wait_for(asyncio.open_connection(host, port_number), timeout=duration)
            status = "SUCCESS"
        except asyncio.TimeoutError:
            status = "TIMEOUT"
        except ConnectionRefusedError:
            status = "REFUSED"
        except Exception as e:
            status = f"FAILURE - Error: {e}"
            await asyncio.sleep(delay)

        if service["service_name"] != "":
            logging.info(f"{status} - {service['service_name']} - {host}:{port}")
        else:
            logging.info(f"{status} - {host}:{port}")
        return service, status


def build_results_dict(
    results: list,
    new_header: str,
    file_name: str,
    print_json: bool,
    json_file: bool,
    print_table,
    timestamp,
) -> None:
    """
    Builds a dictionary from the results and writes it to a JSON file.

    Args:
        results (list): A list of tuples containing service dictionaries and their check statuses.
        new_header (str): The header string representing the current timestamp.
        file_name (str): The base file name for the JSON output.

    """
    latest_results = []
    for service, status in results:
        host = service["host"]
        if is_ip_address(host):
            ip = host
        else:
            ip = get_ip_address(service["host"])
        port = service["port"]
        try:
            port_number = int(port)
            port_name = get_tcp_name_from_num(port_number)
        except ValueError:
            port_number = get_tcp_num_from_name(port)
            port_name = port
            result = {
                "host": service["host"],
                "ip": ip,
                "port_name": port_name,
                "port_number": port_number,
                "result": status,
                "timestamp": timestamp,
            }
            if service["service_name"] != "":
                result["service_name"] = service["service_name"]
            latest_results.append(result)

    if print_json:
        pretty_print(latest_results, is_json=True)
    if print_table:
        pretty_print(latest_results)
    if json_file:
        directory_name = file_name.rsplit(".", 1)[0]
        ensure_directory_exists(directory_name)
        write_to_json(f"{directory_name}/{new_header}.json", latest_results)


async def async_main(
    file_name: str,
    verbose: bool,
    json_file: bool,
    log_file: str,
    syslog_target: str,
    print_json: bool,
    print_table: bool,
    timestamp: str,
    concurrency: int,  # Add concurrency parameter
) -> None:
    logging = setup_logging(verbose, log_file, syslog_target)

    headers, services = read_from_csv(file_name)

    semaphore = asyncio.Semaphore(concurrency)  # Create a semaphore with the concurrency limit

    tasks = [check_port(service, logging, semaphore) for service in services]
    results = await asyncio.gather(*tasks)

    new_header = timestamp
    if new_header not in headers:
        headers.append(new_header)

    for service, status in results:
        service[new_header] = status

    build_results_dict(results, new_header, file_name, print_json, json_file, print_table, timestamp)
    write_to_csv(file_name, headers, services)
    logging.info("COMPLETED - TCP-CHECKER")


@app.command()
def main(
    concurrency: int = typer.Option(
        100,
        "--concurrency",
        "-c",
        help="The maximum number of concurrent checks.",
        min=1,
        max=1000,
    ),  # Add concurrency option
    file_name: Annotated[str, typer.Argument()] = INPUT_FILE,
    log_file: str = typer.Option(LOG_FILE, "--export_log_file", "-el", help="Outputs logs to a log file."),
    json_file: bool = typer.Option(
        False,
        "--export_json_file",
        "-ej",
        help="Outputs results to a JSON file in a directory using the name of the input file.",
    ),
    print_json: bool = typer.Option(False, "--print_json", "-pj", help="Outputs JSON results to stdout."),
    print_table: bool = typer.Option(False, "--print_table", "-pt", help="Outputs pretty table results to stdout."),
    syslog_target: str = typer.Option(
        "",
        "--syslog",
        "-s",
        help="Sends logs to a syslog host(IP or FQDN). Port can be provided with a :).",
    ),
    use_utc: bool = typer.Option(False, "--utc-time", "-u", help="Enables UTC time for the timestamp."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enables verbose logging to stdout."),
) -> None:
    """
    Runs the TCP port check.
    """
    asyncio.run(
        async_main(
            file_name,
            verbose,
            json_file,
            log_file,
            syslog_target,
            print_json,
            print_table,
            get_current_timestamp(use_utc),
            concurrency,  # Pass the concurrency limit to async_main
        )
    )


# Allows us to run the script on its own
if __name__ == "__main__":
    app()
