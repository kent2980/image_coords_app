# Image Coordinates App API 仕様書

## 目次

1. [概要](#概要)
2. [認証システム](#認証システム)
3. [座標管理API](#座標管理api)
4. [基板管理API](#基板管理api)
5. [ファイル管理API](#ファイル管理api)
6. [設定管理API](#設定管理api)
7. [エラーハンドリング](#エラーハンドリング)
8. [データ形式](#データ形式)
9. [統合例](#統合例)

## 概要

Image Coordinates Appは内部APIを提供し、外部システムとの統合やカスタムスクリプトでの自動化を可能にします。

### API設計原則

- **RESTful**: 標準的なHTTPメソッドとステータスコードを使用
- **JSON**: データ交換にはJSON形式を使用
- **認証**: JWT（JSON Web Token）ベースの認証
- **バージョニング**: URLパスでAPIバージョンを管理
- **エラーハンドリング**: 一貫したエラーレスポンス形式

### APIエンドポイント構成

```
http://localhost:8080/api/v1/
├── auth/
│   ├── login
│   ├── logout
│   └── refresh
├── coordinates/
│   ├── list
│   ├── create
│   ├── update
│   └── delete
├── boards/
│   ├── list
│   ├── create
│   ├── update
│   └── delete
├── files/
│   ├── upload
│   ├── download
│   └── list
└── settings/
    ├── get
    └── update
```

## 認証システム

### ログイン

#### エンドポイント
```
POST /api/v1/auth/login
```

#### リクエスト
```json
{
    "username": "user001",
    "password": "password123"
}
```

#### レスポンス（成功）
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600,
        "user": {
            "id": "user001",
            "name": "田中太郎",
            "role": "operator",
            "permissions": [
                "view_coordinates",
                "edit_coordinates"
            ]
        }
    }
}
```

#### レスポンス（エラー）
```json
{
    "status": "error",
    "error": {
        "code": "INVALID_CREDENTIALS",
        "message": "ユーザー名またはパスワードが正しくありません",
        "details": {
            "failed_attempts": 2,
            "lockout_remaining": 298
        }
    }
}
```

### トークン更新

#### エンドポイント
```
POST /api/v1/auth/refresh
```

#### リクエスト
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600
    }
}
```

## 座標管理API

### 座標一覧取得

#### エンドポイント
```
GET /api/v1/coordinates/list
```

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| lot_number | string | No | ロット番号でフィルタ |
| board_index | integer | No | 基板番号でフィルタ |
| limit | integer | No | 取得件数制限（デフォルト: 100） |
| offset | integer | No | オフセット（デフォルト: 0） |

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "coordinates": [
            {
                "id": "coord_001",
                "lot_number": "LOT2025001",
                "board_index": 1,
                "x": 125.5,
                "y": 230.8,
                "defect_type": "ショート",
                "created_at": "2025-08-18T10:30:00Z",
                "updated_at": "2025-08-18T10:30:00Z",
                "created_by": "user001"
            }
        ],
        "total_count": 1,
        "limit": 100,
        "offset": 0
    }
}
```

### 座標作成

#### エンドポイント
```
POST /api/v1/coordinates/create
```

#### リクエスト
```json
{
    "lot_number": "LOT2025001",
    "board_index": 1,
    "x": 125.5,
    "y": 230.8,
    "defect_type": "ショート"
}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "id": "coord_002",
        "lot_number": "LOT2025001",
        "board_index": 1,
        "x": 125.5,
        "y": 230.8,
        "defect_type": "ショート",
        "created_at": "2025-08-18T11:00:00Z",
        "updated_at": "2025-08-18T11:00:00Z",
        "created_by": "user001"
    }
}
```

### 座標更新

#### エンドポイント
```
PUT /api/v1/coordinates/update/{coordinate_id}
```

#### リクエスト
```json
{
    "x": 130.0,
    "y": 235.0,
    "defect_type": "オープン"
}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "id": "coord_001",
        "lot_number": "LOT2025001",
        "board_index": 1,
        "x": 130.0,
        "y": 235.0,
        "defect_type": "オープン",
        "created_at": "2025-08-18T10:30:00Z",
        "updated_at": "2025-08-18T11:15:00Z",
        "created_by": "user001"
    }
}
```

### 座標削除

#### エンドポイント
```
DELETE /api/v1/coordinates/delete/{coordinate_id}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "message": "座標が正常に削除されました",
        "deleted_id": "coord_001"
    }
}
```

## 基板管理API

### 基板一覧取得

#### エンドポイント
```
GET /api/v1/boards/list
```

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| lot_number | string | No | ロット番号でフィルタ |
| status | string | No | ステータスでフィルタ（active, completed, archived） |

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "boards": [
            {
                "lot_number": "LOT2025001",
                "total_boards": 10,
                "completed_boards": 3,
                "status": "active",
                "created_at": "2025-08-18T09:00:00Z",
                "updated_at": "2025-08-18T11:00:00Z",
                "boards": [
                    {
                        "board_index": 1,
                        "coordinate_count": 5,
                        "status": "completed",
                        "last_updated": "2025-08-18T10:30:00Z"
                    }
                ]
            }
        ]
    }
}
```

