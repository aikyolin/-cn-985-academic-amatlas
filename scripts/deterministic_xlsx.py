"""Write reproducible XLSX archives without changing worksheet content.

Workbook timestamps describe the export format, not a source retrieval date.
Source dates remain in worksheet cells. ZIP member order and metadata are fixed
so identical inputs produce identical bytes on repeat builds in one toolchain.
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
import os
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from openpyxl.writer.excel import ExcelWriter


FIXED_DATETIME = datetime(2000, 1, 1)
FIXED_ZIP_DATETIME = (2000, 1, 1, 0, 0, 0)


def save_deterministic_xlsx(workbook, filename):
    """Save a workbook atomically with fixed core dates and canonical ZIP data."""
    workbook.properties.created = FIXED_DATETIME
    workbook.properties.modified = FIXED_DATETIME
    workbook.properties.lastPrinted = None
    workbook.properties.creator = 'Academic Atlas'
    workbook.properties.lastModifiedBy = 'Academic Atlas'
    workbook.properties.revision = '1'
    source = BytesIO()
    # Workbook.save() replaces modified with the wall clock. ExcelWriter writes
    # the same workbook parts while preserving the explicit core properties.
    with ZipFile(source, 'w', ZIP_DEFLATED, allowZip64=True) as archive:
        ExcelWriter(workbook, archive).save()
    source.seek(0)
    target = Path(filename)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, suffix='.xlsx.tmp', delete=False) as file:
            temporary = Path(file.name)
        with ZipFile(source) as original, ZipFile(temporary, 'w', ZIP_DEFLATED, compresslevel=9, allowZip64=True) as canonical:
            for name in sorted(original.namelist()):
                entry = ZipInfo(name, FIXED_ZIP_DATETIME)
                entry.compress_type = ZIP_DEFLATED
                entry.create_system = 0
                entry.external_attr = 0o600 << 16
                canonical.writestr(entry, original.read(name), compress_type=ZIP_DEFLATED, compresslevel=9)
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
