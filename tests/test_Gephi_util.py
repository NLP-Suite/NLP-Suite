"""Gephi: the gexf dates are ISO yyyy-mm-dd, so Gephi can open the SVO network graphs.

create_gexf declares timeformat="date", which GEXF defines as ISO yyyy-mm-dd, but wrote spells as mm-dd-yyyy.
Gephi 0.10+ refuses the file: DateTimeParseException: Text '11-15-2026' could not be parsed.
"""

import os
import re
import sys
import types
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET


def _lxml_or_stand_in():
    """lxml if it is installed; CI installs only pytest, so otherwise the stdlib ElementTree with the two lxml-only
    keywords create_gexf passes (nsmap, pretty_print) dropped. Writing a gexf needs nothing else from lxml."""
    try:
        import lxml  # noqa: F401
        from lxml import etree  # noqa: F401

        return {}
    except ImportError:
        stand_in = types.SimpleNamespace(
            Element=lambda tag, attrib=None, nsmap=None, **extra: ET.Element(tag, attrib or {}, **extra),
            SubElement=ET.SubElement,
            tostring=lambda element, pretty_print=False, **kwargs: ET.tostring(element, **kwargs),
        )
        return {"lxml": types.SimpleNamespace(etree=stand_in), "lxml.etree": stand_in}


def test_svo_gexf_spells_are_iso_dates(tmp_path):
    svo = tmp_path / "svo.csv"
    svo.write_text(
        "Subject (S),Verb (V),Object (O),Sentence ID\nhe,see,dog,1\nshe,feed,dog,2\nhe,walk,dog,3\n", encoding="utf-8"
    )
    io_libraries = MagicMock()
    io_libraries.external_software_install.return_value = ("/Applications/Gephi.app", None, False)
    stubs = {"IO_libraries_util": io_libraries, "IO_user_interface_util": MagicMock(), **_lxml_or_stand_in()}
    with patch.dict(sys.modules, stubs):
        sys.modules.pop("Gephi_util", None)
        import Gephi_util

        path = Gephi_util.create_gexf(
            MagicMock(), "svo", str(tmp_path), str(svo), "Subject (S)", "Verb (V)", "Object (O)", "Sentence ID"
        )
        sys.modules.pop("Gephi_util", None)
    text = open(os.path.join(str(tmp_path), "svo.gexf"), encoding="utf-8").read() if not path else open(path).read()
    dates = re.findall(r'(?:start|end)="([^"]+)"', text)
    assert dates, "no spells written"
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) for d in dates), dates
