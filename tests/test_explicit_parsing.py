"""Explicit entry points never guess the kind of their input."""

import os
import xml.sax
from io import BytesIO
from unittest import mock

import defusedxml.common
import pytest

import untangle


def test_xml_string_does_not_inspect_paths_or_fetch_urls():
    text = "é" * 40_000
    with (
        mock.patch("os.path.exists", side_effect=AssertionError("path lookup")),
        mock.patch("os.path.isfile", side_effect=AssertionError("path lookup")),
        mock.patch("urllib.request.urlopen", side_effect=AssertionError("URL fetch")),
    ):
        result = untangle.parse_xml_string(f"<root>{text}</root>")
    assert result.root.cdata == text


@pytest.mark.parametrize(
    "value", ["tests/res/pom.xml", "https://example.invalid/x.xml"]
)
def test_xml_string_does_not_treat_text_as_another_input_kind(value):
    with (
        mock.patch("urllib.request.urlopen", side_effect=AssertionError("URL fetch")),
        pytest.raises(xml.sax.SAXParseException),
    ):
        untangle.parse_xml_string(value)


@pytest.mark.parametrize("value", ["", " \n\t "])
def test_empty_xml_string(value):
    with pytest.raises(ValueError):
        untangle.parse_xml_string(value)


@pytest.mark.parametrize("value", [None, b"<root/>", 1])
def test_xml_string_requires_text(value):
    with pytest.raises(TypeError):
        untangle.parse_xml_string(value)


@pytest.mark.parametrize("path_type", [str, os.fsencode, lambda path: path])
def test_file_parses_paths_and_preserves_declared_encoding(tmp_path, path_type):
    path = tmp_path / "document.xml"
    path.write_bytes(b'<?xml version="1.0" encoding="iso-8859-1"?><root>caf\xe9</root>')
    with mock.patch("urllib.request.urlopen", side_effect=AssertionError("URL fetch")):
        result = untangle.parse_file(path_type(path))
    assert result.root.cdata == "café"
    path.unlink()  # The entry point releases its file handle.


def test_missing_file_is_not_parsed_as_xml(tmp_path):
    with pytest.raises(FileNotFoundError):
        untangle.parse_file(str(tmp_path / "missing.xml"))


def test_file_requires_path_not_file_descriptor():
    with pytest.raises(TypeError):
        untangle.parse_file(0)


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_url_fetches_without_checking_filesystem(scheme):
    url = f"{scheme}://example.invalid/document.xml"
    response = BytesIO(b"<root>remote</root>")
    with (
        mock.patch("urllib.request.urlopen", return_value=response) as urlopen,
        mock.patch("os.path.exists", side_effect=AssertionError("path lookup")),
        mock.patch("os.path.isfile", side_effect=AssertionError("path lookup")),
    ):
        result = untangle.parse_url(url)
    urlopen.assert_called_once_with(url)
    assert result.root.cdata == "remote"
    assert response.closed


@pytest.mark.parametrize(
    "value", [None, "", "tests/res/pom.xml", "<root/>", "file:///document.xml"]
)
def test_url_rejects_other_input_kinds(value):
    with (
        mock.patch("urllib.request.urlopen", side_effect=AssertionError("URL fetch")),
        pytest.raises(ValueError),
    ):
        untangle.parse_url(value)


@pytest.fixture(params=["parse_xml_string", "parse_file", "parse_url"])
def explicit_parser(request, tmp_path, monkeypatch):
    parse = getattr(untangle, request.param)

    def parse_document(document, **features):
        if request.param == "parse_file":
            path = tmp_path / "document.xml"
            path.write_text(document, encoding="utf-8")
            return parse(path, **features)
        if request.param == "parse_url":
            monkeypatch.setattr(
                "urllib.request.urlopen", lambda url: BytesIO(document.encode("utf-8"))
            )
            return parse("https://example.invalid/document.xml", **features)
        return parse(document, **features)

    return parse_document


def test_explicit_parsers_accept_sax_features(explicit_parser):
    result = explicit_parser("<root>text</root>", feature_string_interning=True)
    assert result.root.cdata == "text"


def test_explicit_parsers_reject_unknown_sax_features(explicit_parser):
    with pytest.raises(AttributeError):
        explicit_parser("<root/>", invalid_feature=True)


@pytest.mark.parametrize("external_ges", [False, True])
def test_explicit_parsers_forbid_entities(explicit_parser, external_ges):
    with pytest.raises(defusedxml.common.EntitiesForbidden):
        explicit_parser(
            '<!DOCTYPE root [<!ENTITY e "expanded">]><root>&e;</root>',
            feature_external_ges=external_ges,
        )


def test_explicit_parsers_forbid_external_dtds(explicit_parser):
    with pytest.raises(defusedxml.common.ExternalReferenceForbidden):
        explicit_parser('<!DOCTYPE root SYSTEM "file:///no-such.dtd"><root/>')


def test_url_releases_response_on_parse_failure():
    response = BytesIO(b"<unclosed>")
    with (
        mock.patch("urllib.request.urlopen", return_value=response),
        pytest.raises(xml.sax.SAXParseException),
    ):
        untangle.parse_url("https://example.invalid/document.xml")
    assert response.closed
