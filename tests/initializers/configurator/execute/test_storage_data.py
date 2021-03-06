import pytest

from PyPWA.initializers.configurator.execute import _storage_data


@pytest.fixture()
def module_picking():
    return _storage_data.ModulePicking()


@pytest.fixture()
def templates():
    loader = _storage_data.Templates()
    return loader.get_templates()


def test_module_picking_can_find_builtin_parser(module_picking):
    found_plugin = module_picking.request_plugin_by_name("Builtin Parser")
    assert found_plugin is not None


def test_module_picking_can_find_shell_fitting_method(module_picking):
    found_plugin = module_picking.request_main_by_id("shell fitting method")
    assert found_plugin is not None


def test_template_is_dict(templates):
    assert isinstance(templates, dict)


def test_global_settings_in_templates(templates):
    assert "Global Options" in templates


def test_builtin_parser_in_templates(templates):
    assert "Builtin Parser" in templates
