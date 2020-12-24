""" Gooey extensions.

These extensions to gooey implement the following functionnality:

- Set keyboard accelerators for each of gooey's buttons.

- Listen to the target executable's stdout.

- Allow the value selected by the user in the UI to be transformed before being
  passed on to the target executable.

The extensions are implemented by monkey patching gooey's code. This
demonstrates the power of dynamic languages such as Python, but is not very
good programming manners. I should definitely submit a PR to gooey's author
whenever I find the time. """


from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional

from gooey.gui.processor import ProcessController
from gooey.gui.containers.application import GooeyApplication

import wx


gooey_frame: Optional[GooeyApplication] = None


def patch_method(module_name: str, cls_name: str, method_name: str):
    """ Decorator - Patch a method.

    The decorated method can access the original method through its own
    'original' attribute.

    For example::

        @patch_method('gooey.gui.containers.application', 'GooeyApplication', '__init__')
        def __init__(self: GooeyApplication, *args, **kwargs) -> None:
            ...
            __init__.original(self, *args, **kwargs)
            .... """
    def decorator(func):
        module = import_module(module_name)
        cls = getattr(module, cls_name)
        original_method = getattr(cls, method_name)
        setattr(cls, method_name, func)
        setattr(func, 'original', original_method)
        return func
    return decorator


@patch_method('gooey.gui.processor', 'ProcessController', 'run')
def run(self: ProcessController, command: str) -> None:
    """ Transform arguments passed to the target executable. """
    args = command.split()
    already_processed = False
    transformers = RegisterArgTransformer.transformers
    for i, arg in enumerate(args):
        if already_processed:
            already_processed = False
        elif arg in transformers and len(args) > i + 1:
            transformer = transformers[arg]
            args[i + 1] = transformer(args[i + 1])
            already_processed = True
    run.original(self, ' '.join(args))


@patch_method('gooey.gui.containers.application', 'GooeyApplication', '__init__')
def __init__(self: GooeyApplication, *args, **kwargs) -> None:
    """ Retrieve gooey window's wx.Frame + handle accelerators. """

    def handle_accelerators(event):
        accelerator = RegisterAccelerator.accelerators[event.GetId()]
        widget = getattr(self.footer, accelerator.widget)
        if widget.IsShown():
            accelerator.action(self)

    global gooey_frame
    gooey_frame = self
    __init__.original(self, *args, **kwargs)
    self.SetAcceleratorTable(
        wx.AcceleratorTable(
            [(accelerator.modifiers, accelerator.key, id)
             for id, accelerator in RegisterAccelerator.accelerators.items()]))
    self.Bind(wx.EVT_MENU, handle_accelerators)


@patch_method('gooey.gui.processor', 'ProcessController', '_extract_progress')
def _extract_progress(self: ProcessController, text: bytes) -> Any:
    """ Call all ``StdoutListener``'s registered. """
    text_str = text.decode()
    for listener in RegisterStdoutListener.listeners:
        listener(text_str)
    return _extract_progress.original(self, text)


StdoutListener = Callable[[str], None]


class RegisterStdoutListener:
    """ Register an stdout listener. """

    listeners: List[StdoutListener] = []

    def __init__(self, listener: StdoutListener):
        RegisterStdoutListener.listeners.append(listener)


@dataclass
class Accelerator:
    button: str
    modifiers: int
    key: int
    action: Callable[[GooeyApplication], None]
    widget: str


class RegisterAccelerator:
    """ Register a keyboard accelerator for one of gooey's buttons."""

    accelerators: Dict[int, Accelerator] = {}

    buttons = {
        'start': (GooeyApplication.onStart, 'start_button'),
        'restart': (GooeyApplication.onStart, 'restart_button'),
        'stop': (GooeyApplication.onStopExecution, 'stop_button'),
        'close': (GooeyApplication.onClose, 'close_button'),
        'cancel': (GooeyApplication.onCancel, 'cancel_button'),
        'edit': (GooeyApplication.onEdit, 'edit_button')
    }

    def __init__(self, button: str, modifiers: int, key: int):
        if button not in RegisterAccelerator.buttons:
            raise ValueError("Unknown button name", button)
        action, widget = RegisterAccelerator.buttons[button]
        RegisterAccelerator.accelerators[wx.Window.NewControlId()] = Accelerator(
            button, modifiers, key, action, widget)


ArgTransformer = Callable[[str], str]


class RegisterArgTransformer:
    """ Register an argument transformer.

    Rationale -- The argument to be passed to youtube-dl for the '--output'
    option differs from the value selected by the user in the UI, which is a
    directory, to which we need to append ``'\\%(title)s.%(ext)s``. We might
    consider transforming the argument by specifying a custom argparse action::

        from argparse import Action
        from gooey import Gooey

        class CustomAction(Action):

            def __call__(self, parser, namespace, values, option_string=None):
                # Perform some transformation on `values`
                setattr(namespace, self.dest, values)

        @Gooey
        def main():
            parser = argparse.ArgumentParser()
            parser.add_argument(..., action=CustomAction, ...)
            parser.parse_args()

    Except that this does not work when a target executable is specified in the
    Gooey decorator (``@Gooey(target='some executable'``), as argument parsing
    is then done by the executable, not by argparse, which means that the
    ``CustomAction`` instance is initialised, but never called.

    The only way to transform arguments in this case is to patch gooey's code,
    which is what we do here. """
    transformers: Dict[str, ArgTransformer] = {}

    def __init__(self, arg: str, transformer: ArgTransformer):
        RegisterArgTransformer.transformers[arg] = transformer


def set_gooey_window_title(title: str) -> None:
    """ Set gooey window's title.

    Note: this works only after ``parse_args()`` has been called and gooey's
    window is displayed. """
    if gooey_frame is not None:
        gooey_frame.SetTitle(title)
