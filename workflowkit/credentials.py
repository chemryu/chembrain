"""Credentials stay outside Box and prompts; Windows storage uses user-bound DPAPI."""
import base64
import ctypes
import json
import os
from pathlib import Path

ENV_NAMES = {'openai_key':'CHEMBRAIN_WORKFLOW_OPENAI_KEY', 'anthropic_key':'CHEMBRAIN_WORKFLOW_ANTHROPIC_KEY', 'github_token':'CHEMBRAIN_WORKFLOW_GITHUB_TOKEN'}


def credentials_path():
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local/share')) / 'ChembrainWorkflow' / 'credentials.dpapi'


def _crypt(data: bytes, decrypt=False) -> bytes:
    if os.name != 'nt':
        raise RuntimeError('Encrypted credential storage requires Windows; use environment bindings for development.')
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]

    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    output = Blob()
    function = ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(output)):
        raise RuntimeError('Windows could not protect/unprotect credentials for this user.')
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        ctypes.windll.kernel32.LocalFree(output.data)


def save(values):
    if set(values) != set(ENV_NAMES) or not all(isinstance(v,str) and v.strip() for v in values.values()):
        raise ValueError('All three credentials must be nonempty.')
    path = credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64encode(_crypt(json.dumps(values).encode('utf-8'))))


def load():
    result = {}
    path = credentials_path()
    if path.exists():
        result.update(json.loads(_crypt(base64.b64decode(path.read_bytes()), decrypt=True)))
    for name, variable in ENV_NAMES.items():
        if os.environ.get(variable):
            result[name] = os.environ[variable]
    missing = [name for name in ENV_NAMES if not result.get(name)]
    if missing:
        raise RuntimeError('Credential setup is incomplete: ' + ', '.join(missing) + '. Run Configure; never paste keys into Box or wiki.')
    return result
