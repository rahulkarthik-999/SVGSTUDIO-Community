"""
UploadService — handles file extraction and decoding from
multipart uploads and raw JSON payloads.
"""
from __future__ import annotations

from typing import Dict, Any, List
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..utils import get_logger, validate_svg_content, validate_filename

logger = get_logger(__name__)


class UploadService:
    """
    Converts incoming request data into validated SVG strings.
    """

    @staticmethod
    def from_file(file: FileStorage) -> Dict[str, Any]:
        """
        Extract and validate an SVG from a werkzeug FileStorage object.

        Returns:
            {"ok": True, "content": str, "filename": str}
            {"ok": False, "error": str}
        """
        filename = file.filename or ""

        err = validate_filename(filename)
        if err:
            return {"ok": False, "error": err}

        try:
            content = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return {"ok": False, "error": "File is not valid UTF-8 text."}

        err = validate_svg_content(content)
        if err:
            return {"ok": False, "error": err}

        logger.info("Accepted upload: %s (%d bytes)", filename, len(content))
        return {"ok": True, "content": content, "filename": secure_filename(filename)}

    @staticmethod
    def from_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate SVG from a parsed JSON dict.

        Returns:
            {"ok": True, "content": str}
            {"ok": False, "error": str}
        """
        content = (data.get("svg") or "").strip()
        err = validate_svg_content(content)
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "content": content}

    @staticmethod
    def from_files(files: List[FileStorage]) -> List[Dict[str, Any]]:
        """Validate and normalize a list of uploaded files."""
        results = []
        for file in files:
            if file is None:
                continue
            filename = file.filename or ''
            file_result = {
                'ok': False,
                'filename': filename,
                'content': None,
                'error': None,
            }

            err = validate_filename(filename)
            if err:
                file_result['error'] = err
                results.append(file_result)
                continue

            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                file_result['error'] = 'File is not valid UTF-8 text.'
                results.append(file_result)
                continue

            err = validate_svg_content(content)
            if err:
                file_result['error'] = err
                results.append(file_result)
                continue

            file_result.update({
                'ok': True,
                'content': content,
                'filename': secure_filename(filename),
            })
            results.append(file_result)

        return results

    @staticmethod
    def from_json_batch(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize a batch JSON payload."""
        items = data.get('files')
        if not isinstance(items, list):
            return {
                'ok': False,
                'error': "Request JSON must include a list of files under 'files'.",
            }

        results = []
        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                return {
                    'ok': False,
                    'error': 'Each batch item must be an object with svg content and optional filename.',
                }

            filename = item.get('filename') or f'file-{index}.svg'
            content = (item.get('svg') or '').strip()
            file_result = {
                'ok': False,
                'filename': filename,
                'content': None,
                'error': None,
            }

            if not filename:
                file_result['error'] = 'Filename is required for each batch item.'
                results.append(file_result)
                continue

            err = validate_filename(filename)
            if err:
                file_result['error'] = err
                results.append(file_result)
                continue

            err = validate_svg_content(content)
            if err:
                file_result['error'] = err
                results.append(file_result)
                continue

            file_result.update({
                'ok': True,
                'content': content,
                'filename': secure_filename(filename),
            })
            results.append(file_result)

        return {
            'ok': True,
            'files': results,
        }
