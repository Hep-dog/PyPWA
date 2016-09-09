from PyPWA.core_libs.templates import configurator_templates

import pytest


def test_ShellCoreTemplate_MethodValues_RaiseNotImplementedError():
    test_shell = configurator_templates.ShellCoreTemplate()

    with pytest.raises(NotImplementedError):
        test_shell.make_config("this")

    with pytest.raises(NotImplementedError):
        test_shell.run("this")
