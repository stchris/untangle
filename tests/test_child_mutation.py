import pytest

import untangle


def test_added_child_is_visible_after_attribute_lookup():
    root = untangle.parse('<root><item id="1"/></root>').root
    first = root.item
    second = untangle.Element("item", {"id": "2"})
    root.add_child(second)
    assert isinstance(root.item, list)
    assert root.item[0] is first
    assert root.item[1] is second


def test_removed_children_are_not_returned_from_attribute_lookup():
    root = untangle.parse('<root><item id="1"/><item id="2"/></root>').root
    original = root.item
    root.children.pop()
    assert root.item is original[0]
    root.children.clear()
    with pytest.raises(AttributeError):
        _ = root.item


def test_xml_names_do_not_overwrite_element_storage():
    root = untangle.parse('<root><children/><cdata/><_name/></root>').root
    assert isinstance(root.children, list)
    assert root.cdata == ""
    assert root._name == "root"
