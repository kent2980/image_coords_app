"""
Main Controller
メインアプリケーションの制御を担当するコントローラー
"""

import tkinter as tk
from typing import Optional
from datetime import datetime, date
import os

from ..models import CoordinateModel, AppSettingsModel, WorkerModel, ImageModel
from ..views import MainView, CoordinateCanvasView, SidebarView
from ..views.dialogs import WorkerInputDialog, SettingsDialog, DateSelectDialog
from .coordinate_controller import CoordinateController
from .file_controller import FileController


class MainController:
    """メインコントローラークラス"""
    
    def __init__(self, coordinate_model=None, settings_model=None, worker_model=None, 
                 image_model=None, main_view=None, canvas_view=None, sidebar_view=None,
                 dialogs=None, coordinate_controller=None, file_controller=None):
        # 共通の初期化
        self.current_mode = "編集"
        self.current_lot_number = ""
        
        # 依存性注入：外部から提供されるか、新規作成するか
        if coordinate_model is None:
            # Tkinterルートウィンドウ（新規作成時のみ）
            self.root = tk.Tk()
            
            # Models（新規作成）
            self.coordinate_model = CoordinateModel()
            self.settings_model = AppSettingsModel()
            self.worker_model = WorkerModel()
            self.image_model = ImageModel()
            
            # Views（新規作成）
            self._create_views()
            
            # Controllers（新規作成）
            self._create_controllers()
        else:
            # 依存性注入された場合
            self.coordinate_model = coordinate_model
            self.settings_model = settings_model
            self.worker_model = worker_model
            self.image_model = image_model
            self.main_view = main_view
            self.canvas_view = canvas_view
            self.sidebar_view = sidebar_view
            self.dialogs = dialogs
            self.coordinate_controller = coordinate_controller
            self.file_controller = file_controller
            
            # 外部で作成されたルートウィンドウを使用
            self.root = self.main_view.root if self.main_view else tk.Tk()
    
    def _create_views(self):
        """ビューを作成（新規作成時のみ）"""
        from ..views import MainView, CoordinateCanvasView, SidebarView
        from ..views.dialogs import WorkerInputDialog, SettingsDialog, DateSelectDialog
        
        # メインビュー
        self.main_view = MainView(self.root)
        
        # キャンバスビュー
        self.canvas_view = CoordinateCanvasView(self.main_view.canvas_frame)
        
        # サイドバービュー
        self.sidebar_view = SidebarView(self.main_view.sidebar_frame)
        
        # ダイアログクラス
        self.dialogs = {
            'WorkerInputDialog': WorkerInputDialog,
            'SettingsDialog': SettingsDialog,
            'DateSelectDialog': DateSelectDialog
        }
    
    def _create_controllers(self):
        """コントローラーを作成（新規作成時のみ）"""
        # ファイルコントローラー
        self.file_controller = FileController(
            self.coordinate_model,
            self.settings_model,
            self.worker_model
        )
        
        # 座標コントローラー
        self.coordinate_controller = CoordinateController(
            self.coordinate_model,
            self.image_model
        )
    
    def initialize_application(self):
        """アプリケーションを初期化"""
        # 初期化処理
        self._setup_views()
        self._setup_callbacks()
        self._initialize_app()
    
    def _setup_views(self):
        """ビューを設定"""
        # メインビューのコールバックを設定
        self.main_view.set_callbacks({
            'select_date': self.select_date,
            'on_mode_change': self.on_mode_change,
            'open_settings': self.open_settings,
            'undo_action': self.undo_action,
            'redo_action': self.redo_action,
            'on_model_selected': self.on_model_selected,
            'on_lot_number_enter': self.on_lot_number_enter,
            'on_save_button_click': self.on_save_button_click,
            'search_coordinates': self.search_coordinates
        })
        
        # 各ビューコンポーネントをセットアップ
        self.main_view.setup_date_display()
        self.main_view.setup_undo_redo_buttons()
        self.main_view.setup_settings_button()
        self.main_view.setup_mode_selection()
        self.main_view.setup_canvas_top()
        
        # キャンバスビューとサイドバービューが既に存在しない場合は作成
        if self.canvas_view is None:
            canvas_frame = self.main_view.get_canvas_frame()
            self.canvas_view = CoordinateCanvasView(
                canvas_frame, 
                self.main_view.CANVAS_WIDTH, 
                self.main_view.CANVAS_HEIGHT
            )
        
        if self.sidebar_view is None:
            sidebar_frame = self.main_view.get_sidebar_frame()
            self.sidebar_view = SidebarView(sidebar_frame, self.current_mode)
        
        # キャンバスとサイドバーのコールバックを設定
        self._setup_canvas_callbacks()
        self._setup_sidebar_callbacks()
    
    def _setup_callbacks(self):
        """コールバック関数を設定"""
        # 座標コントローラーのコールバック
        self.coordinate_controller.set_callbacks({
            'on_coordinate_added': self.on_coordinate_added,
            'on_coordinate_selected': self.on_coordinate_selected,
            'on_coordinates_updated': self.on_coordinates_updated
        })
        
        # ファイルコントローラーのコールバック
        self.file_controller.set_callbacks({
            'on_data_loaded': self.on_data_loaded,
            'on_data_saved': self.on_data_saved,
            'on_settings_changed': self.on_settings_changed
        })
    
    def _setup_canvas_callbacks(self):
        """キャンバスのコールバックを設定"""
        if self.canvas_view:
            self.canvas_view.set_callbacks({
                'on_canvas_click': self.on_canvas_click,
                'on_canvas_right_click': self.on_canvas_right_click,
                'on_canvas_view_click': self.on_canvas_view_click
            })
            self.canvas_view.bind_events(self.current_mode)
    
    def _setup_sidebar_callbacks(self):
        """サイドバーのコールバックを設定"""
        if self.sidebar_view:
            # 不良名リストを設定
            defect_list = self._load_defects_from_file()
            self.sidebar_view.set_defect_list(defect_list)
            
            self.sidebar_view.set_callbacks({
                'on_form_data_changed': self.on_form_data_changed
            })
    
    def _initialize_app(self):
        """アプリケーションを初期化"""
        # 設定を読み込んでデフォルト値を適用
        self._load_and_apply_settings()
        
        # 作業者入力ダイアログを表示
        self._setup_worker_input()
        
        # モデル一覧を更新
        self._update_model_list()
        
        # 保存名エントリを設定
        self._setup_save_name_entry()
        
        # デフォルト画像を読み込み（少し遅延させる）
        self.root.after(100, self._load_default_model_image)
    
    def _load_and_apply_settings(self):
        """設定を読み込んで適用"""
        default_mode = self.settings_model.get_default_mode()
        self.main_view.set_mode(default_mode)
        self.current_mode = default_mode
        self.on_mode_change()
    
    def _setup_worker_input(self):
        """作業者入力を設定"""
        workers = self.worker_model.get_all_workers()
        dialog_class = self.dialogs['WorkerInputDialog']
        dialog = dialog_class(self.root, workers)
        worker_no = dialog.show()
        
        if worker_no is None:
            # 作業者入力がキャンセルされた場合はアプリを終了
            self.root.quit()
            return
        
        self.worker_model.set_current_worker(worker_no)
        worker_name = self.worker_model.get_current_worker_name()
        self.sidebar_view.update_worker_label(worker_name)
        print(f"作業者を設定しました: No.{worker_no} - {worker_name}")
    
    def _update_model_list(self):
        """モデル一覧を更新"""
        image_directory = self.settings_model.get_image_directory()
        if self.settings_model.is_image_directory_valid():
            image_list = self.image_model.load_images_from_directory(image_directory)
            self.main_view.update_model_combobox(image_list)
        else:
            self.main_view.update_model_combobox([{"画像ディレクトリが未設定": "未設定"}])
    
    def _setup_save_name_entry(self):
        """保存名エントリに連番ファイル名を自動設定"""
        try:
            form_data = self.main_view.get_form_data()
            current_save_name = form_data.get('save_name', '').strip()
            
            if not current_save_name:
                save_dir = self._get_save_directory()
                if save_dir:
                    next_number = self._get_next_sequential_number(save_dir)
                    auto_save_name = f"{next_number:04d}"
                    self.main_view.set_form_data({'save_name': auto_save_name})
                    print(f"保存名を自動設定しました: {auto_save_name}")
        except Exception as e:
            print(f"保存名自動設定エラー: {e}")
    
    def _get_save_directory(self) -> Optional[str]:
        """保存ディレクトリを取得"""
        try:
            if not self.settings_model.is_data_directory_valid():
                return None
            
            if not self.settings_model.ensure_data_directory_exists():
                return None
            
            # 現在の日付を取得
            current_date = self.main_view.selected_date.strftime('%Y-%m-%d')
            
            # 現在選択されているモデル名を取得
            form_data = self.main_view.get_form_data()
            model_name = form_data.get('model', '')
            
            if not model_name or model_name.startswith("画像"):
                return None
            
            if not self.current_lot_number:
                return None
            
            # ディレクトリパスを構築
            data_directory = self.settings_model.get_data_directory()
            save_dir = os.path.join(data_directory, current_date, model_name, self.current_lot_number)
            
            # ディレクトリを作成
            os.makedirs(save_dir, exist_ok=True)
            
            return save_dir
            
        except Exception as e:
            print(f"保存ディレクトリ取得エラー: {e}")
            return None
    
    def _load_default_model_image(self):
        """デフォルトのモデル画像を読み込んでキャンバスに表示"""
        try:
            # モデルコンボボックスから最初の項目を選択
            if hasattr(self.main_view, 'model_combobox') and self.main_view.model_combobox:
                values = self.main_view.model_combobox['values']
                if values and len(values) > 0:
                    # 最初の項目を選択
                    first_model = values[0]
                    self.main_view.model_var.set(first_model)
                    
                    # モデル選択イベントを手動で呼び出し
                    self.on_model_selected()
                    print(f"デフォルトモデルを選択しました: {first_model}")
                else:
                    print("選択可能なモデルがありません")
            else:
                print("モデルコンボボックスが初期化されていません")
                
        except Exception as e:
            print(f"デフォルトモデル画像読み込みエラー: {e}")
    
    def _get_next_sequential_number(self, directory: str) -> int:
        """指定されたディレクトリ内の連番ファイル名の次の番号を取得"""
        if not directory or not os.path.exists(directory):
            return 1
        
        try:
            json_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json') and os.path.isfile(os.path.join(directory, filename)):
                    name_without_ext = os.path.splitext(filename)[0]
                    if name_without_ext.isdigit() and len(name_without_ext) == 4:
                        json_files.append(int(name_without_ext))
            
            return max(json_files) + 1 if json_files else 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def _load_defects_from_file(self) -> list:
        """外部ファイルから不良名リストを読み込み"""
        try:
            # 実行ファイルと同じディレクトリのdefects.txtを読み込み
            import sys
            if getattr(sys, 'frozen', False):
                executable_dir = os.path.dirname(sys.executable)
            else:
                executable_dir = os.path.dirname(os.path.abspath(__file__))
            
            defects_file = os.path.join(executable_dir, "defects.txt")
            
            if os.path.exists(defects_file):
                with open(defects_file, 'r', encoding='utf-8') as f:
                    defects = [line.strip() for line in f.readlines() if line.strip()]
                    return defects if defects else ["ズレ"]
            else:
                return ["ズレ", "裏", "飛び"]
                
        except Exception as e:
            print(f"不良名ファイル読み込みエラー: {e}")
            return ["ズレ", "裏", "飛び"]
    
    # イベントハンドラー
    def select_date(self):
        """日付選択ダイアログを表示"""
        dialog_class = self.dialogs['DateSelectDialog']
        dialog = dialog_class(self.root, self.main_view.selected_date)
        result = dialog.show()
        
        if not result['cancelled'] and result['date']:
            self.main_view.update_date_label(result['date'])
            self._setup_save_name_entry()
    
    def on_mode_change(self):
        """モード変更時の処理"""
        self.current_mode = self.main_view.mode_var.get()
        print(f"[モード変更] {self.current_mode}モードに切り替えました")
        
        # キャンバスのイベントバインドを更新
        if self.canvas_view:
            self.canvas_view.bind_events(self.current_mode)
        
        # サイドバーを再作成（モードに応じたスタイルで）
        self._recreate_sidebar()
        
        # モードに応じた処理
        if self.current_mode == "閲覧":
            self._handle_view_mode_activation()
        else:
            self._handle_edit_mode_activation()
    
    def _recreate_sidebar(self):
        """サイドバーを再作成"""
        # 現在のフォームデータを保存
        current_data = self.sidebar_view.get_form_data() if self.sidebar_view else {}
        current_worker = self.worker_model.get_current_worker_name()
        
        # サイドバーフレームをクリア
        sidebar_frame = self.main_view.get_sidebar_frame()
        for widget in sidebar_frame.winfo_children():
            widget.destroy()
        
        # 新しいサイドバーを作成
        self.sidebar_view = SidebarView(sidebar_frame, self.current_mode)
        self._setup_sidebar_callbacks()
        
        # データを復元
        self.sidebar_view.set_form_data(current_data)
        self.sidebar_view.update_worker_label(current_worker)
        self.sidebar_view.update_lot_number_label(self.current_lot_number)
    
    def _handle_view_mode_activation(self):
        """閲覧モード開始時の処理"""
        coordinates = self.coordinate_model.get_coordinates()
        if coordinates:
            # 座標概要情報を表示
            summary = self.coordinate_model.get_coordinate_summary()
            print(f"[閲覧モード] 座標の概要: 総数{summary['total_count']}個、修理済み{summary['repaired_count']}個")
            
            # 最初の座標を選択
            self.coordinate_model.set_current_coordinate(0)
            detail = self.coordinate_model.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.set_form_data(detail)
                self.sidebar_view.update_sidebar_title(f"座標 1 の詳細情報")
            
            if self.canvas_view:
                self.canvas_view.highlight_coordinate(0, coordinates)
    
    def _handle_edit_mode_activation(self):
        """編集モード開始時の処理"""
        if self.canvas_view:
            self.canvas_view.clear_highlight()
        self.sidebar_view.update_sidebar_title("不良詳細情報")
    
    def open_settings(self):
        """設定ダイアログを開く"""
        current_settings = self.settings_model.get_all_settings()
        dialog_class = self.dialogs['SettingsDialog']
        dialog = dialog_class(self.root, current_settings, self._on_settings_updated)
        dialog.show()
    
    def _on_settings_updated(self, new_settings: dict):
        """設定が更新された時の処理"""
        self.settings_model.update_settings(new_settings)
        self.settings_model.save_settings()
        self._update_model_list()
        print("設定が更新されました")
    
    def undo_action(self):
        """元に戻す操作"""
        if self.coordinate_model.undo():
            coordinates = self.coordinate_model.get_coordinates()
            if self.canvas_view:
                self.canvas_view.redraw_all_markers(coordinates)
            print("操作を元に戻しました")
    
    def redo_action(self):
        """やり直し操作"""
        if self.coordinate_model.redo():
            coordinates = self.coordinate_model.get_coordinates()
            if self.canvas_view:
                self.canvas_view.redraw_all_markers(coordinates)
            print("操作をやり直しました")
    
    def on_model_selected(self, event=None):
        """モデル選択時の処理"""
        form_data = self.main_view.get_form_data()
        model_name = form_data.get('model', '')
        print(f"モデル選択: {model_name}")
        
        # 画像を読み込んで表示
        image_path = self.image_model.find_image_path_by_name(model_name)
        if image_path:
            print(f"画像パスを発見: {image_path}")
            tk_image = self.image_model.load_image(
                image_path, 
                self.main_view.CANVAS_WIDTH, 
                self.main_view.CANVAS_HEIGHT
            )
            
            if tk_image and self.canvas_view:
                image_info = self.image_model.get_image_info()
                display_pos = self.image_model.calculate_display_position(
                    self.main_view.CANVAS_WIDTH, 
                    self.main_view.CANVAS_HEIGHT
                )
                
                self.canvas_view.display_image(tk_image, display_pos['x'], display_pos['y'])
                print(f"画像を表示しました: {model_name}")
                
                # 座標モデルに画像情報を設定
                self.coordinate_model.set_image_info(image_info)
                
                # 既存の座標をクリア
                self.coordinate_model.clear_coordinates()
                if self.canvas_view:
                    self.canvas_view.clear_markers()
            else:
                print(f"画像の読み込みまたは表示に失敗しました: {model_name}")
        else:
            print(f"画像パスが見つかりません: {model_name}")
        
        # 保存名エントリを更新
        self._setup_save_name_entry()
    
    def on_lot_number_enter(self, event=None):
        """ロット番号入力でEnterキーが押された時の処理"""
        self.on_save_button_click()
    
    def on_save_button_click(self):
        """保存ボタンクリック時の処理"""
        import re
        
        # 作業者が設定されているかチェック
        if not self.worker_model.get_current_worker_no():
            tk.messagebox.showerror("エラー", "作業者が設定されていません。")
            return
        
        # ロット番号を取得
        lot_number = self.main_view.get_current_lot_number()
        if not lot_number:
            self._show_lot_number_error("ロット番号を入力してください。")
            return
        
        # ロット番号の形式をチェック
        lot_pattern = r'^\d{7}-10$|^\d{7}-20$'
        if not re.match(lot_pattern, lot_number):
            self._show_lot_number_error("ロット番号の形式が正しくありません。\n形式: 1234567-10 または 1234567-20")
            return
        
        # ロット番号を保存
        self.current_lot_number = lot_number
        self.sidebar_view.update_lot_number_label(lot_number)
        self.main_view.clear_lot_number_input()
        
        print(f"ロット番号を保存しました: {lot_number}")
    
    def _show_lot_number_error(self, message: str):
        """ロット番号エラーダイアログを表示"""
        tk.messagebox.showerror("ロット番号エラー", message)
    
    def search_coordinates(self):
        """座標検索機能（閲覧モード用）"""
        print("検索機能は今後実装予定です。")
    
    # キャンバスイベントハンドラー
    def on_canvas_click(self, event):
        """編集モード：キャンバスクリック時の処理"""
        x, y = event.x, event.y
        
        # 座標を追加
        index = self.coordinate_model.add_coordinate(x, y)
        
        # マーカーを描画
        if self.canvas_view:
            coordinates = self.coordinate_model.get_coordinates()
            self.canvas_view.redraw_all_markers(coordinates)
        
        # 新しい座標を選択状態にする
        self.coordinate_model.set_current_coordinate(index)
        
        # フォームをクリアして新しい座標用に設定
        self.sidebar_view.clear_form()
        self.sidebar_view.set_form_data({'item_number': str(index + 1)})
        self.sidebar_view.focus_reference_entry()
        
        print(f"座標を追加しました: ({x}, {y})")
    
    def on_canvas_right_click(self, event):
        """編集モード：右クリック時の処理（既存座標の選択）"""
        x, y = event.x, event.y
        
        # 最も近い座標を検索
        coordinates = self.coordinate_model.get_coordinates()
        selected_index = self.coordinate_model.find_nearest_coordinate(x, y, 20)
        
        if selected_index >= 0:
            # 座標を選択
            self.coordinate_model.set_current_coordinate(selected_index)
            
            # フォームを選択した座標の詳細情報で更新
            detail = self.coordinate_model.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.set_form_data(detail)
            
            print(f"座標 {selected_index + 1} を選択しました")
    
    def on_canvas_view_click(self, event):
        """閲覧モード：キャンバスクリック時の処理"""
        x, y = event.x, event.y
        
        # 最も近い座標を検索
        coordinates = self.coordinate_model.get_coordinates()
        selected_index = self.coordinate_model.find_nearest_coordinate(x, y, 20)
        
        if selected_index >= 0:
            # 座標を選択
            self.coordinate_model.set_current_coordinate(selected_index)
            
            # フォームを選択した座標の詳細情報で更新
            detail = self.coordinate_model.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.set_form_data(detail)
                self.sidebar_view.update_sidebar_title(f"座標 {selected_index + 1} の詳細情報")
            
            # ハイライト表示
            if self.canvas_view:
                self.canvas_view.highlight_coordinate(selected_index, coordinates)
            
            print(f"[閲覧モード] 座標 {selected_index + 1} を選択しました")
        else:
            # 座標が選択されていない場合はフォームをクリア
            self.coordinate_model.set_current_coordinate(-1)
            self.sidebar_view.clear_form()
            if self.canvas_view:
                self.canvas_view.clear_highlight()
            self.sidebar_view.update_sidebar_title("不良詳細情報")
            print("[閲覧モード] 座標の選択を解除しました")
    
    def on_form_data_changed(self):
        """フォームデータが変更された時の処理"""
        # 現在選択中の座標があれば詳細情報を更新
        current_index = self.coordinate_model.get_current_coordinate_index()
        if current_index >= 0:
            detail = self.sidebar_view.get_form_data()
            self.coordinate_model.update_current_coordinate_detail(detail)
            
            # 自動保存処理をここに追加可能
    
    # コールバックハンドラー
    def on_coordinate_added(self, coordinate, index):
        """座標が追加された時のコールバック"""
        pass
    
    def on_coordinate_selected(self, index, coordinate):
        """座標が選択された時のコールバック"""
        pass
    
    def on_coordinates_updated(self, coordinates):
        """座標が更新された時のコールバック"""
        if self.canvas_view:
            self.canvas_view.redraw_all_markers(coordinates)
    
    def on_data_loaded(self, data):
        """データが読み込まれた時のコールバック"""
        pass
    
    def on_data_saved(self, file_path):
        """データが保存された時のコールバック"""
        pass
    
    def on_settings_changed(self, settings):
        """設定が変更された時のコールバック"""
        pass
    
    def run_app(self):
        """アプリケーションを実行"""
        self.root.mainloop()