### 基板作成

#### エンドポイント
```
POST /api/v1/boards/create
```

#### リクエスト
```json
{
    "lot_number": "LOT2025002",
    "total_boards": 15,
    "description": "新製品テストロット"
}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "lot_number": "LOT2025002",
        "total_boards": 15,
        "completed_boards": 0,
        "status": "active",
        "description": "新製品テストロット",
        "created_at": "2025-08-18T12:00:00Z",
        "updated_at": "2025-08-18T12:00:00Z"
    }
}
```

## ファイル管理API

### ファイルアップロード

#### エンドポイント
```
POST /api/v1/files/upload
```

#### リクエスト（multipart/form-data）
```
file: [バイナリファイル]
file_type: "image" | "config" | "data"
description: "ファイルの説明"
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "file_id": "file_001",
        "file_name": "board_image.jpg",
        "file_type": "image",
        "file_size": 1024000,
        "upload_date": "2025-08-18T12:30:00Z",
        "url": "/api/v1/files/download/file_001"
    }
}
```

### ファイルダウンロード

#### エンドポイント
```
GET /api/v1/files/download/{file_id}
```

#### レスポンス
```
バイナリファイルデータ

Headers:
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="board_image.jpg"
Content-Length: 1024000
```

### ファイル一覧取得

#### エンドポイント
```
GET /api/v1/files/list
```

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| file_type | string | No | ファイルタイプでフィルタ |
| limit | integer | No | 取得件数制限 |

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "files": [
            {
                "file_id": "file_001",
                "file_name": "board_image.jpg",
                "file_type": "image",
                "file_size": 1024000,
                "upload_date": "2025-08-18T12:30:00Z",
                "description": "基板画像ファイル"
            }
        ],
        "total_count": 1
    }
}
```

## 設定管理API

### 設定取得

#### エンドポイント
```
GET /api/v1/settings/get
```

#### クエリパラメータ
| パラメータ | 型 | 必須 | 説明 |
|-----------|----|----|------|
| category | string | No | 設定カテゴリ（app, ui, network） |

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "settings": {
            "app": {
                "default_mode": "編集",
                "auto_save": true,
                "max_undo_stack": 50
            },
            "ui": {
                "window_width": 1400,
                "window_height": 900,
                "canvas_width": 800,
                "canvas_height": 600
            },
            "network": {
                "timeout": 30,
                "retry_count": 3
            }
        }
    }
}
```

### 設定更新

#### エンドポイント
```
PUT /api/v1/settings/update
```

#### リクエスト
```json
{
    "settings": {
        "app": {
            "auto_save": false,
            "max_undo_stack": 100
        },
        "ui": {
            "window_width": 1600,
            "window_height": 1000
        }
    }
}
```

