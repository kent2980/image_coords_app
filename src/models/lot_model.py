class LotModel:
    """ロット情報を管理するモデル"""

    def __init__(self, model:str="", image_path:str="", lot_no:str="", worker_no:str=""):
        self._model = model
        self._image_path = image_path
        self._lot_no = lot_no
        self._worker_no = worker_no

    @property
    def model(self) -> str:
        if self.is_settings_complete():
            return self._model
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def image_path(self) -> str:
        if self.is_settings_complete():
            return self._image_path
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def lot_no(self) -> str:
        if self.is_settings_complete():
            return self._lot_no
        raise ValueError("LotModel Is Settings Not Complete.")

    @property
    def worker_no(self) -> str:
        if self.is_settings_complete():
            return self._worker_no
        raise ValueError("LotModel Is Settings Not Complete.")

    @model.setter
    def model(self, value: str):
        self._model = value

    @image_path.setter
    def image_path(self, value: str):
        self._image_path = value

    @lot_no.setter
    def lot_no(self, value: str):
        self._lot_no = value

    @worker_no.setter
    def worker_no(self, value: str):
        self._worker_no = value

    def set_all_properties(self, model: str, image_path: str, lot_no: str, worker_no: str):
        self._model = model
        self._image_path = image_path
        self._lot_no = lot_no
        self._worker_no = worker_no

    def is_settings_complete(self) -> bool:
        """設定が完了しているかチェック"""
        return all([
            self._model,
            self._image_path,
            self._lot_no,
            self._worker_no
        ])