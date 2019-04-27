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
        """Initialise instance of Keybindings.

        :param parent: object calling self
        """
        # Get the file where the keybindings are stored
        bindings_path = pathlib.Path(__file__).parent / "keybindings.json"
        # Get the keybindings for the OS from the file
        with open(bindings_path) as f:
            self.bindings: Dict[str, BindingsDict] = json.load(f)[sys.platform]
        # The functions each action refers to
        self.functions: Dict[str, Callable] = {
            "stop": parent.stop,
            "switch_help": parent.switch_help,
            "switch_main": parent.switch_main,
            "undo": parent.core.undo_last_move,
            "redo": parent.core.redo_last_move,
            "focus_input": parent.focus_input,
        }
        # The parent whose keybindings these are
        # If the parent doesn't have the functions specified in
        # self.functions, bad things will happen
        self.parent = parent

        # For turning the bindings into something meaningful to the
        # bindings object
        def create_dict(code_set: BindingsDict) -> TupleDict:
            to_return = {}
            for x in code_set:
                action = self.functions[x['action']]
                key = CodeTuple(x['key'], frozenset(x['modifiers']))
                to_return[key] = action
            return to_return

        # Keybindings usable on any screen
        self.any_screen = create_dict(self.bindings['any_screen'])
        # Keybindings usable on the main screen
        self.main_screen = {
            **create_dict(self.bindings['main_screen']), **self.any_screen
        }
        # Keybindings usable on the help screen
        self.help_screen = {
            **create_dict(self.bindings['help_screen']), **self.any_screen
        }

    def key_action(
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
        # Set which bindings should be used, based on the current
        # screen type
        if self.parent.root.current == 'main':
            bindings = self.main_screen
        elif isinstance(self.parent.root.current_screen, HelpScreen):
            bindings = self.help_screen
        else:
            raise ValueError
        # Create the proper key for the dictionary
        key = CodeTuple(
            code_point if code_point is not None else key,
            frozenset(modifiers),
        )
        # Get the action from the dictionary, if it exists
        # Otherwise, do nothing
        try:
            action = bindings[key]
        except KeyError:
            return
        # Actually do whatever it is the person wanted
        action()
