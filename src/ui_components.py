"""
UI Components Module
UIデザインとレイアウトを担当するモジュール - モード別UIコンポーネントのファクトリ
"""

from .ui_components_edit import UIComponentsEdit
from .ui_components_view import UIComponentsView

class UIComponents:
    """UIコンポーネントのファクトリクラス"""
    
    def __init__(self, root, callbacks=None):
        self.root = root
        self.callbacks = callbacks or {}
        
        # 初期モードは編集モードでUIコンポーネントを作成
        self.current_ui = UIComponentsEdit(root, callbacks)
        self.current_mode = "編集"
    
    def switch_mode(self, mode):
        """モードを切り替えてUIコンポーネントを再作成"""
        if mode == self.current_mode:
            return  # 同じモードの場合は何もしない
        
        # 現在のUIの状態を保存
        form_data = self.current_ui.get_form_data()
        current_lot_number = self.current_ui.get_current_lot_number()
        current_worker_no = self.current_ui.get_current_worker()
        
        # 古いUIを削除
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 新しいモードに応じてUIコンポーネントを作成
        if mode == "編集":
            self.current_ui = UIComponentsEdit(self.root, self.callbacks)
        else:  # 閲覧モード
            self.current_ui = UIComponentsView(self.root, self.callbacks)
        
        # UIをセットアップ
        self.current_ui.setup_main_layout()
        self.current_ui.setup_date_display()
        self.current_ui.setup_undo_redo_buttons()
        self.current_ui.setup_settings_button()
        self.current_ui.setup_mode_selection()
        self.current_ui.setup_canvas_top()
        self.current_ui.setup_canvas()
        self.current_ui.setup_sidebar()
        
        # 状態を復元
        self.current_ui.set_form_data(form_data)
        self.current_ui.set_current_lot_number(current_lot_number)
        self.current_ui.set_current_worker(current_worker_no)
        
        # モードを更新
        self.current_mode = mode
        self.current_ui.mode_var.set(mode)
    
    def __getattr__(self, name):
        """属性アクセスを現在のUIコンポーネントに委譲"""
        return getattr(self.current_ui, name)        python main_mvc.py
