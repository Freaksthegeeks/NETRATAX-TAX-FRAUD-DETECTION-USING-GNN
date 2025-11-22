import os
from pathlib import Path
from cryptography.fernet import Fernet


KEY_PATH = Path(__file__).parent.parent / "data" / "secure" / "key.key"


def ensure_key():
    """Ensure an encryption key exists; create one if missing."""
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not KEY_PATH.exists():
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        try:
            # Restrict permissions where possible
            os.chmod(KEY_PATH, 0o600)
        except Exception:
            # Windows may not support chmod the same way; ignore
            pass
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key


def load_key():
    if not KEY_PATH.exists():
        return ensure_key()
    with open(KEY_PATH, "rb") as f:
        return f.read()


def encrypt_file(in_path: Path, out_path: Path = None) -> Path:
    """Encrypt a file using Fernet symmetric encryption.

    Returns the path to the encrypted file.
    """
    key = load_key()
    fernet = Fernet(key)
    in_path = Path(in_path)
    if out_path is None:
        out_path = in_path.with_suffix(in_path.suffix + '.enc')
    with open(in_path, 'rb') as f:
        data = f.read()
    token = fernet.encrypt(data)
    with open(out_path, 'wb') as f:
        f.write(token)
    try:
        os.chmod(out_path, 0o600)
    except Exception:
        pass
    return out_path


def decrypt_file(enc_path: Path, out_path: Path = None) -> Path:
    key = load_key()
    fernet = Fernet(key)
    enc_path = Path(enc_path)
    if out_path is None:
        # remove .enc suffix
        if enc_path.suffix == '.enc':
            out_path = enc_path.with_suffix('')
        else:
            out_path = enc_path.with_suffix(enc_path.suffix + '.dec')
    with open(enc_path, 'rb') as f:
        token = f.read()
    data = fernet.decrypt(token)
    with open(out_path, 'wb') as f:
        f.write(data)
    return out_path
