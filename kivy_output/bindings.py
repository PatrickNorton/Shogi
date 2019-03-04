import json
import pathlib
import sys

from collections import namedtuple
from typing import Dict, List, Union, Callable

from .screens import HelpScreen

__all__ = [
    "Keybindings",
    "CodeTuple",
]


CodeTuple = namedtuple('CodeTuple', ['key', 'modifiers'])
BindingsDict = List[Dict[str, Union[str, List[str]]]]
TupleDict = Dict[CodeTuple, Callable]


class Keybindings:
    """The class to run all keybindings for the app.

    :ivar bindings: object containing all bindings
    :ivar functions: dict mapping functions to actions
    :ivar parent: "parent" of object
    """
    def __init__(self, parent):
        """Initialise instance of _Keybindings.

        :param parent: object calling self
        """
        bindings_path = pathlib.Path(__file__).parent / "keybindings.json"
        with open(bindings_path) as f:
            self.bindings: Dict[str, BindingsDict] = json.load(f)[sys.platform]
        self.functions: Dict[str, Callable] = {
            "stop": parent.stop,
            "switch_help": parent.switch_help,
            "switch_main": parent.switch_main,
            "undo": parent.core.undo_last_move,
            "redo": parent.core.redo_last_move,
            "focus_input": parent.focus_input,
        }
        self.parent = parent

        def create_dict(code_set: BindingsDict) -> TupleDict:
            to_return = {}
            for x in code_set:
                action = self.functions[x['action']]
                key = CodeTuple(x['key'], frozenset(x['modifiers']))
                to_return[key] = action
            return to_return

        self.any_screen = create_dict(self.bindings['any_screen'])
        self.main_screen = {
            **create_dict(self.bindings['main_screen']), **self.any_screen}
        self.help_screen = {
            **create_dict(self.bindings['help_screen']), **self.any_screen}

    def get_key(
            self,
            _instance,
            key: int,
            _scan_code: int,
            code_point: str,
            modifiers: List[str]
    ):
        """Keyboard binding code.

        This runs the keyboard shortcuts necessary to make the app
        run properly. Parameters starting with an underscore are not
        currently used, but passed into the function by kivy, so they
        must remain there.

        :param _instance: instance of window, unused and unknown
        :param key: integer of key pressed
        :param _scan_code: scanned code, unused
        :param code_point: text of pressed key
        :param modifiers: list of modifiers pressed in conjunction
        """
        if self.parent.root.current == 'main':
            bindings = self.main_screen
        elif isinstance(self.parent.root.current_screen, HelpScreen):
            bindings = self.help_screen
        else:
            raise ValueError
        key = CodeTuple(
            code_point if code_point is not None else key,
            frozenset(modifiers)
        )
        try:
            action = bindings[key]
        except KeyError:
            return
        action()
