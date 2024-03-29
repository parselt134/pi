import sys
import platform  # о системе
import psutil  # о компонентах
import time  # для задержки на одну секунду при постройке графика
import speedtest  # для замера скорости интернета
from pi_design import Ui_MainWindow
from PyQt5.QtCore import Qt  # понадобится для пасхального яйца
from PyQt5.QtGui import QPixmap  # понадобится для пасхального яйца
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel


class PI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(PI, self).__init__()
        self.setupUi(self)
        # Устанавливаем названия вкладок
        self.tabWidget.setTabText(0, "Общие сведения")
        self.tabWidget.setTabText(1, "CPU")
        self.tabWidget.setTabText(2, "Диски")
        self.tabWidget.setTabText(3, "Интернет")
        self.tabWidget.setTabText(4, "RAM")
        # Вызываем метод _set_general, который установит информацию во вкладку "Общие сведения"
        self._set_general()
        # Подчёркивание вначале названия метода нужно для обозначения метода защищённым
        # т.е. этот метод будет допускаться к обращению только внутри класса и в его
        # дочерних классах
        self._set_cpu()
        self.pushButton_cpu.clicked.connect(self._plot_cpu)
        self.graphic_cpu.showGrid(x=True, y=True, alpha=0.5)

        if platform.system() == "Linux":
            discs = ["/"]
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
        # platform.architecture() вернёт кортеж из двух элементов,
        # где первый элемент -- архитектура битов (разрядность)
        architecture = platform.architecture()[0]
        self.os_label.setText("Операционная система: " + name_os)
        self.os_version_label.setText("Версия ОС: " + release)
        self.name_label.setText("Имя ПК: " + name_pc)
        self.architecture_label.setText("Разрядность: " + architecture)
        if name_os == "Windows":
            edition = platform.win32_edition()
            self.edition_label.setText("Редакция или дистрибутив: " + edition)
        elif name_os == "Linux":
            # К сожалению, метод platform.linux_distribution() устарел и
            # был удалён в Python 3.8 (он определял дистрибутив Linux)

            # Для того, чтобы определить дистрибутив,
            # будет в папке etc, содержащая файлы настроек,
            # читаться файл lsb-release, имеющий 4 строки,
            # где 1-ая -- название дистрибутива
            # (строка вида DISTRIB_ID="<название дистрибутива>").

            # Открываем файл lsb-release
            # Берём 1-ую строку, используя метод readline()
            # Делим её по символу "=" на две части
            # Берём последнюю и удаляем парные кавычки
            with open("/etc/lsb-release", mode="rt", encoding="utf-8") as f:
                edition = f.readline().split("=")[-1].replace('"', "")
            self.edition_label.setText("Редакция или дистрибутив: " + edition)
        else:
            self.edition_label.setText("Редакция или дистрибутив: " + "Отсутствует")

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
        try:
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
        # OSError -- исключение, связанное с системой
        except OSError:
            self.capacity_label.setText("Невозможно определить свойства диска")
            self.used_label.setText("")
            self.used_pb.setValue(round(0))
            self.free_label.setText("")
            self.free_pb.setValue(round(0))

    def _set_inet(self):
        try:
            st = speedtest.Speedtest()
            self.open_second_form(30)
            # Скорость загрузки
            download_speed = str(round(st.download()/1024/1024, 2))
            self.download_label.setText("Скорость загрузки: " + download_speed + " Мбит/c")
            # Скорость передачи
            upload_speed = str(round(st.upload()/1024/1024, 2))
            self.upload_label.setText("Скорость передачи: " + upload_speed + " Мбит/с")
            st.get_servers([])
            ping = str(st.results.ping)
            self.ping_label.setText("Пинг: " + ping + " мс")
        # SpeedtestException -- общее исключение библиотеки speedtest
        except speedtest.SpeedtestException:
            self.download_label.setText("Проблемы с подключением")
            self.upload_label.setText("")
            self.ping_label.setText("")

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

    def keyPressEvent(self, event):
        if int(event.modifiers()) == Qt.ShiftModifier:
            if event.key() == Qt.Key_S:
                self.easter_egg = EasterEgg()
                self.easter_egg.show()


class EasterEgg(QWidget):
    def __init__(self):
        super(EasterEgg, self).__init__()
        self.initUi()

    def initUi(self):
        self.setFixedSize(370, 370)
        self.setWindowTitle("Как ты здесь оказался?")

        self.pixmax = QPixmap("./pic/easter_eggs.png")
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.setPixmap(self.pixmax)


class SecondForm(QWidget):
    def __init__(self, *args):
        super(SecondForm, self).__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setFixedSize(450, 50)
        self.setWindowTitle(f"Пожалуйста, подождите {args[-1]} секунд...")
        self.lbl = QLabel("Готово!", self)
        self.lbl.adjustSize()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PI()
    widget.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
