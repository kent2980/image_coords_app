# Image Coordinates App セキュリティガイド

## 目次

1. [概要](#概要)
2. [セキュリティ原則](#セキュリティ原則)
3. [認証とアクセス制御](#認証とアクセス制御)
4. [データ保護](#データ保護)
5. [ネットワークセキュリティ](#ネットワークセキュリティ)
6. [アプリケーションセキュリティ](#アプリケーションセキュリティ)
7. [監査とログ](#監査とログ)
8. [インシデント対応](#インシデント対応)
9. [セキュリティ設定](#セキュリティ設定)

## 概要

このドキュメントでは、Image Coordinates Appのセキュリティ要件と実装方針を説明します。製造業での座標データという機密性の高い情報を扱うため、適切なセキュリティ対策が必要です。

### セキュリティ要件

- **機密性**: 座標データと製品情報の保護
- **完全性**: データの改ざん防止
- **可用性**: 業務継続性の確保
- **追跡可能性**: 操作履歴の記録
- **アクセス制御**: 権限に基づく機能制限

## セキュリティ原則

### 1. 多層防御

```
┌─────────────────────────────────────┐
│           物理セキュリティ            │
├─────────────────────────────────────┤
│         ネットワークセキュリティ       │
├─────────────────────────────────────┤
│          OSセキュリティ              │
├─────────────────────────────────────┤
│       アプリケーションセキュリティ     │
├─────────────────────────────────────┤
│           データセキュリティ          │
└─────────────────────────────────────┘
```

### 2. 最小権限の原則

- ユーザーには必要最小限の権限のみ付与
- 機能別の権限分離
- 定期的な権限レビュー

### 3. データ分類

| 分類 | 内容 | 保護レベル |
|------|------|-----------|
| **極秘** | 座標データ、設計情報 | 最高 |
| **機密** | ロット情報、作業者情報 | 高 |
| **内部** | システム設定、ログ | 中 |
| **公開** | ヘルプ、マニュアル | 低 |

## 認証とアクセス制御

### ユーザー認証システム

#### 1. 認証方式の実装

```python
# src/security/auth.py
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

class AuthenticationManager:
    """認証管理システム"""
    
    def __init__(self):
        self.users_file = Path('security/users.json')
        self.sessions_file = Path('security/sessions.json')
        self.failed_attempts = {}
        self.lockout_duration = 300  # 5分
        self.max_failed_attempts = 3
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple[str, str]:
        """パスワードをハッシュ化"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # PBKDF2を使用した安全なハッシュ化
        import hashlib
        hashed = hashlib.pbkdf2_hmac('sha256', 
                                   password.encode('utf-8'), 
                                   salt, 
                                   100000)  # 100,000回反復
        
        return hashed.hex(), salt.hex()
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """パスワードを検証"""
        try:
            expected_hash, _ = self.hash_password(password, bytes.fromhex(salt))
            return secrets.compare_digest(expected_hash, hashed)
        except Exception:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """ユーザー認証"""
        
        # アカウントロックアウトチェック
        if self.is_account_locked(username):
            return None
        
        users = self.load_users()
        user_data = users.get(username)
        
        if not user_data:
            self.record_failed_attempt(username)
            return None
        
        # パスワード検証
        if self.verify_password(password, user_data['password_hash'], user_data['salt']):
            self.clear_failed_attempts(username)
            session_token = self.create_session(username)
            
            return {
                'username': username,
                'role': user_data['role'],
                'permissions': user_data['permissions'],
                'session_token': session_token
            }
        else:
            self.record_failed_attempt(username)
            return None
    
    def is_account_locked(self, username: str) -> bool:
        """アカウントロックアウト状態をチェック"""
        if username not in self.failed_attempts:
            return False
        
        attempts_data = self.failed_attempts[username]
        if attempts_data['count'] >= self.max_failed_attempts:
            locked_until = attempts_data['locked_until']
            if datetime.now() < locked_until:
                return True
            else:
                # ロックアウト期間終了
                self.clear_failed_attempts(username)
        
        return False
    
    def record_failed_attempt(self, username: str):
        """ログイン失敗を記録"""
        now = datetime.now()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {'count': 0, 'locked_until': None}
        
        self.failed_attempts[username]['count'] += 1
        
        if self.failed_attempts[username]['count'] >= self.max_failed_attempts:
            self.failed_attempts[username]['locked_until'] = now + timedelta(seconds=self.lockout_duration)
    
    def create_session(self, username: str) -> str:
        """セッショントークンを作成"""
        session_token = secrets.token_urlsafe(32)
        session_data = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat()
        }
        
        sessions = self.load_sessions()
        sessions[session_token] = session_data
        self.save_sessions(sessions)
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """セッションを検証"""
        sessions = self.load_sessions()
        session_data = sessions.get(session_token)
        
        if not session_data:
            return None
        
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        if datetime.now() > expires_at:
            # セッション期限切れ
            del sessions[session_token]
            self.save_sessions(sessions)
            return None
        
        return session_data['username']
```

#### 2. 権限管理システム

```python
# src/security/permissions.py
from enum import Enum
from typing import Set, Dict, Any
import json

class Permission(Enum):
    """権限定義"""
    VIEW_COORDINATES = "view_coordinates"
    EDIT_COORDINATES = "edit_coordinates"
    DELETE_COORDINATES = "delete_coordinates"
    MANAGE_BOARDS = "manage_boards"
    VIEW_REPORTS = "view_reports"
    ADMIN_SETTINGS = "admin_settings"
    USER_MANAGEMENT = "user_management"
    EXPORT_DATA = "export_data"

class Role(Enum):
    """ロール定義"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"

class PermissionManager:
    """権限管理システム"""
    
    def __init__(self):
        self.role_permissions = {
            Role.VIEWER: {
                Permission.VIEW_COORDINATES,
                Permission.VIEW_REPORTS
            },
            Role.OPERATOR: {
                Permission.VIEW_COORDINATES,
                Permission.EDIT_COORDINATES,
                Permission.VIEW_REPORTS
            },
            Role.SUPERVISOR: {
                Permission.VIEW_COORDINATES,
                Permission.EDIT_COORDINATES,
                Permission.DELETE_COORDINATES,
                Permission.MANAGE_BOARDS,
                Permission.VIEW_REPORTS,
                Permission.EXPORT_DATA
            },
            Role.ADMIN: set(Permission)  # 全権限
        }
    
    def has_permission(self, user_role: str, permission: Permission) -> bool:
        """ユーザーが指定の権限を持っているかチェック"""
        try:
            role = Role(user_role)
            return permission in self.role_permissions[role]
        except (ValueError, KeyError):
            return False
    
    def get_user_permissions(self, user_role: str) -> Set[Permission]:
        """ユーザーの権限一覧を取得"""
        try:
            role = Role(user_role)
            return self.role_permissions[role]
        except (ValueError, KeyError):
            return set()

def require_permission(permission: Permission):
    """権限チェックデコレータ"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'current_user') and self.current_user:
                perm_manager = PermissionManager()
                if perm_manager.has_permission(self.current_user['role'], permission):
                    return func(self, *args, **kwargs)
                else:
                    raise PermissionError(f"権限が不足しています: {permission.value}")
            else:
                raise PermissionError("認証が必要です")
        return wrapper
    return decorator
```

### セキュアなログイン画面

```python
# src/views/dialogs/login_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.security.auth import AuthenticationManager
from src.security.permissions import PermissionManager

class LoginDialog:
    """セキュアなログインダイアログ"""
    
    def __init__(self, parent):
        self.parent = parent
        self.auth_manager = AuthenticationManager()
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """ダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ログイン - Image Coordinates App")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # モーダルダイアログ
        
        # センタリング
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
        
        # Enterキーでログイン
        self.dialog.bind('<Return>', lambda e: self.login())
        
        # Escapeキーでキャンセル
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # ユーザー名フィールドにフォーカス
        self.username_entry.focus()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="認証が必要です", 
                               font=("", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # ユーザー名
        ttk.Label(main_frame, text="ユーザー名:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(pady=(5, 15), fill=tk.X)
        
        # パスワード
        ttk.Label(main_frame, text="パスワード:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.pack(pady=(5, 20), fill=tk.X)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="キャンセル", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="ログイン", 
                  command=self.login).pack(side=tk.RIGHT)
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
    
    def login(self):
        """ログイン処理"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="ユーザー名とパスワードを入力してください")
            return
        
        # 認証試行
        user_data = self.auth_manager.authenticate_user(username, password)
        
        if user_data:
            self.result = user_data
            self.dialog.destroy()
        else:
            self.status_label.config(text="認証に失敗しました")
            self.password_entry.delete(0, tk.END)
            
            # アカウントロックアウト警告
            if self.auth_manager.is_account_locked(username):
                messagebox.showwarning("アカウントロック", 
                                     "アカウントが一時的にロックされています。\n"
                                     "しばらく待ってから再度お試しください。")
    
    def cancel(self):
        """キャンセル処理"""
        self.dialog.destroy()
    
    def show(self):
        """ダイアログを表示"""
        self.dialog.wait_window()
        return self.result
```

## データ保護

### データ暗号化

#### 1. ファイル暗号化

```python
# src/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
from pathlib import Path

class DataEncryption:
    """データ暗号化管理"""
    
    def __init__(self, password: str = None):
        self.key = self._derive_key(password) if password else self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """パスワードから暗号化キーを導出"""
        password_bytes = password.encode('utf-8')
        salt = b'image_coords_app_salt_2025'  # 本番では動的に生成
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def _load_or_generate_key(self) -> bytes:
        """キーファイルを読み込みまたは生成"""
        key_file = Path('security/encryption.key')
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # 新しいキーを生成
            key = Fernet.generate_key()
            key_file.parent.mkdir(exist_ok=True)
            
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # キーファイルの権限を制限
            os.chmod(key_file, 0o600)
            
            return key
    
    def encrypt_file(self, file_path: Path, output_path: Path = None):
        """ファイルを暗号化"""
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.enc')
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: Path, output_path: Path = None):
        """ファイルを復号化"""
        if output_path is None:
            output_path = encrypted_file_path.with_suffix('')
        
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
        except Exception as e:
            raise ValueError(f"復号化に失敗しました: {e}")
    
    def encrypt_json_data(self, data: dict) -> str:
        """JSON データを暗号化"""
        json_str = json.dumps(data, ensure_ascii=False)
        encrypted_data = self.cipher.encrypt(json_str.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('ascii')
    
    def decrypt_json_data(self, encrypted_str: str) -> dict:
        """暗号化されたJSON データを復号化"""
        try:
            encrypted_data = base64.b64decode(encrypted_str.encode('ascii'))
            decrypted_data = self.cipher.decrypt(encrypted_data)
            json_str = decrypted_data.decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"JSON復号化に失敗しました: {e}")
```

#### 2. データベース暗号化

```python
# src/security/secure_storage.py
import sqlite3
import json
from pathlib import Path
from src.security.encryption import DataEncryption

class SecureDataStorage:
    """セキュアデータストレージ"""
    
    def __init__(self, db_path: Path, encryption_password: str = None):
        self.db_path = db_path
        self.encryption = DataEncryption(encryption_password)
        self.init_database()
    
    def init_database(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 暗号化されたデータテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encrypted_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_type TEXT NOT NULL,
                    data_key TEXT NOT NULL,
                    encrypted_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(data_type, data_key)
                )
            ''')
            
            # 監査ログテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def store_encrypted_data(self, data_type: str, data_key: str, data: dict):
        """暗号化してデータを保存"""
        encrypted_content = self.encryption.encrypt_json_data(data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO encrypted_data 
                (data_type, data_key, encrypted_content, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (data_type, data_key, encrypted_content))
            conn.commit()
    
    def retrieve_encrypted_data(self, data_type: str, data_key: str) -> dict:
        """暗号化されたデータを復号化して取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT encrypted_content FROM encrypted_data 
                WHERE data_type = ? AND data_key = ?
            ''', (data_type, data_key))
            
            result = cursor.fetchone()
            if result:
                return self.encryption.decrypt_json_data(result[0])
            else:
                raise KeyError(f"データが見つかりません: {data_type}/{data_key}")
    
    def log_audit_event(self, user_id: str, action: str, resource_type: str, 
                       resource_id: str = None, details: str = None, 
                       ip_address: str = None):
        """監査イベントをログ"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log 
                (user_id, action, resource_type, resource_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, action, resource_type, resource_id, details, ip_address))
            conn.commit()
```

### バックアップとリカバリ

#### セキュアバックアップシステム

```python
# src/security/backup.py
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from src.security.encryption import DataEncryption

class SecureBackupManager:
    """セキュアバックアップ管理"""
    
    def __init__(self, backup_dir: Path, encryption_password: str):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)
        self.encryption = DataEncryption(encryption_password)
    
    def create_backup(self, source_dirs: list, backup_name: str = None) -> Path:
        """暗号化バックアップを作成"""
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
        
        # 一時的なZIPファイルを作成
        temp_zip = self.backup_dir / f"{backup_name}_temp.zip"
        
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_dir in source_dirs:
                source_path = Path(source_dir)
                if source_path.exists():
                    if source_path.is_file():
                        zipf.write(source_path, source_path.name)
                    else:
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                relative_path = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, relative_path)
        
        # ZIPファイルを暗号化
        encrypted_backup = self.backup_dir / f"{backup_name}.bak"
        self.encryption.encrypt_file(temp_zip, encrypted_backup)
        
        # 一時ファイルを削除
        temp_zip.unlink()
        
        # チェックサムを作成
        self._create_checksum(encrypted_backup)
        
        return encrypted_backup
    
    def restore_backup(self, backup_file: Path, restore_dir: Path):
        """バックアップを復元"""
        # チェックサム検証
        if not self._verify_checksum(backup_file):
            raise ValueError("バックアップファイルが破損しています")
        
        # 一時的な復号化
        temp_zip = backup_file.with_suffix('.zip')
        self.encryption.decrypt_file(backup_file, temp_zip)
        
        try:
            # ZIPファイルを展開
            with zipfile.ZipFile(temp_zip, 'r') as zipf:
                zipf.extractall(restore_dir)
        finally:
            # 一時ファイルを削除
            if temp_zip.exists():
                temp_zip.unlink()
    
    def _create_checksum(self, file_path: Path):
        """ファイルのチェックサムを作成"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        checksum_file = file_path.with_suffix('.sha256')
        with open(checksum_file, 'w') as f:
            f.write(f"{hash_sha256.hexdigest()}  {file_path.name}\n")
    
    def _verify_checksum(self, file_path: Path) -> bool:
        """チェックサムを検証"""
        checksum_file = file_path.with_suffix('.sha256')
        
        if not checksum_file.exists():
            return False
        
        # 現在のチェックサムを計算
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        current_checksum = hash_sha256.hexdigest()
        
        # 保存されたチェックサムと比較
        with open(checksum_file, 'r') as f:
            stored_checksum = f.read().split()[0]
        
        return current_checksum == stored_checksum
```

## ネットワークセキュリティ

### セキュアファイル転送

```python
# src/security/network.py
import ssl
import ftplib
import paramiko
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

class SecureFileTransfer:
    """セキュアファイル転送"""
    
    def __init__(self, server: str, username: str, password: str, 
                 port: int = 22, protocol: str = 'sftp'):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.protocol = protocol.lower()
    
    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """ファイルをセキュアにアップロード"""
        try:
            if self.protocol == 'sftp':
                return self._sftp_upload(local_path, remote_path)
            elif self.protocol == 'ftps':
                return self._ftps_upload(local_path, remote_path)
            else:
                raise ValueError(f"サポートされていないプロトコル: {self.protocol}")
        except Exception as e:
            print(f"アップロードエラー: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """ファイルをセキュアにダウンロード"""
        try:
            if self.protocol == 'sftp':
                return self._sftp_download(remote_path, local_path)
            elif self.protocol == 'ftps':
                return self._ftps_download(remote_path, local_path)
            else:
                raise ValueError(f"サポートされていないプロトコル: {self.protocol}")
        except Exception as e:
            print(f"ダウンロードエラー: {e}")
            return False
    
    def _sftp_upload(self, local_path: Path, remote_path: str) -> bool:
        """SFTP でアップロード"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(self.server, port=self.port, 
                       username=self.username, password=self.password)
            
            sftp = ssh.open_sftp()
            sftp.put(str(local_path), remote_path)
            sftp.close()
            
            return True
        finally:
            ssh.close()
    
    def _sftp_download(self, remote_path: str, local_path: Path) -> bool:
        """SFTP でダウンロード"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(self.server, port=self.port, 
                       username=self.username, password=self.password)
            
            sftp = ssh.open_sftp()
            sftp.get(remote_path, str(local_path))
            sftp.close()
            
            return True
        finally:
            ssh.close()
    
    def _ftps_upload(self, local_path: Path, remote_path: str) -> bool:
        """FTPS でアップロード"""
        # TLS コンテキストの作成
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with ftplib.FTP_TLS(context=context) as ftps:
            ftps.connect(self.server, self.port)
            ftps.login(self.username, self.password)
            ftps.prot_p()  # データ接続を保護
            
            with open(local_path, 'rb') as f:
                ftps.storbinary(f'STOR {remote_path}', f)
            
            return True
    
    def _ftps_download(self, remote_path: str, local_path: Path) -> bool:
        """FTPS でダウンロード"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with ftplib.FTP_TLS(context=context) as ftps:
            ftps.connect(self.server, self.port)
            ftps.login(self.username, self.password)
            ftps.prot_p()
            
            with open(local_path, 'wb') as f:
                ftps.retrbinary(f'RETR {remote_path}', f.write)
            
            return True
```

### ネットワーク監視

```python
# src/security/network_monitor.py
import socket
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

class NetworkMonitor:
    """ネットワーク監視システム"""
    
    def __init__(self):
        self.connection_log = []
        self.suspicious_activities = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """監視を開始"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.monitoring:
            try:
                self._check_network_connections()
                self._detect_suspicious_activities()
                time.sleep(60)  # 1分間隔
            except Exception as e:
                print(f"監視エラー: {e}")
                time.sleep(10)
    
    def _check_network_connections(self):
        """ネットワーク接続をチェック"""
        try:
            import psutil
            
            connections = psutil.net_connections()
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    connection_info = {
                        'timestamp': datetime.now().isoformat(),
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "Unknown",
                        'pid': conn.pid,
                        'status': conn.status
                    }
                    
                    self.connection_log.append(connection_info)
                    
                    # ログサイズ制限
                    if len(self.connection_log) > 1000:
                        self.connection_log = self.connection_log[-500:]
                        
        except Exception as e:
            print(f"接続チェックエラー: {e}")
    
    def _detect_suspicious_activities(self):
        """suspicious activityの検出"""
        recent_connections = [
            conn for conn in self.connection_log 
            if (datetime.now() - datetime.fromisoformat(conn['timestamp'])).seconds < 300
        ]
        
        # 短時間での大量接続を検出
        if len(recent_connections) > 50:
            self.suspicious_activities.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'high_connection_rate',
                'details': f"5分間で{len(recent_connections)}の接続を検出",
                'severity': 'medium'
            })
    
    def get_security_report(self) -> Dict[str, Any]:
        """セキュリティレポートを生成"""
        return {
            'monitoring_status': self.monitoring,
            'total_connections': len(self.connection_log),
            'recent_connections': len([
                conn for conn in self.connection_log 
                if (datetime.now() - datetime.fromisoformat(conn['timestamp'])).seconds < 3600
            ]),
            'suspicious_activities': len(self.suspicious_activities),
            'last_check': datetime.now().isoformat()
        }
```

## 監査とログ

### 包括的監査システム

```python
# src/security/audit.py
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from enum import Enum

class AuditEventType(Enum):
    """監査イベントタイプ"""
    LOGIN = "login"
    LOGOUT = "logout"
    FILE_ACCESS = "file_access"
    DATA_MODIFICATION = "data_modification"
    SETTINGS_CHANGE = "settings_change"
    EXPORT = "export"
    IMPORT = "import"
    ERROR = "error"
    SECURITY_VIOLATION = "security_violation"

class AuditLogger:
    """監査ログシステム"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.current_session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """セッションIDを生成"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def log_event(self, event_type: AuditEventType, user_id: str, 
                 details: Dict[str, Any], severity: str = "info"):
        """監査イベントをログ"""
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.current_session_id,
            'event_type': event_type.value,
            'user_id': user_id,
            'severity': severity,
            'details': details,
            'checksum': None
        }
        
        # チェックサムを計算
        event_str = json.dumps(event, sort_keys=True, ensure_ascii=False)
        event['checksum'] = hashlib.sha256(event_str.encode()).hexdigest()[:16]
        
        # ログファイルに保存
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(event, f, ensure_ascii=False)
            f.write('\n')
    
    def log_login(self, user_id: str, ip_address: str = None, success: bool = True):
        """ログインイベントをログ"""
        details = {
            'ip_address': ip_address,
            'success': success,
            'user_agent': 'ImageCoordsApp/1.0'
        }
        
        severity = "info" if success else "warning"
        self.log_event(AuditEventType.LOGIN, user_id, details, severity)
    
    def log_file_access(self, user_id: str, file_path: str, action: str):
        """ファイルアクセスをログ"""
        details = {
            'file_path': file_path,
            'action': action,  # read, write, delete
            'file_size': None
        }
        
        try:
            file_obj = Path(file_path)
            if file_obj.exists():
                details['file_size'] = file_obj.stat().st_size
        except Exception:
            pass
        
        self.log_event(AuditEventType.FILE_ACCESS, user_id, details)
    
    def log_data_modification(self, user_id: str, data_type: str, 
                            record_id: str, changes: Dict[str, Any]):
        """データ変更をログ"""
        details = {
            'data_type': data_type,
            'record_id': record_id,
            'changes': changes,
            'change_count': len(changes)
        }
        
        self.log_event(AuditEventType.DATA_MODIFICATION, user_id, details)
    
    def search_events(self, start_date: datetime = None, end_date: datetime = None, 
                     event_type: AuditEventType = None, user_id: str = None) -> List[Dict[str, Any]]:
        """監査イベントを検索"""
        events = []
        
        # ログファイルを日付順で処理
        log_files = sorted(self.log_dir.glob("audit_*.log"))
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event['timestamp'])
                        
                        # 日付フィルタ
                        if start_date and event_time < start_date:
                            continue
                        if end_date and event_time > end_date:
                            continue
                        
                        # イベントタイプフィルタ
                        if event_type and event['event_type'] != event_type.value:
                            continue
                        
                        # ユーザーフィルタ
                        if user_id and event['user_id'] != user_id:
                            continue
                        
                        events.append(event)
                        
                    except json.JSONDecodeError:
                        continue
        
        return events
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """監査レポートを生成"""
        events = self.search_events(start_date, end_date)
        
        # 統計情報を計算
        event_counts = {}
        user_activities = {}
        security_events = 0
        
        for event in events:
            # イベントタイプ別集計
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # ユーザー別集計
            user_id = event['user_id']
            if user_id not in user_activities:
                user_activities[user_id] = {
                    'total_events': 0,
                    'event_types': set()
                }
            
            user_activities[user_id]['total_events'] += 1
            user_activities[user_id]['event_types'].add(event_type)
            
            # セキュリティイベント集計
            if event['severity'] in ['warning', 'error', 'critical']:
                security_events += 1
        
        # セットをリストに変換（JSON化のため）
        for user_data in user_activities.values():
            user_data['event_types'] = list(user_data['event_types'])
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'event_counts': event_counts,
                'security_events': security_events,
                'unique_users': len(user_activities)
            },
            'user_activities': user_activities,
            'generated_at': datetime.now().isoformat()
        }
```

## セキュリティ設定

### セキュリティ設定ファイル

```ini
# security/security_config.ini
[Authentication]
password_min_length=8
password_require_uppercase=true
password_require_lowercase=true
password_require_numbers=true
password_require_symbols=true
password_history_count=5
account_lockout_attempts=3
account_lockout_duration=300
session_timeout=28800

[Encryption]
algorithm=AES-256
key_derivation=PBKDF2
iterations=100000
encrypt_data_files=true
encrypt_config_files=false

[Network]
allowed_protocols=https,sftp
max_concurrent_connections=10
connection_timeout=30
certificate_validation=true

[Audit]
log_level=INFO
log_all_file_access=true
log_data_changes=true
log_retention_days=365
log_encryption=true

[Security]
auto_lock_enabled=true
auto_lock_timeout=1800
screen_lock_on_idle=true
disable_screenshot=false
watermark_enabled=true
```

### セキュリティポリシー管理

```python
# src/security/policy.py
import configparser
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SecurityPolicy:
    """セキュリティポリシー設定"""
    
    # 認証設定
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    account_lockout_attempts: int = 3
    account_lockout_duration: int = 300
    session_timeout: int = 28800
    
    # 暗号化設定
    encrypt_data_files: bool = True
    encrypt_config_files: bool = False
    
    # ネットワーク設定
    allowed_protocols: List[str] = None
    max_concurrent_connections: int = 10
    connection_timeout: int = 30
    
    # 監査設定
    log_all_file_access: bool = True
    log_data_changes: bool = True
    log_retention_days: int = 365
    
    def __post_init__(self):
        if self.allowed_protocols is None:
            self.allowed_protocols = ['https', 'sftp']

class SecurityPolicyManager:
    """セキュリティポリシー管理"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.policy = self._load_policy()
    
    def _load_policy(self) -> SecurityPolicy:
        """ポリシー設定を読み込み"""
        if not self.config_file.exists():
            return SecurityPolicy()
        
        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')
        
        return SecurityPolicy(
            password_min_length=config.getint('Authentication', 'password_min_length', fallback=8),
            password_require_uppercase=config.getboolean('Authentication', 'password_require_uppercase', fallback=True),
            password_require_lowercase=config.getboolean('Authentication', 'password_require_lowercase', fallback=True),
            password_require_numbers=config.getboolean('Authentication', 'password_require_numbers', fallback=True),
            password_require_symbols=config.getboolean('Authentication', 'password_require_symbols', fallback=True),
            account_lockout_attempts=config.getint('Authentication', 'account_lockout_attempts', fallback=3),
            account_lockout_duration=config.getint('Authentication', 'account_lockout_duration', fallback=300),
            session_timeout=config.getint('Authentication', 'session_timeout', fallback=28800),
            encrypt_data_files=config.getboolean('Encryption', 'encrypt_data_files', fallback=True),
            encrypt_config_files=config.getboolean('Encryption', 'encrypt_config_files', fallback=False),
            allowed_protocols=config.get('Network', 'allowed_protocols', fallback='https,sftp').split(','),
            max_concurrent_connections=config.getint('Network', 'max_concurrent_connections', fallback=10),
            connection_timeout=config.getint('Network', 'connection_timeout', fallback=30),
            log_all_file_access=config.getboolean('Audit', 'log_all_file_access', fallback=True),
            log_data_changes=config.getboolean('Audit', 'log_data_changes', fallback=True),
            log_retention_days=config.getint('Audit', 'log_retention_days', fallback=365)
        )
    
    def validate_password(self, password: str) -> List[str]:
        """パスワードポリシーを検証"""
        errors = []
        
        if len(password) < self.policy.password_min_length:
            errors.append(f"パスワードは{self.policy.password_min_length}文字以上である必要があります")
        
        if self.policy.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("パスワードには大文字を含める必要があります")
        
        if self.policy.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("パスワードには小文字を含める必要があります")
        
        if self.policy.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("パスワードには数字を含める必要があります")
        
        if self.policy.password_require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("パスワードには記号を含める必要があります")
        
        return errors
    
    def is_protocol_allowed(self, protocol: str) -> bool:
        """プロトコルが許可されているかチェック"""
        return protocol.lower() in [p.strip().lower() for p in self.policy.allowed_protocols]
```

---

## インシデント対応

### セキュリティインシデント検出

```python
# src/security/incident_detection.py
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from enum import Enum
from src.security.audit import AuditLogger, AuditEventType

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityIncident:
    """セキュリティインシデント"""
    
    def __init__(self, incident_type: str, severity: IncidentSeverity, 
                 description: str, details: Dict[str, Any]):
        self.id = self._generate_id()
        self.incident_type = incident_type
        self.severity = severity
        self.description = description
        self.details = details
        self.timestamp = datetime.now()
        self.resolved = False
        self.resolution_notes = None
    
    def _generate_id(self) -> str:
        """インシデントIDを生成"""
        import hashlib
        timestamp = datetime.now().isoformat()
        return f"INC-{hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()}"

class IncidentDetector:
    """セキュリティインシデント検出システム"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.incidents = []
        self.detection_rules = self._init_detection_rules()
        self.monitoring = False
        self.monitor_thread = None
    
    def _init_detection_rules(self) -> Dict[str, Any]:
        """検出ルールを初期化"""
        return {
            'failed_login_threshold': 5,
            'failed_login_window': 300,  # 5分
            'mass_file_access_threshold': 50,
            'mass_file_access_window': 600,  # 10分
            'unusual_activity_threshold': 100,
            'data_export_size_threshold': 100 * 1024 * 1024,  # 100MB
        }
    
    def start_detection(self):
        """検出を開始"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._detection_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_detection(self):
        """検出を停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _detection_loop(self):
        """検出ループ"""
        while self.monitoring:
            try:
                self._check_failed_logins()
                self._check_mass_file_access()
                self._check_unusual_activity()
                self._check_large_exports()
                
                time.sleep(60)  # 1分間隔
            except Exception as e:
                print(f"検出エラー: {e}")
                time.sleep(30)
    
    def _check_failed_logins(self):
        """ログイン失敗の検出"""
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=self.detection_rules['failed_login_window'])
        
        # 最近のログインイベントを取得
        events = self.audit_logger.search_events(
            start_date=start_time,
            end_date=end_time,
            event_type=AuditEventType.LOGIN
        )
        
        # ユーザー別失敗回数を集計
        failed_attempts = {}
        for event in events:
            if not event['details'].get('success', True):
                user_id = event['user_id']
                failed_attempts[user_id] = failed_attempts.get(user_id, 0) + 1
        
        # 閾値を超えたユーザーを検出
        for user_id, count in failed_attempts.items():
            if count >= self.detection_rules['failed_login_threshold']:
                incident = SecurityIncident(
                    incident_type="brute_force_attack",
                    severity=IncidentSeverity.HIGH,
                    description=f"ユーザー {user_id} への総当たり攻撃の可能性",
                    details={
                        'user_id': user_id,
                        'failed_attempts': count,
                        'time_window': self.detection_rules['failed_login_window']
                    }
                )
                self._report_incident(incident)
    
    def _check_mass_file_access(self):
        """大量ファイルアクセスの検出"""
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=self.detection_rules['mass_file_access_window'])
        
        events = self.audit_logger.search_events(
            start_date=start_time,
            end_date=end_time,
            event_type=AuditEventType.FILE_ACCESS
        )
        
        # ユーザー別アクセス回数を集計
        access_counts = {}
        for event in events:
            user_id = event['user_id']
            access_counts[user_id] = access_counts.get(user_id, 0) + 1
        
        # 閾値を超えたユーザーを検出
        for user_id, count in access_counts.items():
            if count >= self.detection_rules['mass_file_access_threshold']:
                incident = SecurityIncident(
                    incident_type="mass_file_access",
                    severity=IncidentSeverity.MEDIUM,
                    description=f"ユーザー {user_id} による大量ファイルアクセス",
                    details={
                        'user_id': user_id,
                        'access_count': count,
                        'time_window': self.detection_rules['mass_file_access_window']
                    }
                )
                self._report_incident(incident)
    
    def _report_incident(self, incident: SecurityIncident):
        """インシデントを報告"""
        self.incidents.append(incident)
        
        # 監査ログに記録
        self.audit_logger.log_event(
            AuditEventType.SECURITY_VIOLATION,
            "system",
            {
                'incident_id': incident.id,
                'incident_type': incident.incident_type,
                'severity': incident.severity.value,
                'description': incident.description,
                'details': incident.details
            },
            severity="warning" if incident.severity == IncidentSeverity.LOW else "error"
        )
        
        print(f"セキュリティインシデント検出: {incident.id} - {incident.description}")
    
    def get_incidents(self, severity: IncidentSeverity = None, 
                     resolved: bool = None) -> List[SecurityIncident]:
        """インシデント一覧を取得"""
        incidents = self.incidents
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        if resolved is not None:
            incidents = [i for i in incidents if i.resolved == resolved]
        
        return incidents
    
    def resolve_incident(self, incident_id: str, resolution_notes: str):
        """インシデントを解決"""
        for incident in self.incidents:
            if incident.id == incident_id:
                incident.resolved = True
                incident.resolution_notes = resolution_notes
                
                self.audit_logger.log_event(
                    AuditEventType.SECURITY_VIOLATION,
                    "system",
                    {
                        'incident_id': incident_id,
                        'action': 'resolved',
                        'resolution_notes': resolution_notes
                    }
                )
                break
```

---

**最終更新**: 2025年8月18日  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot
