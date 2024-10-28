import datetime
import configparser
import os
import time
import csv
from PIL import Image, ImageDraw, ImageFont


config = configparser.ConfigParser()
config.read("./configs/configApp.ini")


config_update = configparser.ConfigParser()
config_update.read("./configs/config.ini")


def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def format_current_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H-%M-%S:%f")[:-3]
    return formatted_time


def create_daily_folders():
    path = config["PATH"]["IMAGE_DIR"]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(path, current_date)
    os.makedirs(folder_path, exist_ok=True)
    create_file_csv()


def create_file_csv():
    path = config["PATH"]["IMAGE_DIR"]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(path, current_date)
    filename = f"{folder_path}/{current_date}.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["NUMBER_ORDER", "VALUE", "CREATE_TIME"])


def insert_file_csv(data: list):
    path = config["PATH"]["IMAGE_DIR"]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(path, current_date)
    filename = f"{folder_path}/{current_date}.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            if not file_exists:
                writer.writerow(["NUMBER_ORDER", "VALUE", "CREATE_TIME"])
        else:
            writer.writerow(data)


# def handle_remove_old_folders():
#     folder_to_keep = int(config["PATH"]["FOLDER_TO_KEEP"])
#     path = config["PATH"]["IMAGE_NG_DIR"]
#     subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
#     subfolders.sort()
#     if len(subfolders) > folder_to_keep:
#         folders_to_delete = subfolders[: len(subfolders) - folder_to_keep]
#         for folder_to_delete in folders_to_delete:
#             try:
#                 shutil.rmtree(folder_to_delete)
#                 print(f"Removed old folder: {folder_to_delete}")
#             except Exception as e:
#                 print(f"Remove error '{folder_to_delete}': {e}")


# def setup_logger():
#     path_dir_log = "./logs/"
#     time_day = time.strftime("%Y_%m_%d")
#     logger = logging.getLogger("MyLogger")
#     logger.setLevel(logging.DEBUG)
#     formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#     file_handler = logging.FileHandler(f"{path_dir_log}{time_day}.log")
#     file_handler.setFormatter(formatter)
#     file_handler.setLevel(logging.DEBUG)
#     logger.addHandler(file_handler)
#     return logger


# running when start program

# handle_remove_old_folders()
create_daily_folders()
# logger = setup_logger()
path_logEvent = "./logs/"


def LogEvent(data, type, logtype):
    try:
        data = str(data.encode("utf-8"))
        if type == "DT":
            pathLog = path_logEvent + "LogData_" + time.strftime("%Y%m%d") + ".log"
        elif type == "IMG":
            pathLog = path_logEvent + "LogImage_" + time.strftime("%Y%m%d") + ".log"
        else:
            pathLog = path_logEvent + "LogDB_" + time.strftime("%Y%m%d") + ".log"
        with open(pathLog, "a") as file:
            if logtype == "info":
                file.write(time.strftime("%H:%M:%S") + " - INFO - " + data + "\n")
            if logtype == "E":
                file.write(time.strftime("%H:%M:%S") + " - ERROR - " + data + "\n")
            if logtype == "war":
                file.write(time.strftime("%H:%M:%S") + " - WARNING - " + data + "\n")
    except Exception as e:
        print(
            "-->>>" + time.strftime("%Y%m%d_%H_%M_%S") + ": ERROR LogEvent: ",
            e,
            "--Data: ",
            data,
        )


def write_text_on_image(image_path, text, font_path="arial.ttf", font_size=48):
    # Mở ảnh
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Chọn font và kích thước
    font = ImageFont.truetype(font_path, font_size)  # Sử dụng font từ file .ttf

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]  # Width = right - left
    text_height = bbox[3] - bbox[1]  # Height = bottom - top
    position = (image.width - text_width - 10, image.height - text_height - 10)

    # Vẽ chữ lên ảnh
    draw.text(position, text, fill="white", font=font)

    # Lưu ảnh
    image.save(image_path)


def write_text_on_image(image_path, text, font_size=18):
    font_path = "arial.ttf"
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = (image.width - text_width - 20, image.height - text_height - 20)

    draw.text(position, text, fill="white", font=font)
    image.save(image_path)
