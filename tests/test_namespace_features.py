import untangle


def test_namespace_processing_keeps_elements_text_and_sibling_order():
    document = untangle.parse(
        "<root><item>first</item><item>second</item></root>",
        feature_namespaces=True,
    )
    assert [item.cdata for item in document.root.item] == ["first", "second"]


def test_namespace_processing_uses_local_elements_and_qualified_attributes():
    document = untangle.parse(
        '<r:root xmlns:r="urn:root" xmlns:a="urn:first" xmlns:b="urn:second">'
        '<a:class a:id="1" b:id="2" id="3">text</a:class>'
        "</r:root>",
        feature_namespaces=True,
    )
    element = document.root.class_
    assert element.cdata == "text"
    assert element["a:id"] == "1"
    assert element["b:id"] == "2"
    assert element["id"] == "3"


def test_default_namespace_processing_keeps_child_structure():
    document = untangle.parse(
        '<root xmlns="urn:root"><item><value>ok</value></item></root>',
        feature_namespaces=True,
    )
    assert document.root.item.value.cdata == "ok"


def test_namespace_processing_disabled_retains_prefixed_names():
    document = untangle.parse('<r:root xmlns:r="urn:root"><r:item/></r:root>')
    assert document.r_root.r_item._name == "r_item"
