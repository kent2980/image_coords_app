"""
Main Application Module
メインアプリケーション - デザインと機能を統合
"""

import tkinter as tk
import os
from .ui_components import UIComponents
from .coordinate_manager import CoordinateManager
from .file_manager import FileManager


class CoordinateApp:
    """座標管理アプリケーションのメインクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # 各モジュールを初期化
        self.coordinate_manager = CoordinateManager()
        self.file_manager = FileManager()
        
        # UIコンポーネントを初期化（コールバック関数を設定）
        callbacks = {
            'select_date': self.select_date,
            'on_mode_change': self.on_mode_change,
            'open_settings': self.open_settings,
            'undo_action': self.undo_action,
            'redo_action': self.redo_action,
            'on_settings_changed': self.on_settings_changed,
            'on_image_loaded': self.on_image_loaded,
            'load_models_from_file': self.load_models_from_file,
            'load_image_for_display': self.load_image_for_display
        }
        self.ui = UIComponents(self.root, callbacks)
        
        # UIをセットアップ
        self._setup_ui()
        
        # 設定を読み込んでデフォルト値を適用
        self._load_and_apply_settings()
        
        # メニューボタンを設定
        self._setup_menu_buttons()
        
        # イベントバインド
        self._bind_events()
        
    def _setup_ui(self):
        """UIをセットアップ"""
        self.ui.setup_main_layout()
        self.ui.setup_date_display()
        self.ui.setup_undo_redo_buttons()
        self.ui.setup_settings_button()
        self.ui.setup_mode_selection()
        self.ui.setup_canvas_top()
        
        # キャンバスをセットアップして参照を保持
        self.canvas = self.ui.setup_canvas()
        
        self.ui.setup_sidebar()
        
        # 初期画像を表示（キャンバス作成後）
        self.ui._load_and_display_image()
        
    def _load_and_apply_settings(self):
        """設定を読み込んで適用"""
        # FileManagerから設定を読み込み
        settings = self.file_manager._load_settings_from_ini()
        
        # デフォルトモードを適用
        default_mode = settings.get('default_mode', '編集')
        self.ui.mode_var.set(default_mode)
        
        # モード変更を適用
        self.on_mode_change()
        
    def _setup_menu_buttons(self):
        """メニューボタンを設定"""
        # メニューフレーム
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 画像選択ボタン
        select_button = tk.Button(
            menu_frame,
            text="画像を選択",
            command=self.select_image,
            font=("Arial", 10)
        )
        select_button.pack(side=tk.LEFT, padx=5)
        
        # JSON読み込みボタン
        load_button = tk.Button(
            menu_frame,
            text="JSONを読み込み",
            command=self.load_json,
            font=("Arial", 10)
        )
        load_button.pack(side=tk.LEFT, padx=5)
        
        # 保存ボタン
        save_button = tk.Button(
            menu_frame,
            text="座標を保存",
            command=self.save_coordinates,
            font=("Arial", 10)
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # クリアボタン
        clear_button = tk.Button(
            menu_frame,
            text="座標をクリア",
            command=self.clear_coordinates,
            font=("Arial", 10)
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
    def _bind_events(self):
        """イベントをバインド"""
        self.canvas.bind("<Button-1>", self.on_click)
        
    def on_mode_change(self):
        """モード変更時の処理"""
        if self.ui.mode_var.get() == "編集":
            self.canvas.bind("<Button-1>", self.on_click)
        else:
            self.canvas.unbind("<Button-1>")
            
    def on_click(self, event):
        """キャンバスクリック時の処理"""
        x, y = event.x, event.y
        
        # 座標を追加
        self.coordinate_manager.add_coordinate(x, y)
        
        # マーカーを描画
        self.coordinate_manager.draw_coordinate_marker(self.canvas, x, y)
        
    def select_date(self):
        """日付選択ダイアログを表示"""
        result = self.file_manager.create_date_dialog(self.root, self.ui.selected_date)
        
        if not result['cancelled'] and result['date']:
            self.ui.selected_date = result['date']
            self.ui.update_date_label(result['date'])
            
    def select_image(self):
        """画像を選択"""
        file_path = self.file_manager.select_image_file()
        
        if not file_path:
            return
            
        try:
            # 画像を読み込み
            tk_img = self.coordinate_manager.load_image(file_path)
            
            # キャンバスサイズを設定
            self.canvas.config(
                width=self.ui.CANVAS_WIDTH,
                height=self.ui.CANVAS_HEIGHT
            )
            
            # キャンバスをクリアして画像を表示
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=tk_img)
            
            # 座標をクリア
            self.coordinate_manager.clear_coordinates()
            
            # JSONパスをリセット
            self.file_manager.current_json_path = None
            
        except Exception as e:
            self.file_manager.show_error_message(str(e))
            
    def load_json(self):
        """JSONファイルを読み込み"""
        file_path = self.file_manager.select_json_file()
        
        if not file_path:
            return
            
        try:
            # JSONデータを読み込み
            data = self.file_manager.load_json_data(file_path)
            parsed_data = self.file_manager.parse_loaded_data(data)
            
            # 画像パスをチェック
            image_path = parsed_data['image_path']
            if not image_path:
                self.file_manager.show_error_message("画像パスがJSONに含まれていません。")
                return
                
            # 画像を読み込み
            tk_img = self.coordinate_manager.load_image(image_path)
            
            # キャンバスを設定
            self.canvas.config(
                width=self.ui.CANVAS_WIDTH,
                height=self.ui.CANVAS_HEIGHT
            )
            
            # 座標を設定
            self.coordinate_manager.set_coordinates(parsed_data['coordinates'])
            
            # キャンバスを再描画
            self.coordinate_manager.redraw_all_markers(self.canvas)
            
            # フォームデータを設定
            self.ui.set_form_data(parsed_data['form_data'])
            
            # ファイルパスを記憶
            self.file_manager.current_json_path = file_path
            
        except Exception as e:
            self.file_manager.show_error_message(str(e))
            
    def save_coordinates(self):
        """座標を保存"""
        coordinates = self.coordinate_manager.get_coordinates()
        
        if not coordinates:
            self.file_manager.show_info_message("座標がありません。")
            return
            
        try:
            # フォームデータを取得
            form_data = self.ui.get_form_data()
            
            # 保存ファイル名を生成
            save_name = form_data.get('save_name', '')
            default_filename = f"{save_name}.json" if save_name else "coordinates.json"
            
            # 保存先を選択
            file_path = self.file_manager.save_json_file(default_filename)
            
            if not file_path:
                return
                
            # 保存データを作成
            save_data = self.file_manager.create_save_data(
                coordinates,
                self.coordinate_manager.get_current_image_path() or "",
                form_data
            )
            
            # データを保存
            self.file_manager.save_json_data(file_path, save_data)
            
            self.file_manager.show_success_message("座標をJSON形式で保存しました。")
            
        except Exception as e:
            self.file_manager.show_error_message(str(e))
            
    def clear_coordinates(self):
        """座標をクリア"""
        self.coordinate_manager.clear_coordinates()
        self.coordinate_manager.redraw_all_markers(self.canvas)
        
    def open_settings(self):
        """設定ダイアログを開く"""
        self.file_manager.create_settings_dialog(self.root, self.on_settings_changed)
    
    def on_settings_changed(self):
        """設定変更時のコールバック"""
        # モデル選択リストを更新
        self.ui.update_model_combobox()
    
    def undo_action(self):
        """元に戻す操作"""
        if self.coordinate_manager.undo():
            self.coordinate_manager.redraw_all_markers(self.canvas)
            
    def redo_action(self):
        """進む操作"""
        if self.coordinate_manager.redo():
            self.coordinate_manager.redraw_all_markers(self.canvas)
    
    def on_image_loaded(self, image_info):
        """画像が読み込まれた際のコールバック"""
        # coordinate_managerに画像情報を設定
        self.coordinate_manager.set_image_info(image_info)
        
        # マーカーをクリア（新しい画像なので）
        self.coordinate_manager.clear_markers()
        self.coordinate_manager.redraw_all_markers(self.canvas)
    
    def load_models_from_file(self):
        """設定で指定された画像ディレクトリから画像ファイル名を読み込み
        
        Returns:
            List[Dict[str, str]]: [{"filename": "フルパス"}, ...] 形式のリスト
        """
        try:
            # 設定ファイルから画像ディレクトリを取得
            settings = self.file_manager._load_settings_from_ini()
            image_directory = settings.get('image_directory', '')
            
            if image_directory and image_directory != "未選択":
                # 画像ディレクトリから画像ファイル名とフルパスを取得
                image_files_dict = self._get_image_files_with_paths(image_directory)
                
                if image_files_dict:
                    return image_files_dict
                else:
                    # 画像ファイルが見つからない場合
                    return [{"画像なし": f"画像なし（{os.path.basename(image_directory)}）"}]
            else:
                # 画像ディレクトリが設定されていない場合
                return [{"画像ディレクトリが未設定": "画像ディレクトリが未設定"}]
                
        except Exception as e:
            # エラーが発生した場合はデフォルト値を返す
            print(f"画像ファイル読み込みエラー: {e}")
            return [{"設定エラー": "設定エラー"}]
    
    def _get_image_files_with_paths(self, directory):
        """指定されたディレクトリから画像ファイル名とフルパスの辞書リストを取得
        
        Returns:
            List[Dict[str, str]]: [{"filename": "フルパス"}, ...] 形式のリスト
        """
        import os
        
        if not directory or not os.path.exists(directory):
            return []
        
        # サポートする画像拡張子
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        
        try:
            image_files_dict = []
            for filename in os.listdir(directory):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    # 拡張子を取得して小文字に変換
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in image_extensions:
                        # 拡張子を除いたファイル名をキーに、フルパスを値にした辞書を作成
                        name_without_ext = os.path.splitext(filename)[0]
                        image_files_dict.append({name_without_ext: full_path})
            
            # ファイル名でソート
            return sorted(image_files_dict, key=lambda x: list(x.keys())[0])
            
        except Exception as e:
            print(f"画像ファイル読み込みエラー: {e}")
            return []
    
    def load_image_for_display(self, image_path):
        """表示用に画像を読み込み、coordinate_managerを使用してリサイズ"""
        try:
            # coordinate_managerのload_imageメソッドを使用
            tk_image = self.coordinate_manager.load_image(image_path)
            
            # 画像情報を取得（元のサイズなど）
            from PIL import Image
            with Image.open(image_path) as pil_image:
                orig_width, orig_height = pil_image.size
            
            # 表示サイズを計算（UIComponentsの定数を使用）
            canvas_width = self.ui.CANVAS_WIDTH
            canvas_height = self.ui.CANVAS_HEIGHT
            
            # アスペクト比を計算
            aspect_ratio = orig_width / orig_height
            
            # キャンバスに収まるサイズを計算
            if aspect_ratio > canvas_width / canvas_height:
                # 横長の画像
                new_width = canvas_width
                new_height = int(canvas_width / aspect_ratio)
            else:
                # 縦長の画像
                new_height = canvas_height
                new_width = int(canvas_height * aspect_ratio)
            
            return {
                'tk_image': tk_image,
                'display_width': new_width,
                'display_height': new_height,
                'original_width': orig_width,
                'original_height': orig_height,
                'image_path': image_path
            }
            
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return None
        
    def run_app(self):
        """アプリケーションを実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CoordinateApp()
    app.run_app()