from argparse import _MutuallyExclusiveGroup, Action, HelpFormatter, PARSER
from collections.abc import Iterable


class MainHelpFormatter(HelpFormatter):
    """_summary_"""

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[Action],
        groups: Iterable[_MutuallyExclusiveGroup],
        prefix: str | None = None,
    ) -> None:
        return super().add_usage(usage, actions, groups, prefix)

    # def _format_usage(self, usage: str | None, actions: Iterable[Action], groups: Iterable[_MutuallyExclusiveGroup], prefix: str | None) -> str:
    #     print(usage)
    #     return super()._format_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        parts = super()._format_action(action)
        if action.nargs == PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

    def start_section(self, heading):
        if heading == "options":
            heading = "Options"
        return super().start_section(heading)
