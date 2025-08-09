# コード署名セットアップガイド

このガイドでは、Windows実行ファイルのコード署名を設定して、セキュリティアラートを改善する方法を説明します。

## 概要

コード署名により以下の利点があります：

- Windows Defenderなどのウイルス対策ソフトウェアでの誤検知を減らす
- ユーザーがアプリケーションを起動する際のセキュリティ警告を軽減
- アプリケーションの信頼性と真正性を向上

## 自動署名の仕組み

GitHub Actionsワークフローは以下の手順で自動的にコード署名を実行します：

### 1. 証明書の取得

- **GitHub Secrets利用**: 本番用の信頼できる証明書がある場合
- **自己署名証明書**: 開発・テスト用途で自動生成

### 2. Windows SDK のインストール

```powershell
choco install windows-sdk-10-version-2004-all
```

### 3. signtool.exe による署名

```powershell
signtool sign /f certificate.pfx /p password /fd SHA256 /tr http://timestamp.sectigo.com /td SHA256 executable.exe
```

## GitHub Secrets の設定（本番用）

信頼できる証明書機関から取得した証明書を使用する場合：

### 1. 証明書の準備

```powershell
# PFXファイルをBase64エンコード
$bytes = [System.IO.File]::ReadAllBytes("your-certificate.pfx")
$base64 = [System.Convert]::ToBase64String($bytes)
Write-Output $base64
```

### 2. GitHub リポジトリでのSecrets設定

1. リポジトリページ → Settings → Secrets and variables → Actions
2. 以下のSecretsを追加：
   - `CODE_SIGN_CERT`: Base64エンコードした証明書内容
   - `CODE_SIGN_PASSWORD`: 証明書のパスワード

## 証明書の種類と効果

### 自己署名証明書（現在の設定）

- **利点**: 無料、自動生成可能
- **制限**: ユーザーに「不明な発行元」として表示
- **用途**: 開発・内部配布用

### EV証明書（推奨）

- **利点**: 最高レベルの信頼性、SmartScreenフィルターを即座に通過
- **費用**: 年間数万円～
- **発行元**: DigiCert、Sectigo、GlobalSign など

### OV/DV証明書

- **利点**: コスト効率が良い、基本的な署名機能
- **制限**: 初回は警告が表示される場合あり
- **費用**: 年間数千円～

## トラブルシューティング

### signtool.exe が見つからない場合

```powershell
# Windows SDK の手動インストール
winget install Microsoft.WindowsSDK.10
```

### 署名検証失敗

```powershell
# 署名の詳細確認
signtool verify /pa /v /d executable.exe

# 証明書ストアの確認
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert
```

### タイムスタンプエラー

- 別のタイムスタンプサーバーを試用
- ネットワーク接続を確認
- 代替URL: `http://timestamp.digicert.com`

## セキュリティ考慮事項

### 証明書の保護

- GitHub Secretsに保存された証明書は暗号化される
- ビルド後に一時ファイルは自動削除される
- 証明書のパスワードは環境変数で管理

### アクセス制限

- Secretsはリポジトリの管理者のみが設定可能
- ワークフロー実行時のみアクセス可能

## 参考リンク

- [Microsoft Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [SignTool.exe Documentation](https://docs.microsoft.com/en-us/dotnet/framework/tools/signtool-exe)
- [Certificate Authority Comparison](https://certificateauthorities.org/)

## 推奨証明書プロバイダー

1. **DigiCert**: 業界標準、高い信頼性
2. **Sectigo (旧 Comodo)**: コストパフォーマンス良好
3. **GlobalSign**: 国際的な認知度
4. **Certum**: 価格競争力
