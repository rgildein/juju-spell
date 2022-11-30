import pathlib
import sys
import textwrap

from craft_cli import (
    ArgumentParsingError,
    BaseCommand,
    CommandGroup,
    CraftError,
    Dispatcher,
    EmitterMode,
    ProvideHelpException,
    emit,
)


class RemoveFileCommand(BaseCommand):
    """Remove the indicated file."""

    name = "unlink"
    help_msg = "Remove the indicated file."
    overview = textwrap.dedent(
        """
        Remove the indicated file.

        A file needs to be indicated. It is an argument error if the path does not exist
        or it's a directory.

        It will return successfully if the file was properly removed.
    """
    )

    def fill_parser(self, parser):
        """Add own parameters to the general parser."""
        parser.add_argument("filepath", type=pathlib.Path, help="The file to be removed")

    def run(self, parsed_args):
        """Run the command."""
        if not parsed_args.filepath.exists() or parsed_args.filepath.is_dir():
            raise ArgumentParsingError("The indicated path is not a file or does not exist.")
        try:
            parsed_args.filepath.unlink()
        except Exception as exc:
            raise CraftError(f"Problem removing the file: {exc}.")

        emit.message("File removed successfully.")


emit.init(EmitterMode.BRIEF, "example-app", "Starting example app v1.")
command_groups = [CommandGroup("Basic", [RemoveFileCommand])]
summary = "Example application for the craft-cli tutorial."

try:
    dispatcher = Dispatcher("example-app", command_groups, summary=summary)
    dispatcher.pre_parse_args(sys.argv[1:])
    dispatcher.load_command(None)
    dispatcher.run()
except (ArgumentParsingError, ProvideHelpException) as err:
    print(err, file=sys.stderr)  # to stderr, as argparse normally does
    emit.ended_ok()
except CraftError as err:
    emit.error(err)
except KeyboardInterrupt as exc:
    error = CraftError("Interrupted.")
    error.__cause__ = exc
    emit.error(error)
except Exception as exc:
    error = CraftError(f"Application internal error: {exc!r}")
    error.__cause__ = exc
    emit.error(error)
else:
    emit.ended_ok()
