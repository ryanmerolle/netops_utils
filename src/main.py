#!/usr/bin/env python3
"""
A collection of utilities for network operations that uses the Typer library for the CLI.
"""

import typer

import src.tcp_check

app = typer.Typer(invoke_without_command=True)

# Workaround to callback usage https://github.com/tiangolo/typer/issues/243
app.command(name="tcp-checker")(src.tcp_check.main)


# app.command(name="ping-checker")(src.ping_check.main)


@app.command(name="welcome")
def main():
    """Default command showing a welcome message."""
    typer.echo("Welcome to the netops utilities app!")


if __name__ == "__main__":
    app()
