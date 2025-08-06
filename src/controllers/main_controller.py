"""
メインコントローラー
アプリケーション全体の制御と他のコントローラーとの連携を管理
"""
import tkinter as tk
from datetime import date, datetime
from typing import Dict, Any, List, Tuple, Optional


class MainController:
    """メインアプリケーションコントローラー"""
    
    def __init__(self, coordinate_model, settings_model, worker_model, image_model,
                 main_view, canvas_view, sidebar_view, dialogs,
                 coordinate_controller, file_controller):
        
        # モデル
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        self.image_model = image_model
        
        # ビュー
        self.main_view = main_view
        self.canvas_view = canvas_view
        self.sidebar_view = sidebar_view
        self.dialogs = dialogs
        
        # 他のコントローラー
        self.coordinate_controller = coordinate_controller
        self.file_controller = file_controller
        
        # 現在の日付
        self.current_date = date.today()
        
        # 初期化フラグ
        self.is_initialized = False
    
    def initialize_application(self):
        """アプリケーションを初期化"""
        if self.is_initialized:
            return
        
        # 作業者入力
        self._setup_worker_input()
        
        # コントローラー間の連携を設定
        self.coordinate_controller.set_canvas_view(self.canvas_view)
        
        # ビューのコールバックを設定
        self._setup_view_callbacks()
        
        # ビューのイベントバインドを設定
        self._setup_canvas_events()
        
        # UI要素を初期化
        self._initialize_ui_elements()
        
        # 設定を読み込んで適用
        self._apply_settings()
        
        self.is_initialized = True
    
    def _setup_worker_input(self):
        """作業者入力ダイアログを表示"""
        dialog = self.dialogs['WorkerInputDialog'](self.main_view.root, self.worker_model)
        result = dialog.show()
        
        if result is None:
            # キャンセルされた場合はアプリを終了
            self.main_view.root.quit()
            return
        
        # 作業者情報をサイドバーに設定
        self.sidebar_view.worker_var.set(result['worker_no'])
    
    def _setup_view_callbacks(self):
        """ビューのコールバック関数を設定"""
        # メインビューのコールバック
        main_callbacks = {
            'select_date': self.select_date,
            'on_mode_change': self.on_mode_change,
            'open_settings': self.open_settings,
            'undo': self.undo_action,
            'redo': self.redo_action,
            'select_image': self.select_image,
            'load_json': self.load_json,
            'save_coordinates': self.save_coordinates,
            'clear_coordinates': self.clear_coordinates
        }
        self.main_view.set_callbacks(main_callbacks)
        
        # キャンバスビューのコールバック
        canvas_callbacks = {
            'on_left_click': self.on_canvas_left_click,
            'on_right_click': self.on_canvas_right_click,
            'on_view_click': self.on_canvas_view_click
        }
        self.canvas_view.set_callbacks(canvas_callbacks)
        
        # サイドバービューのコールバック
        sidebar_callbacks = {
            'on_form_data_changed': self.on_form_data_changed,
            'search_coordinates': self.search_coordinates
        }
        self.sidebar_view.set_callbacks(sidebar_callbacks)
    
    def _setup_canvas_events(self):
        """キャンバスのイベントバインドを設定"""
        # 初期モードに基づいてイベントを設定
        current_mode = self.main_view.get_current_mode()
        mode = "edit" if current_mode == "編集" else "view"
        self.canvas_view.bind_events(mode)
    
    def _initialize_ui_elements(self):
        """UI要素を初期化"""
        # トップコントロールを設定
        self.main_view.setup_top_controls()
        self.main_view.setup_menu_buttons()
        
        # 日付表示を更新
        self.main_view.update_date_label(self.current_date.strftime('%Y-%m-%d'))
        
        # モデル選択肢を更新
        self._update_model_options()
        
        # 不良項目選択肢を更新
        defects = self.file_controller.load_defects_from_file()
        self.sidebar_view.update_defect_options(defects)
        
        # Undo/Redoボタンの状態を更新
        self._update_undo_redo_state()
    
    def _apply_settings(self):
        """設定を適用"""
        # デフォルトモードを設定
        default_mode = self.settings_model.default_mode
        self.main_view.set_mode(default_mode)
        self.on_mode_change()
    
    def _update_model_options(self):
        """モデル選択肢を更新"""
        image_files = self.image_model.load_image_files_from_directory(
            self.settings_model.image_directory
        )
        
        model_names = self.image_model.get_image_names()
        if not model_names:
            model_names = ["画像ディレクトリが未設定"]
        
        self.sidebar_view.update_model_options(model_names)
    
    def _update_undo_redo_state(self):
        """Undo/Redoボタンの状態を更新"""
        can_undo = self.coordinate_controller.can_undo()
        can_redo = self.coordinate_controller.can_redo()
        self.main_view.update_undo_redo_state(can_undo, can_redo)
    
    # イベントハンドラー
    def on_mode_change(self):
        """モード変更時の処理"""
        current_mode = self.main_view.get_current_mode()
        
        if current_mode == "編集":
            # 編集モード
            self.canvas_view.bind_events("edit")
            self.sidebar_view.set_readonly_mode(False)
            print("[モード変更] 編集モードに切り替えました")
        else:
            # 閲覧モード
            self.canvas_view.bind_events("view")
            self.sidebar_view.set_readonly_mode(True)
            print("[モード変更] 閲覧モードに切り替えました")
            
            # 座標がある場合は概要情報を表示
            if self.coordinate_model.coordinates:
                summary = self.coordinate_controller.get_coordinate_summary()
                self.sidebar_view.display_coordinate_summary(summary)
                
                # 最初の座標を自動選択
                self.coordinate_controller.set_current_coordinate(0)
                detail = self.coordinate_controller.get_current_coordinate_detail()
                if detail:
                    self.sidebar_view.display_coordinate_info(detail, 0)
        
        # ハイライトをクリア（モード変更時は一旦リセット）
        if current_mode == "編集":
            self.canvas_view.clear_highlight()
    
    def on_canvas_left_click(self, event):
        """キャンバス左クリック（編集モード）"""
        x, y = int(event.x), int(event.y)
        
        # 座標を追加
        index = self.coordinate_controller.add_coordinate(x, y)
        
        # 新しい座標を選択状態にする
        self.coordinate_controller.set_current_coordinate(index)
        
        # フォームをクリアして項目番号を設定
        self.sidebar_view.clear_form()
        self.sidebar_view.item_number_var.set(str(index + 1))
        
        # リファレンス入力フィールドにフォーカス
        self.sidebar_view.focus_reference_entry()
        
        # Undo/Redoボタンの状態を更新
        self._update_undo_redo_state()
    
    def on_canvas_right_click(self, event):
        """キャンバス右クリック（編集モード）"""
        x, y = int(event.x), int(event.y)
        
        # 最も近い座標を選択
        selected_index = self.coordinate_controller.select_coordinate(x, y)
        
        if selected_index is not None:
            # フォームを選択した座標の詳細情報で更新
            detail = self.coordinate_controller.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.set_coordinate_detail(detail)
                self.sidebar_view.item_number_var.set(str(selected_index + 1))
            
            print(f"座標 {selected_index + 1} を選択しました")
    
    def on_canvas_view_click(self, event):
        """キャンバスクリック（閲覧モード）"""
        x, y = int(event.x), int(event.y)
        
        # 最も近い座標を選択
        selected_index = self.coordinate_controller.select_coordinate(x, y)
        
        if selected_index is not None:
            # 選択した座標の詳細情報を表示
            detail = self.coordinate_controller.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.display_coordinate_info(detail, selected_index)
            
            print(f"[閲覧モード] 座標 {selected_index + 1} を選択しました")
        else:
            # 座標が選択されていない場合はフォームをクリア
            self.coordinate_model.set_current_coordinate(-1)
            self.sidebar_view.clear_form()
            self.canvas_view.clear_highlight()
            print("[閲覧モード] 座標の選択を解除しました")
    
    def on_form_data_changed(self):
        """フォームデータ変更時の処理"""
        # 現在選択中の座標があれば詳細情報を更新
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            detail = self.sidebar_view.get_coordinate_detail()
            self.coordinate_controller.update_current_coordinate_detail(detail)
        
        # 座標が存在し、現在のJSONファイルがある場合のみ自動更新
        coordinates = self.coordinate_controller.get_all_coordinates()
        
        if coordinates and self.file_controller.current_json_path:
            try:
                # 座標詳細情報を取得
                coordinate_details = self.coordinate_controller.get_all_coordinate_details()
                
                # 現在のロット番号と作業者Noを取得
                form_data = self.sidebar_view.get_form_data()
                lot_number = form_data['lot_number']
                worker_no = form_data['worker_no']
                
                # 自動更新保存
                if self.file_controller.save_coordinates_with_auto_update(
                    coordinates, coordinate_details, lot_number, worker_no
                ):
                    print(f"JSONファイルを自動更新しました: {self.file_controller.current_json_path}")
                
            except Exception as e:
                print(f"自動更新エラー: {e}")
    
    # アクション
    def select_date(self):
        """日付選択ダイアログを表示"""
        dialog = self.dialogs['DateSelectDialog'](self.main_view.root, self.current_date)
        result = dialog.show()
        
        if result and not result['cancelled'] and result['date']:
            self.current_date = result['date']
            self.main_view.update_date_label(result['date'].strftime('%Y-%m-%d'))
    
    def open_settings(self):
        """設定ダイアログを開く"""
        dialog = self.dialogs['SettingsDialog'](
            self.main_view.root, 
            self.settings_model, 
            self.on_settings_changed
        )
        dialog.show()
    
    def on_settings_changed(self):
        """設定変更時のコールバック"""
        # モデル選択リストを更新
        self._update_model_options()
    
    def select_image(self):
        """画像を選択"""
        file_path = self.file_controller.select_image_file()
        
        if not file_path:
            return
        
        try:
            # 画像を読み込み
            tk_image = self.image_model.load_image(
                file_path, 
                self.canvas_view.canvas_width, 
                self.canvas_view.canvas_height
            )
            
            if tk_image:
                # キャンバスに画像を表示
                self.canvas_view.display_image(
                    tk_image, 
                    self.image_model.display_size[0],
                    self.image_model.display_size[1]
                )
                
                # 座標をクリア
                self.coordinate_controller.clear_coordinates()
                
                # JSONパスをリセット
                self.file_controller.current_json_path = None
                
                print(f"画像を読み込みました: {file_path}")
            else:
                self.file_controller.show_error_message("画像の読み込みに失敗しました。")
                
        except Exception as e:
            self.file_controller.show_error_message(f"画像読み込みエラー: {e}")
    
    def load_json(self):
        """JSONファイルを読み込み"""
        file_path = self.file_controller.select_json_file()
        
        if not file_path:
            return
        
        try:
            # JSONデータを読み込み
            data = self.file_controller.load_json_data(file_path)
            parsed_data = self.file_controller.parse_loaded_data(data)
            
            # 画像パスをチェック
            image_path = parsed_data['image_path']
            if not self.file_controller.validate_image_path(image_path):
                self.file_controller.show_error_message("画像ファイルが見つかりません。")
                return
            
            # 画像を読み込み
            tk_image = self.image_model.load_image(
                image_path,
                self.canvas_view.canvas_width,
                self.canvas_view.canvas_height
            )
            
            if tk_image:
                # キャンバスに画像を表示
                self.canvas_view.display_image(
                    tk_image,
                    self.image_model.display_size[0],
                    self.image_model.display_size[1]
                )
                
                # 座標と詳細情報を設定
                self.coordinate_controller.load_coordinates_from_data(
                    parsed_data['coordinates'],
                    parsed_data['coordinate_details']
                )
                
                # サイドバーに基本情報を設定
                form_data = {
                    'lot_number': parsed_data['lot_number'],
                    'worker_no': parsed_data['worker_no']
                }
                self.sidebar_view.set_form_data(form_data)
                
                # ファイルパスを記録
                self.file_controller.current_json_path = file_path
                
                # 読み込み完了メッセージ
                coord_count = len(parsed_data['coordinates'])
                current_mode = self.main_view.get_current_mode()
                
                if current_mode == "閲覧":
                    self.file_controller.show_info_message(
                        f"JSONファイルを閲覧モードで読み込みました。\n"
                        f"座標数: {coord_count}個\n"
                        f"座標をクリックして詳細情報を確認できます。"
                    )
                else:
                    self.file_controller.show_info_message(
                        f"JSONファイルを読み込みました。\n座標数: {coord_count}個"
                    )
                
                print(f"JSONファイルを読み込みました: {file_path}")
            else:
                self.file_controller.show_error_message("画像の読み込みに失敗しました。")
                
        except Exception as e:
            self.file_controller.show_error_message(f"JSON読み込みエラー: {e}")
    
    def save_coordinates(self):
        """座標を保存"""
        coordinates = self.coordinate_controller.get_all_coordinates()
        
        if not coordinates:
            self.file_controller.show_info_message("座標がありません。")
            return
        
        try:
            # フォームデータを取得
            form_data = self.sidebar_view.get_form_data()
            
            # ロット番号をチェック
            if not form_data['lot_number'].strip():
                self.file_controller.show_error_message(
                    "ロット番号が入力されていません。\nロット番号を入力してから保存してください。"
                )
                return
            
            # 保存パスを生成または選択
            file_path = None
            
            # 自動的なファイルパス生成を試行
            if (form_data['save_name'] and 
                self.settings_model.data_directory != "未選択" and
                form_data.get('model')):
                
                file_path = self.file_controller.get_automatic_save_path(
                    self.current_date.strftime('%Y-%m-%d'),
                    form_data['model'],
                    form_data['lot_number'],
                    form_data['save_name']
                )
            
            if not file_path:
                # ファイル選択ダイアログを表示
                default_filename = f"{form_data['save_name']}.json" if form_data['save_name'] else "coordinates.json"
                file_path = self.file_controller.save_json_file(default_filename)
            
            if not file_path:
                return
            
            # 座標詳細情報を取得
            coordinate_details = self.coordinate_controller.get_all_coordinate_details()
            
            # 保存データを作成
            save_data = self.file_controller.create_save_data(
                coordinates,
                self.image_model.current_image_path,
                coordinate_details,
                form_data['lot_number'],
                form_data['worker_no']
            )
            
            # データを保存
            if self.file_controller.save_json_data(file_path, save_data):
                self.file_controller.show_success_message(
                    f"座標をJSON形式で保存しました。\n保存先: {file_path}"
                )
                print(f"座標を保存しました: {file_path}")
            
        except Exception as e:
            self.file_controller.show_error_message(f"保存エラー: {e}")
    
    def clear_coordinates(self):
        """座標をクリア"""
        self.coordinate_controller.clear_coordinates()
        self.sidebar_view.clear_form()
        self._update_undo_redo_state()
    
    def undo_action(self):
        """元に戻す操作"""
        if self.coordinate_controller.undo():
            self._update_undo_redo_state()
    
    def redo_action(self):
        """やり直し操作"""
        if self.coordinate_controller.redo():
            self._update_undo_redo_state()
    
    def search_coordinates(self):
        """座標検索機能（閲覧モード用）"""
        # TODO: 座標検索機能を実装
        print("検索機能は今後実装予定です。")
