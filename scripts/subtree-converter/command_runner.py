#!/usr/bin/env python3
"""Command execution abstraction following Dependency Inversion Principle."""

import subprocess
from pathlib import Path
from typing import Protocol


class CommandResult:
    """Result of a command execution."""

    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Initialize command result.

        Args:
            returncode: Exit code of the command
            stdout: Standard output from command
            stderr: Standard error from command
        """
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        """Check if command was successful.

        Returns:
            True if returncode is 0, False otherwise
        """
        return self.returncode == 0


class CommandRunner(Protocol):
    """Protocol for command execution (Dependency Inversion Principle).

    This protocol defines the interface for running commands, allowing
    different implementations (subprocess, mock, etc.) without changing
    dependent code.
    """

    def run(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        check: bool = True,
        capture: bool = False,
    ) -> CommandResult:
        """Run a command.

        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command
            check: Whether to raise error on non-zero exit
            capture: Whether to capture stdout/stderr

        Returns:
            CommandResult with execution details

        Raises:
            CommandExecutionError: If check=True and command fails
        """
        ...


class SubprocessCommandRunner:
    """Concrete implementation using subprocess (Single Responsibility Principle)."""

    def run(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        check: bool = True,
        capture: bool = False,
    ) -> CommandResult:
        """Run a command using subprocess.

        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command
            check: Whether to raise error on non-zero exit
            capture: Whether to capture stdout/stderr

        Returns:
            CommandResult with execution details

        Raises:
            CommandExecutionError: If check=True and command fails
        """
        try:
            from .exceptions import CommandExecutionError
        except ImportError:
            from exceptions import CommandExecutionError

        kwargs: dict[str, object] = {"text": True}
        if cwd:
            kwargs["cwd"] = str(cwd)
        if capture:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE

        try:
            process = subprocess.run(cmd, **kwargs)  # type: ignore[call-overload]
        except subprocess.SubprocessError as e:
            if check:
                raise CommandExecutionError(f"Failed to execute {' '.join(cmd)}: {e}") from e
            return CommandResult(returncode=-1, stderr=str(e))

        result = CommandResult(
            returncode=process.returncode,
            stdout=process.stdout if capture else "",
            stderr=process.stderr if capture else "",
        )

        if check and not result.success:
            error_msg = f"Command failed ({result.returncode}): {' '.join(cmd)}"
            if result.stderr:
                error_msg += f"\n{result.stderr}"
            raise CommandExecutionError(error_msg)

        return result