#### レスポンス
```json
{
    "status": "success",
    "data": {
        "message": "設定が正常に更新されました",
        "updated_settings": {
            "app.auto_save": false,
            "app.max_undo_stack": 100,
            "ui.window_width": 1600,
            "ui.window_height": 1000
        }
    }
}
```

## エラーハンドリング

### エラーレスポンス形式

```json
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "エラーメッセージ",
        "details": {
            "field": "エラーの詳細情報"
        },
        "timestamp": "2025-08-18T12:00:00Z",
        "request_id": "req_123456"
    }
}
```

### エラーコード一覧

| コード | HTTPステータス | 説明 |
|--------|---------------|------|
| INVALID_CREDENTIALS | 401 | 認証情報が無効 |
| INSUFFICIENT_PERMISSIONS | 403 | 権限不足 |
| RESOURCE_NOT_FOUND | 404 | リソースが見つからない |
| VALIDATION_ERROR | 400 | 入力値の検証エラー |
| DUPLICATE_RESOURCE | 409 | リソースの重複 |
| INTERNAL_SERVER_ERROR | 500 | サーバー内部エラー |
| SERVICE_UNAVAILABLE | 503 | サービス一時停止 |

### 検証エラーの詳細例

```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "入力値に問題があります",
        "details": {
            "x": "X座標は0以上である必要があります",
            "defect_type": "不良項目は必須です"
        }
    }
}
```

## データ形式

### 座標データ

```typescript
interface Coordinate {
    id: string;
    lot_number: string;
    board_index: number;
    x: number;
    y: number;
    defect_type: string;
    created_at: string; // ISO 8601
    updated_at: string; // ISO 8601
    created_by: string;
}
```

### 基板データ

```typescript
interface Board {
    lot_number: string;
    total_boards: number;
    completed_boards: number;
    status: "active" | "completed" | "archived";
    description?: string;
    created_at: string;
    updated_at: string;
    boards: BoardDetail[];
}

interface BoardDetail {
    board_index: number;
    coordinate_count: number;
    status: "pending" | "in_progress" | "completed";
    last_updated: string;
}
```

### ファイルデータ

```typescript
interface FileInfo {
    file_id: string;
    file_name: string;
    file_type: "image" | "config" | "data";
    file_size: number;
    upload_date: string;
    description?: string;
    url: string;
}
```

### 設定データ

```typescript
interface Settings {
    app: {
        default_mode: string;
        auto_save: boolean;
        max_undo_stack: number;
    };
    ui: {
        window_width: number;
        window_height: number;
        canvas_width: number;
        canvas_height: number;
    };
    network: {
        timeout: number;
        retry_count: number;
    };
}
```

## 統合例

### Python クライアント

```python
# api_client.py
import requests
import json
from typing import Dict, Any, Optional, List

class ImageCoordsAPIClient:
    """Image Coordinates App APIクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8080/api/v1"):
        self.base_url = base_url
        self.access_token = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> bool:
        """ログイン"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                self.access_token = data["data"]["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                return True
        
        return False
    
    def get_coordinates(self, lot_number: str = None, 
                       board_index: int = None) -> List[Dict[str, Any]]:
        """座標一覧を取得"""
        params = {}
        if lot_number:
            params["lot_number"] = lot_number
        if board_index is not None:
            params["board_index"] = board_index
        
        response = self.session.get(
            f"{self.base_url}/coordinates/list",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["data"]["coordinates"]
        
        return []
    
    def create_coordinate(self, lot_number: str, board_index: int,
                         x: float, y: float, defect_type: str) -> Optional[Dict[str, Any]]:
        """座標を作成"""
        response = self.session.post(
            f"{self.base_url}/coordinates/create",
            json={
                "lot_number": lot_number,
                "board_index": board_index,
                "x": x,
                "y": y,
                "defect_type": defect_type
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["data"]
        
        return None
    
    def update_coordinate(self, coordinate_id: str, 
                         updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """座標を更新"""
        response = self.session.put(
            f"{self.base_url}/coordinates/update/{coordinate_id}",
            json=updates
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["data"]
        
        return None
    
    def delete_coordinate(self, coordinate_id: str) -> bool:
        """座標を削除"""
        response = self.session.delete(
            f"{self.base_url}/coordinates/delete/{coordinate_id}"
        )
        
        return response.status_code == 200
    
    def upload_file(self, file_path: str, file_type: str, 
                   description: str = None) -> Optional[Dict[str, Any]]:
        """ファイルをアップロード"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'file_type': file_type,
                'description': description or ''
            }
            
            response = self.session.post(
                f"{self.base_url}/files/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["data"]
        
        return None

# 使用例
def main():
    client = ImageCoordsAPIClient()
    
    # ログイン
    if client.login("user001", "password123"):
        print("ログイン成功")
        
        # 座標一覧取得
        coordinates = client.get_coordinates(lot_number="LOT2025001")
        print(f"座標数: {len(coordinates)}")
        
        # 新しい座標を作成
        new_coord = client.create_coordinate(
            lot_number="LOT2025001",
            board_index=1,
            x=100.5,
            y=200.3,
            defect_type="ショート"
        )
        
        if new_coord:
            print(f"座標作成成功: {new_coord['id']}")
            
            # 座標を更新
            updated_coord = client.update_coordinate(
                new_coord['id'],
                {"defect_type": "オープン"}
            )
            
            if updated_coord:
                print("座標更新成功")
    else:
        print("ログイン失敗")

if __name__ == "__main__":
    main()
```

