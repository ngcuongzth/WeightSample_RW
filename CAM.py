from GUI.Ui_WF_Weight import Ui_MainWindow
from src import (
    Serial_Thread,
    config,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QApplication,
)
from PyQt5.QtGui import QIcon
import  sys
import ast


class MyApplication(QMainWindow):
    def __init__(self):
        self.init_UI()
        self.read_config()

        self.SCALE_THREAD = Serial_Thread(self.PORT_SCALE, self.BAUD_SCALE)
        self.SCALE_THREAD.data_received.connect(self.handle_weight_data)
        self.SCALE_THREAD.start()

        self.uic.combo_mode.currentIndexChanged.connect(self.handle_change_mode)
        self.uic.btn_reweight.clicked.connect(self.handle_reweight_clicked)
        # clear filter

    def init_UI(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        self.setWindowTitle("WEIGHT X17")
        self.setWindowIcon(QIcon(r"./icon/sd.ico"))
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
        self.uic.txt_result.setText("START")

        self.radio_buttons = [
            self.uic.radio_1,
            self.uic.radio_2,
            self.uic.radio_3,
            self.uic.radio_4,
            self.uic.radio_5,
            self.uic.radio_6,
            self.uic.radio_7,
            self.uic.radio_8,
            self.uic.radio_9,
            self.uic.radio_10,
        ]

        for radio in self.radio_buttons:
            radio.clicked.connect(self.handle_check_radio)
        self.show()

        self.sample_inputs = [
            self.uic.sample_1,
            self.uic.sample_2,
            self.uic.sample_3,
            self.uic.sample_4,
            self.uic.sample_5,
            self.uic.sample_6,
            self.uic.sample_7,
            self.uic.sample_8,
            self.uic.sample_9,
            self.uic.sample_10,
        ]


    def read_config(self):
        self.PORT_SCALE =  config.get("SERIAL", "PORT_SCALE")
        self.BAUD_SCALE = config.get("SERIAL", "BAUDRATE_SCALE")
        self.IS_INIT_SAMPLE = config.get("SAMPLE_WEIGHT", "IS_INIT")
        if self.IS_INIT_SAMPLE == "1":
            sample_weight_str = config.get('SAMPLE_WEIGHT', 'SAMPLE_WEIGHT_LIST')
            self.SAMPLE_WEIGHT_LIST = ast.literal_eval(sample_weight_str)
            for input_field, value in zip(self.sample_inputs, self.SAMPLE_WEIGHT_LIST):
                if value == 0:
                    input_field.setPlainText("")
                else:
                    input_field.setPlainText(str(value))
            if self.is_enough_10_values():
                self.calc_ave_min_max_sample()
            else:
                self.uic.txt_minValue.setPlainText("")
                self.uic.txt_maxValue.setPlainText("")


    def handle_change_mode(self):
        # sự kiện thay đổi chế độ
        if self.uic.combo_mode.currentIndex() == 1:
            for radio in self.radio_buttons:
                radio.setChecked(False)
                radio.setDisabled(True)
        elif self.uic.combo_mode.currentIndex() == 0:
            for radio in self.radio_buttons:
                radio.setChecked(False)
                radio.setEnabled(True)
        

    def handle_weight_data(self, data):
        # hàm xử lý nhận dữ liệu cân
        if len(data) > 8:
            data = data.decode().strip()
            if data.find("GS") != -1:
                data = data[1 : (len(data) - 2)].strip()
                if data != "0.00":
                    self.uic.txt_currentValue.setText(data)

                    # kiểm tra chế độ cân
                    index_mode = self.uic.combo_mode.currentIndex()
                    
                    # cân hàng mẫu
                    if index_mode == 0:
                        is_exist_sample_value = self.is_enough_10_values()
                        if is_exist_sample_value == False:
                            # list chưa có giá trị 
                            list_empty = self.find_empty_sample()
                            if len(list_empty) > 0:
                                index_cursor = list_empty[0]
                                self.handle_check_radio()
                                self.radio_buttons[index_cursor].setChecked(True)
                                checked_radio_index = self.find_checked_radio_index()
                                if len(checked_radio_index) > 0:
                                    index = checked_radio_index[0]
                                    self.sample_inputs[index].setPlainText(data)
                                
                                self.uic.txt_minValue.setPlainText('')
                                self.uic.txt_maxValue.setPlainText('')
                            
                            else:
                                # đủ giá trị rồi thì sẽ bỏ check tất cả radio
                                self.handle_check_radio()

                            # tính toán min, max
                            is_sample_inputs_filled = self.is_enough_10_values()
                            if is_sample_inputs_filled:
                                self.calc_ave_min_max_sample()

                        else: 
                            checked_radio_index = self.find_checked_radio_index()
                            if len(checked_radio_index) > 0:
                                index = checked_radio_index[0]
                                self.sample_inputs[index].setPlainText(data)

                            is_sample_inputs_filled = self.is_enough_10_values()
                            if is_sample_inputs_filled:
                                self.calc_ave_min_max_sample()
                    
                    # cân trọng lượng
                    elif index_mode == 1:
                        # lấy ra giá trị min và max của hàng mẫu 
                        value_min_weight = self.uic.txt_minValue.toPlainText().strip()
                        value_max_weight = self.uic.txt_maxValue.toPlainText().strip()

                        if self.is_number(value_min_weight) and self.is_number(value_max_weight):
                            # so sánh giá trị cân hiện tại với giá trị min max 
                            current_value = self.uic.txt_currentValue.toPlainText().strip()
                            value_compare = float(value_min_weight) <= float(current_value) <= float(value_max_weight)
                            if value_compare:
                                # self.uic.txt_result.setText("PASS")
                                self.set_ui_state("PASS")
                                value_qty = int(self.uic.txt_quantity.text().strip())
                                self.uic.txt_quantity.setText(str(value_qty + 1))
                            else:
                                self.set_ui_state("FAIL")
                        else:
                            print("Something went wrong")

                    

    def find_checked_radio_index(self):
        # tìm kiểm và trả về mảng chứa các radio đang được check
        checked_indexes = [
            index for index, radio in enumerate(self.radio_buttons) if radio.isChecked()
        ]
        return checked_indexes

    def is_enough_10_values(self):
        # 10 giá trị sample đã có giá trị hay chưa 
        all_filled = all(
            input_field.toPlainText().strip() != ""
            for input_field in self.sample_inputs
        )
        if all_filled:
            return True
        return False

    def handle_check_radio(self):
        clicked_radio = self.sender()
        for radio in self.radio_buttons:
            if radio != clicked_radio:
                radio.setChecked(False)

    def calc_ave_min_max_sample(self):
        weight_list = [
            float(input_field.toPlainText().strip())
            for input_field in self.sample_inputs
            if input_field.toPlainText().strip()
        ]
        max_value = max(weight_list)
        min_value = min(weight_list)
        ave_value = sum(weight_list) / len(weight_list)
        
        min_10_samples = round((ave_value - ave_value * (max_value - min_value) / ave_value), 3)
        max_10_samples = round((ave_value + ave_value * (max_value - min_value) / ave_value), 3)

        self.uic.txt_minValue.setPlainText(str(min_10_samples))
        self.uic.txt_maxValue.setPlainText(str(max_10_samples))

    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def find_empty_sample(self):
        """@return : list data"""
        empty_list = []
        for index, input_field in enumerate(self.sample_inputs):
            if input_field.toPlainText().strip() == "":  
                empty_list.append(index)
        return empty_list

    def set_ui_state(self, type:str):
        if type == "PASS":
            self.uic.txt_result.setText("PASS")
            self.uic.txt_result.setStyleSheet("color: #fff; background-color: #34eb5e;")
        elif type == "FAIL":
            self.uic.txt_result.setText("NG: Weight Error")
            self.uic.txt_result.setStyleSheet("color: #fff; background-color: #d9450b")
        else:
            self.uic.txt_result.setText(type)
            self.uic.txt_result.setStyleSheet("color: #000; background-color: #fff")

    def handle_reweight_clicked(self):
        self.set_ui_state(type="RE-WEIGHT SAMPLE")
        self.uic.combo_mode.setCurrentIndex(0)
        self.uic.txt_minValue.setText("")
        self.uic.txt_maxValue.setText("")
        self.uic.txt_currentValue.setText("")
        for sample_input in self.sample_inputs:
            sample_input.setPlainText("")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MyApplication()
    sys.exit(app.exec_())
