"""
core/checklist_receipt.py — Checklist-style receipt.

A Receipt subclass whose body renders as a bulleted task list
instead of word-wrapped description text.
"""

from core.receipt import BODY_LINES, Receipt, Priority


class ChecklistReceipt(Receipt):
    """A receipt whose body is a bulleted checklist instead of wrapped text."""

    def __init__(
        self,
        title: str,
        tasks: list[str],
        priority: int = Priority.HIGH,
        printer_name: str = "POS-80",
    ) -> None:
        super().__init__(title, "", priority, printer_name)
        self.tasks  = tasks
        self.bullet = "•"

    def _body_lines(self) -> list[str]:
        body = []
        for task in self.tasks:
            body.append(f"{self.bullet} {task}")
            body.append("")

        blank      = BODY_LINES - len(body)
        top_pad    = blank // 3
        bottom_pad = blank - top_pad
        return [""] * top_pad + body + [""] * bottom_pad