### JavaScript クライアント

```javascript
// api-client.js
class ImageCoordsAPIClient {
    constructor(baseUrl = 'http://localhost:8080/api/v1') {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }

    async login(username, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.accessToken = data.data.access_token;
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('ログインエラー:', error);
            return false;
        }
    }

    async getCoordinates(lotNumber = null, boardIndex = null) {
        const params = new URLSearchParams();
        if (lotNumber) params.append('lot_number', lotNumber);
        if (boardIndex !== null) params.append('board_index', boardIndex);

        try {
            const response = await fetch(
                `${this.baseUrl}/coordinates/list?${params}`,
                {
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.coordinates;
            }
            
            return [];
        } catch (error) {
            console.error('座標取得エラー:', error);
            return [];
        }
    }

    async createCoordinate(lotNumber, boardIndex, x, y, defectType) {
        try {
            const response = await fetch(`${this.baseUrl}/coordinates/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify({
                    lot_number: lotNumber,
                    board_index: boardIndex,
                    x: x,
                    y: y,
                    defect_type: defectType
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data;
            }
            
            return null;
        } catch (error) {
            console.error('座標作成エラー:', error);
            return null;
        }
    }
}

// 使用例
async function example() {
    const client = new ImageCoordsAPIClient();
    
    // ログイン
    const loginSuccess = await client.login('user001', 'password123');
    if (loginSuccess) {
        console.log('ログイン成功');
        
        // 座標一覧取得
        const coordinates = await client.getCoordinates('LOT2025001');
        console.log(`座標数: ${coordinates.length}`);
        
        // 新しい座標作成
        const newCoord = await client.createCoordinate(
            'LOT2025001', 1, 150.0, 250.0, 'ショート'
        );
        
        if (newCoord) {
            console.log(`座標作成成功: ${newCoord.id}`);
        }
    } else {
        console.log('ログイン失敗');
    }
}
```

### PowerShell スクリプト

```powershell
# ImageCoordsAPI.ps1
class ImageCoordsAPIClient {
    [string]$BaseUrl
    [string]$AccessToken
    
    ImageCoordsAPIClient([string]$baseUrl = "http://localhost:8080/api/v1") {
        $this.BaseUrl = $baseUrl
        $this.AccessToken = $null
    }
    
    [bool] Login([string]$username, [string]$password) {
        $body = @{
            username = $username
            password = $password
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/auth/login" -Method Post -Body $body -ContentType "application/json"
            
            if ($response.status -eq "success") {
                $this.AccessToken = $response.data.access_token
                return $true
            }
            
            return $false
        }
        catch {
            Write-Error "ログインエラー: $_"
            return $false
        }
    }
    
