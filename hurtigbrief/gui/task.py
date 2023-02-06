# A latex task.

from ..abstraction.letter import Letter
from ..abstraction.design import Design
from ..latex.mklatex import do_latex
from ..latex.workspace import Workspace
from ..latex.preamblecache import PreambleCache
from .types import TemplateName
from .gtk import GObject
from .notify import Notify
from threading import Thread

class LatexTask(Thread):
    """
    A latex compilation job executed in a separate thread.
    """
    def __init__(self, letter: Letter, design: Design, template: TemplateName,
                 workspace: Workspace, preamble_cache: PreambleCache):
        super().__init__(daemon=True)
        self.letter = letter
        self.design = design
        self.template = template
        self.workspace = workspace
        self.preamble_cache = preamble_cache
        self.notify = Notify()

    def run(self):
        do_latex(self.letter, self.design, self.template, self.workspace,
                 self.preamble_cache)
        self.notify.emit_result("The result")
