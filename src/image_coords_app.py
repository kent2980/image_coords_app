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
            'load_image_for_display': self.load_image_for_display,
            'setup_json_save_dir': self._setup_json_save_dir,
            'setup_save_name_entry': self._setup_save_name_entry,
            'on_form_data_changed': self.on_form_data_changed,
            'save_json': self.save_coordinates,
            'search_coordinates': self.search_coordinates
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

        # 保存先ディレクトリをセットアップ
        self._setup_save_name_entry()

        # 保存名エントリをセットアップ
        self._setup_save_name_entry()
        
        # 作業者入力ダイアログを表示
        self._setup_worker_input()

    def _setup_worker_input(self):
        """作業者入力を設定"""
        worker_name = self.ui.show_worker_input_dialog()
        if worker_name is None:
            # 作業者入力がキャンセルされた場合はアプリを終了
            return

    def _setup_json_save_dir(self):
        """ 
        JSONファイルの保存先ディレクトリを作成 
        \データディレクトリ\日付\モデル名\ロット番号\
        
        Returns:
            str: 作成されたディレクトリのパス（作成できない場合はNone）
        """
        try:
            # 設定を読み込み
            settings = self.file_manager._load_settings_from_ini()
            data_directory = settings.get('data_directory', '')
            
            if not data_directory or data_directory == "未選択":
                print("データディレクトリが設定されていません。")
                return None
            
            # データディレクトリが存在するかチェック、存在しない場合は作成
            if not os.path.exists(data_directory):
                try:
                    os.makedirs(data_directory, exist_ok=True)
                    print(f"データディレクトリを作成しました: {data_directory}")
                except Exception as e:
                    print(f"データディレクトリの作成に失敗しました: {data_directory}, エラー: {e}")
                    return None
            
            # 現在の日付を取得（YYYY-MM-DD形式）
            current_date = self.ui.selected_date.strftime('%Y-%m-%d')
            
            # 現在選択されているモデル名を取得
            model_name = self.ui.model_var.get()
            
            if not model_name or model_name.startswith("画像") or model_name == "設定エラー":
                print("有効なモデルが選択されていません。")
                return None
            
            # 現在のロット番号を取得
            lot_number = self.ui.get_current_lot_number()
            
            if not lot_number or lot_number.strip() == "":
                print("ロット番号が設定されていません。")
                return None
            
            # ディレクトリパスを構築: データディレクトリ\日付\モデル名\ロット番号
            save_dir = os.path.join(data_directory, current_date, model_name, lot_number)
            
            # ディレクトリを作成（存在しない場合）
            os.makedirs(save_dir, exist_ok=True)
            
            print(f"保存ディレクトリを作成/確認しました: {save_dir}")
            return save_dir
            
        except Exception as e:
            print(f"保存ディレクトリ作成エラー: {e}")
            return None
    
    def _get_next_sequential_number(self, directory):
        """指定されたディレクトリ内の連番ファイル名の次の番号を取得
        
        Args:
            directory (str): 検索対象のディレクトリパス
            
        Returns:
            int: 次の連番（0001から開始）
        """
        if not directory or not os.path.exists(directory):
            return 1
        
        try:
            # ディレクトリ内のJSONファイルを検索
            json_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json') and os.path.isfile(os.path.join(directory, filename)):
                    # ファイル名から数字部分を抽出
                    name_without_ext = os.path.splitext(filename)[0]
                    
                    # 4桁の数字のみのファイル名かチェック
                    if name_without_ext.isdigit() and len(name_without_ext) == 4:
                        json_files.append(int(name_without_ext))
            
            if not json_files:
                # 連番ファイルが存在しない場合は1から開始
                return 1
            
            # 最大値の次の番号を返す
            return max(json_files) + 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def _setup_save_name_entry(self):
        """保存名エントリに連番ファイル名を自動設定"""
        try:
            # 現在の保存名をチェック
            current_save_name = self.ui.save_name_var.get()
            
            # 保存名が空の場合のみ自動設定
            if not current_save_name.strip():
                # 保存ディレクトリを取得
                save_dir = self._setup_json_save_dir()
                
                if save_dir:
                    # 次の連番を取得
                    next_number = self._get_next_sequential_number(save_dir)
                    
                    # 4桁ゼロパディングで保存名を設定
                    auto_save_name = f"{next_number:04d}"
                    self.ui.save_name_var.set(auto_save_name)
                    
                    print(f"保存名を自動設定しました: {auto_save_name}")
                    
        except Exception as e:
            print(f"保存名自動設定エラー: {e}")

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
        self.canvas.bind("<Button-3>", self.on_right_click)  # 右クリックで座標選択
        
    def on_right_click(self, event):
        """右クリック時の処理 - 既存座標の選択"""
        x, y = event.x, event.y
        
        # 最も近い座標を検索
        min_distance = float('inf')
        selected_index = -1
        
        for i, (coord_x, coord_y) in enumerate(self.coordinate_manager.coordinates):
            distance = ((x - coord_x) ** 2 + (y - coord_y) ** 2) ** 0.5
            if distance < 20 and distance < min_distance:  # 20ピクセル以内
                min_distance = distance
                selected_index = i
        
        if selected_index >= 0:
            # 座標を選択
            self.coordinate_manager.set_current_coordinate(selected_index)
            
            # フォームを選択した座標の詳細情報で更新
            detail = self.coordinate_manager.get_current_coordinate_detail()
            if detail:
                self.ui.update_form_with_coordinate_detail(detail)
            
            print(f"座標 {selected_index + 1} を選択しました")
        
    def on_mode_change(self):
        """モード変更時の処理"""
        current_mode = self.ui.mode_var.get()
        
        if current_mode == "編集":
            # 編集モード: 左クリックで座標追加、右クリックで座標選択
            self.canvas.bind("<Button-1>", self.on_click)
            self.canvas.bind("<Button-3>", self.on_right_click)
            # サイドバーを編集可能にする
            self.ui.set_readonly_mode(False)
            # サイドバータイトルをリセット
            self.ui.reset_sidebar_title_for_viewing()
            print("[モード変更] 編集モードに切り替えました")
        else:
            # 閲覧モード: 左クリックで座標選択のみ
            self.canvas.bind("<Button-1>", self.on_view_click)
            self.canvas.unbind("<Button-3>")
            # サイドバーを読み取り専用にする
            self.ui.set_readonly_mode(True)
            print("[モード変更] 閲覧モードに切り替えました")
            
            # 座標がある場合は概要情報を表示し、最初の座標を自動選択
            if self.coordinate_manager.coordinates:
                # 座標概要情報を表示
                summary = self.coordinate_manager.get_coordinate_summary()
                self.ui.display_coordinate_summary_for_viewing(summary)
                
                # 最初の座標を選択
                self.coordinate_manager.set_current_coordinate(0)
                detail = self.coordinate_manager.get_current_coordinate_detail()
                if detail:
                    self.ui.display_coordinate_info_for_viewing(detail, 0)
                self._highlight_selected_coordinate(0)
                print("[閲覧モード] 最初の座標を自動選択しました")
            
        # ハイライトをクリア（モード変更時は一旦リセット）
        if current_mode == "編集":
            self._clear_highlight()
            
    def on_view_click(self, event):
        """閲覧モード時のキャンバスクリック処理"""
        x, y = event.x, event.y
        
        # 最も近い座標を検索
        min_distance = float('inf')
        selected_index = -1
        
        for i, (coord_x, coord_y) in enumerate(self.coordinate_manager.coordinates):
            distance = ((x - coord_x) ** 2 + (y - coord_y) ** 2) ** 0.5
            if distance < 20 and distance < min_distance:  # 20ピクセル以内
                min_distance = distance
                selected_index = i
        
        if selected_index >= 0:
            # 座標を選択
            self.coordinate_manager.set_current_coordinate(selected_index)
            
            # フォームを選択した座標の詳細情報で更新（閲覧モード用）
            detail = self.coordinate_manager.get_current_coordinate_detail()
            if detail:
                # 閲覧モード専用の詳細表示を使用
                self.ui.display_coordinate_info_for_viewing(detail, selected_index)
                
            # 選択した座標をハイライト表示
            self._highlight_selected_coordinate(selected_index)
            
            print(f"[閲覧モード] 座標 {selected_index + 1} を選択しました")
        else:
            # 座標が選択されていない場合はフォームをクリア
            self.coordinate_manager.current_coordinate_index = -1
            self.ui.clear_form()
            self._clear_highlight()
            print("[閲覧モード] 座標の選択を解除しました")
    
    def _highlight_selected_coordinate(self, index):
        """選択された座標をハイライト表示"""
        # coordinate_managerの新しいハイライト機能を使用
        self.coordinate_manager.highlight_coordinate(self.canvas, index)
    
    def _clear_highlight(self):
        """ハイライト表示をクリア"""
        # coordinate_managerの新しいクリア機能を使用
        self.coordinate_manager.clear_highlight(self.canvas)
            
    def on_click(self, event):
        """キャンバスクリック時の処理"""
        x, y = event.x, event.y
        
        # 座標を追加
        self.coordinate_manager.add_coordinate(x, y)
        
        # マーカーを描画（座標数を番号として使用）
        number = len(self.coordinate_manager.coordinates)
        self.coordinate_manager.draw_coordinate_marker(self.canvas, x, y, number)

        # 新しい座標を選択状態にする
        new_index = len(self.coordinate_manager.coordinates) - 1
        self.coordinate_manager.set_current_coordinate(new_index)
        
        # 新しい座標なのでフォームをクリア
        self.ui.clear_form()
        
        # 項目番号のみ設定（座標の番号）
        self.ui.item_number_var.set(str(number))
        
        # リファレンス入力フィールドにフォーカスを当てる
        self.ui.focus_reference_entry()

        
    def select_date(self):
        """日付選択ダイアログを表示"""
        result = self.file_manager.create_date_dialog(self.root, self.ui.selected_date)
        
        if not result['cancelled'] and result['date']:
            self.ui.selected_date = result['date']
            self.ui.update_date_label(result['date'])
            
            # 日付が変更されたら保存名エントリを更新
            self._setup_save_name_entry()
            
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
            
            # 座標と詳細情報を設定
            self.coordinate_manager.set_coordinates_with_details(
                parsed_data['coordinates'], 
                parsed_data.get('coordinate_details', [])
            )
            
            # ロット番号をUIに設定
            if 'lot_number' in parsed_data and parsed_data['lot_number']:
                self.ui.set_current_lot_number(parsed_data['lot_number'])
            else:
                self.ui.set_current_lot_number("")
            
            # 作業者NoをUIに設定
            if 'worker_no' in parsed_data and parsed_data['worker_no']:
                self.ui.set_current_worker(parsed_data['worker_no'])
            
            # キャンバスを再描画
            self.coordinate_manager.redraw_all_markers(self.canvas)
            
            # 座標数を表示
            coord_count = len(self.coordinate_manager.coordinates)
            print(f"JSONファイルを読み込みました: {coord_count}個の座標")
            
            # 閲覧モードの場合は座標概要を表示
            current_mode = self.ui.mode_var.get()
            if current_mode == "閲覧":
                # 座標概要情報を表示
                summary = self.coordinate_manager.get_coordinate_summary()
                self.ui.display_coordinate_summary_for_viewing(summary)
                
                # 最初の座標を選択して詳細表示
                if self.coordinate_manager.coordinates:
                    self.coordinate_manager.set_current_coordinate(0)
                    detail = self.coordinate_manager.get_current_coordinate_detail()
                    if detail:
                        self.ui.display_coordinate_info_for_viewing(detail, 0)
                    self._highlight_selected_coordinate(0)
                    print("[閲覧モード] 最初の座標を自動選択しました")
            elif current_mode == "編集" and self.coordinate_manager.coordinates:
                # 編集モードの場合は通常の表示
                self.coordinate_manager.set_current_coordinate(0)
                detail = self.coordinate_manager.get_current_coordinate_detail()
                if detail:
                    self.ui.update_form_with_coordinate_detail(detail)
            
            # ファイルパスを記憶
            self.file_manager.current_json_path = file_path
            
            # 読み込み完了メッセージ
            if current_mode == "閲覧":
                self.file_manager.show_info_message(
                    f"JSONファイルを閲覧モードで読み込みました。\n"
                    f"座標数: {coord_count}個\n"
                    f"座標をクリックして詳細情報を確認できます。"
                )
            
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
            
            # ロット番号をチェック
            current_lot_number = self.ui.get_current_lot_number()
            if not current_lot_number or current_lot_number.strip() == "":
                self.file_manager.show_error_message("ロット番号が入力されていません。\nロット番号を入力してから保存してください。")
                return
            
            # 保存ディレクトリを作成
            save_dir = self._setup_json_save_dir()
            
            if not save_dir:
                # ディレクトリ作成に失敗した場合は従来の方法でファイル選択
                # （データディレクトリ、モデル名、またはロット番号が設定されていない場合）
                save_name = form_data.get('save_name', '')
                default_filename = f"{save_name}.json" if save_name else "coordinates.json"
                file_path = self.file_manager.save_json_file(default_filename)
            else:
                # 自動的にファイルパスを生成
                save_name = form_data.get('save_name', '')
                
                if save_name:
                    # 保存名が設定されている場合
                    filename = f"{save_name}.json"
                    file_path = os.path.join(save_dir, filename)
                    
                    # 同名ファイルが存在する場合は連番を付ける
                    counter = 1
                    while os.path.exists(file_path):
                        name_part = os.path.splitext(filename)[0]
                        file_path = os.path.join(save_dir, f"{name_part}_{counter:04d}.json")
                        counter += 1
                else:
                    # 保存名が設定されていない場合は連番ファイル名を生成
                    next_number = self._get_next_sequential_number(save_dir)
                    filename = f"{next_number:04d}.json"
                    file_path = os.path.join(save_dir, filename)
                    
                    # 保存名フィールドに生成されたファイル名（拡張子なし）を設定
                    self.ui.save_name_var.set(f"{next_number:04d}")
            
            if not file_path:
                return
                
            # 座標詳細情報を取得
            coordinate_details = self.coordinate_manager.get_all_coordinate_details()
            
            # 現在のロット番号と作業者Noを取得
            current_lot_number = self.ui.get_current_lot_number()
            current_worker_no = self.ui.get_current_worker()
                
            # 保存データを作成
            save_data = self.file_manager.create_save_data(
                coordinates,
                self.coordinate_manager.get_current_image_path() or "",
                coordinate_details,
                current_lot_number,
                current_worker_no
            )
            
            # データを保存
            self.file_manager.save_json_data(file_path, save_data)
            
            self.file_manager.show_success_message(f"座標をJSON形式で保存しました。\n保存先: {file_path}")
            
            # 保存名エントリを更新
            self._setup_save_name_entry()

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
    
    def on_form_data_changed(self):
        """フォームデータが変更された時の処理"""
        # 現在選択中の座標があれば詳細情報を更新
        if self.coordinate_manager.current_coordinate_index >= 0:
            detail = self.ui.get_current_coordinate_detail()
            self.coordinate_manager.update_current_coordinate_detail(detail)
        
        # 座標が存在し、現在のJSONファイルがある場合のみ自動更新
        coordinates = self.coordinate_manager.get_coordinates()
        
        if coordinates and hasattr(self.file_manager, 'current_json_path') and self.file_manager.current_json_path:
            try:
                # 座標詳細情報を取得
                coordinate_details = self.coordinate_manager.get_all_coordinate_details()
                
                # 現在のロット番号と作業者Noを取得
                current_lot_number = self.ui.get_current_lot_number()
                current_worker_no = self.ui.get_current_worker()
                
                # 保存データを作成
                save_data = self.file_manager.create_save_data(
                    coordinates,
                    self.coordinate_manager.get_current_image_path() or "",
                    coordinate_details,
                    current_lot_number,
                    current_worker_no
                )
                
                # 現在のJSONファイルを更新
                self.file_manager.save_json_data(self.file_manager.current_json_path, save_data)
                
                print(f"JSONファイルを自動更新しました: {self.file_manager.current_json_path}")
                
            except Exception as e:
                print(f"自動更新エラー: {e}")
    
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
    
    def search_coordinates(self):
        """座標検索機能（閲覧モード用）"""
        # TODO: 座標検索機能を実装
        print("検索機能は今後実装予定です。")
        
    def run_app(self):
        """アプリケーションを実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CoordinateApp()
    app.run_app()