    [array] GetCoordinates([string]$lotNumber = $null, [int]$boardIndex = -1) {
        $uri = "$($this.BaseUrl)/coordinates/list"
        $params = @()
        
        if ($lotNumber) {
            $params += "lot_number=$lotNumber"
        }
        
        if ($boardIndex -ge 0) {
            $params += "board_index=$boardIndex"
        }
        
        if ($params.Count -gt 0) {
            $uri += "?" + ($params -join "&")
        }
        
        try {
            $headers = @{
                Authorization = "Bearer $($this.AccessToken)"
            }
            
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
            
            if ($response.status -eq "success") {
                return $response.data.coordinates
            }
            
            return @()
        }
        catch {
            Write-Error "座標取得エラー: $_"
            return @()
        }
    }
    
    [hashtable] CreateCoordinate([string]$lotNumber, [int]$boardIndex, [double]$x, [double]$y, [string]$defectType) {
        $body = @{
            lot_number = $lotNumber
            board_index = $boardIndex
            x = $x
            y = $y
            defect_type = $defectType
        } | ConvertTo-Json
        
        try {
            $headers = @{
                Authorization = "Bearer $($this.AccessToken)"
                'Content-Type' = "application/json"
            }
            
            $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/coordinates/create" -Method Post -Body $body -Headers $headers
            
            if ($response.status -eq "success") {
                return $response.data
            }
            
            return $null
        }
        catch {
            Write-Error "座標作成エラー: $_"
            return $null
        }
    }
}

# 使用例
function Main {
    $client = [ImageCoordsAPIClient]::new()
    
    # ログイン
    if ($client.Login("user001", "password123")) {
        Write-Host "ログイン成功"
        
        # 座標一覧取得
        $coordinates = $client.GetCoordinates("LOT2025001")
        Write-Host "座標数: $($coordinates.Count)"
        
        # 新しい座標作成
        $newCoord = $client.CreateCoordinate("LOT2025001", 1, 175.0, 275.0, "ショート")
        
        if ($newCoord) {
            Write-Host "座標作成成功: $($newCoord.id)"
        }
    }
    else {
        Write-Host "ログイン失敗"
    }
}

# 実行
Main
```

---

## API サーバー実装

### Flask ベースのAPI サーバー

```python
# api_server.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import json
from pathlib import Path

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 本番では環境変数から取得
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

# API エンドポイントの実装
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 認証ロジック（実際の実装では、データベースやファイルから検証）
        if username == 'user001' and password == 'password123':
            access_token = create_access_token(identity=username)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'access_token': access_token,
                    'expires_in': 3600,
                    'user': {
                        'id': username,
                        'name': '田中太郎',
                        'role': 'operator',
                        'permissions': ['view_coordinates', 'edit_coordinates']
                    }
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'ユーザー名またはパスワードが正しくありません'
                }
            }), 401
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@app.route('/api/v1/coordinates/list', methods=['GET'])
@jwt_required()
def get_coordinates():
    try:
        lot_number = request.args.get('lot_number')
        board_index = request.args.get('board_index', type=int)
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # 実際の実装では、データベースやファイルから座標を取得
        coordinates = [
            {
                'id': 'coord_001',
                'lot_number': 'LOT2025001',
                'board_index': 1,
                'x': 125.5,
                'y': 230.8,
                'defect_type': 'ショート',
                'created_at': '2025-08-18T10:30:00Z',
                'updated_at': '2025-08-18T10:30:00Z',
                'created_by': get_jwt_identity()
            }
        ]
        
        # フィルタリング
        if lot_number:
            coordinates = [c for c in coordinates if c['lot_number'] == lot_number]
        if board_index is not None:
            coordinates = [c for c in coordinates if c['board_index'] == board_index]
        
        # ページネーション
        total_count = len(coordinates)
        coordinates = coordinates[offset:offset + limit]
        
        return jsonify({
            'status': 'success',
            'data': {
                'coordinates': coordinates,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

---

**最終更新**: 2025年8月18日  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot
