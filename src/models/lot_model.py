class LotModel:
    """ロット情報を管理するモデル"""


    def __init__(self, model:str="", image_path:str="", lot_no:str="", worker_no:str=""):
        self.model = model
        self.image_path = image_path
        self.lot_no = lot_no
        self.worker_no = worker_no

    @property
    def model(self) -> str:
        if self.is_settings_complete():
            return self.model
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def image_path(self) -> str:
        if self.is_settings_complete():
            return self.image_path
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def lot_no(self) -> str:
        if self.is_settings_complete():
            return self.lot_no
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def worker_no(self) -> str:
        if self.is_settings_complete():
            return self.worker_no
        raise ValueError("LotModel Is Settings Not Complete.")

    @property.setter
    def model(self, value: str):
        self.model = value

    @property.setter
    def image_path(self, value: str):
        self.image_path = value

    @property.setter
    def lot_no(self, value: str):
        self.lot_no = value

    @property.setter
    def worker_no(self, value: str):
        self.worker_no = value

    def set_all_properties(self, model: str, image_path: str, lot_no: str, worker_no: str):
        self.model = model
        self.image_path = image_path
        self.lot_no = lot_no
        self.worker_no = worker_no

    def is_settings_complete(self) -> bool:
        """設定が完了しているかチェック"""
        return all([
            self.model,
            self.image_path,
            self.lot_no,
            self.worker_no
        ])