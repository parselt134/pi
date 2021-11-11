import sys
import platform  # о системе
import psutil  # о компонентах
import time  # для задержки на одну секунду при постройке графика
import speedtest  # для замера скорости интернета
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel


class PI(QMainWindow):
    def __init__(self):
        super(PI, self).__init__()
        uic.loadUi("pi-design.ui", self)
        # Устанавливаем названия вкладок
        self.tabWidget.setTabText(0, "Общие сведения")
        self.tabWidget.setTabText(1, "CPU")
        self.tabWidget.setTabText(2, "Диски")
        self.tabWidget.setTabText(3, "Интернет")
        self.tabWidget.setTabText(4, "RAM")
        # Вызываем метод _set_general, который установит информацию во вкладку "Общие сведения"
        """ Подчёркивание вначале названия метода нужно для обозначения метода защищённым
         т.е. этот метод будет допускаться к обращению только внутри класса и в его
         дочерних классах"""
        self._set_general()

        self._set_cpu()
        self.pushButton_cpu.clicked.connect(self._plot_cpu)
        self.graphic_cpu.showGrid(x=True, y=True, alpha=0.5)

        # Если ОС на компьютере "Linux", то за диск принимаем только корень
        if platform.system() == "Linux":
            discs = ["/"]
        # Иначе, устанавливаем буквы логических дисков (только на Windows)
        else:
            discs = [i.device for i in psutil.disk_partitions()]
        self.discs_cb.addItems(discs)
        self.pushButton_discs.clicked.connect(self._set_discs)

        self.pushButton_ram.clicked.connect(self._plot_ram)
        self.graphic_ram.showGrid(x=True, y=True, alpha=0.5)

        self.pushButton_inet.clicked.connect(self._set_inet)

    def _set_general(self):
        name_os = platform.uname().system
        name_pc = platform.uname().node
        release = platform.uname().release
        """ platform.architecture() вернёт кортеж из двух элементов,
         где первый элемент -- архитектура битов (разрядность)"""
        architecture = platform.architecture()[0]
        self.os_label.setText("Операционная система: " + name_os)
        self.os_version_label.setText("Версия ОС: " + release)
        self.name_label.setText("Имя ПК: " + name_pc)
        self.architecture_label.setText("Разрядность: " + architecture)
        if name_os == "Windows":
            edition = platform.win32_edition()
            self.edition_label.setText("Редакция или дистрибутив: " + edition)
        elif name_os == "Linux":
            edition = open("/etc/lsb-release", mode="rt", encoding="utf-8")\
                .readline().split("=")[-1].replace('"', "")
            self.edition_label.setText("Редакция или дистрибутив: " + edition)
        else:
            self.edition_label.setText(self.edition_label.text() + "Отсутствует ")

    def _set_cpu(self):
        self.name_cpu_label.setText("Реальное имя процессора: " + platform.processor())
        self.logic_proc_label.setText("Количество логических процессоров: " + str(psutil.cpu_count()))
        self.cores_label.setText("Количество ядер: " + str(psutil.cpu_count(logical=False)))

    def _plot_cpu(self):
        self.graphic_cpu.clear()
        range_seconds = self.spinBox_cpu.value()
        self.open_second_form(range_seconds)
        self.graphic_cpu.plot([i for i in range(range_seconds + 1)],
                              [psutil.cpu_percent(interval=1) for _ in range(range_seconds + 1)],
                              pen="g")

    def _set_discs(self):
        disc_usage = psutil.disk_usage(self.discs_cb.currentText())
        capacity = str(int(disc_usage.total/1024/1024/1024))
        used = str(int(disc_usage.used/1024/1024/1024))
        free = str(int(disc_usage.free/1024/1024/1024))
        self.capacity_label.setText("Ёмкость: " + capacity + " ГБ")
        self.used_label.setText("Используется (в ГБ): " + used)
        # disc_usage.percent вернёт процент использования
        self.used_pb.setValue(round(disc_usage.percent))
        self.free_label.setText("Свободно (в ГБ): " + free)
        self.free_pb.setValue(round(100 - disc_usage.percent))

    def _set_inet(self):
        self.open_second_form(30)
        st = speedtest.Speedtest()
        # Скорость загрузки
        download_speed = str(round(st.download()/1024/1024, 2))
        self.download_label.setText("Скорость загрузки: " + download_speed + " Мбит/c")
        # Скорость передачи
        upload_speed = str(round(st.upload()/1024/1024, 2))
        self.upload_label.setText("Скорость передачи: " + upload_speed + " Мбит/с")
        st.get_servers([])
        ping = str(st.results.ping)
        self.ping_label.setText("Пинг: " + ping + " мс")

    def _plot_ram(self):
        self.graphic_ram.clear()
        range_seconds = self.spinBox_ram.value()
        self.open_second_form(range_seconds)
        x = [i for i in range(range_seconds + 1)]
        y = []
        for _ in range(range_seconds + 1):
            y.append(round(psutil.virtual_memory().percent))
            time.sleep(1)
        self.graphic_ram.plot(x, y, pen="g")

    def open_second_form(self, seconds):
        self.second_form = SecondForm(self, seconds)
        self.second_form.show()


class SecondForm(QWidget):
    def __init__(self, *args):
        super(SecondForm, self).__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setFixedSize(450, 50)
        self.setWindowTitle(f"Пожалуйста, подождите {args[-1]} секунд...")
        self.lbl = QLabel("Готово!", self)
        self.lbl.adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PI()
    widget.show()
    sys.exit(app.exec())
