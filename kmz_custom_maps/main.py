import os
from zipfile import ZipFile
from PIL import Image
import pathlib
from lxml import html
import numpy as np
import zipfile
import shutil
import copy

MAX_FILE_SIZE = 3
EXPAND = 1


MAX_PIXELS = 1024

def calc_map_grid(original_image_size: tuple[int, int], max_pixels:int):
    orig_height = original_image_size[1]
    orig_width = original_image_size[0]
    
    r = int(np.ceil(orig_height / max_pixels))
    c = int(np.ceil(orig_width / max_pixels))

    return r * c, c, r


class KML_doc():
    def __init__(self, kml_string):
        doc = html.fromstring(kml_string)
        name = doc.cssselect("name")[0]
        ground_overlay = doc.cssselect('GroundOverlay')[0]
        href = ground_overlay.cssselect("Icon href")[0]
        latlonbox = ground_overlay.cssselect("LatLonBox")[0]
        north = latlonbox.cssselect("north")[0]
        south = latlonbox.cssselect("south")[0]
        east = latlonbox.cssselect("east")[0]
        west = latlonbox.cssselect("west")[0]

        self.ground_overlay = ground_overlay
        self.name = name
        self.doc = doc
        self.img_name = href
        self.north = north
        self.south = south
        self.west = west
        self.east = east

        self.folder = None

    def get_latlonbox(self) -> dict:
        latlonbox = {
            "north": float(self.north.text),
             "south": float(self.south.text),
             "west": float(self.west.text),
             "east": float(self.east.text),
        }

        return latlonbox

    def get_name(self) -> str:
        return self.name.text

    def update_name(self, name: str):
        self.name.text = name

    def get_image_name(self) -> str:
        return self.img_name.text

    def update_latlonbox(self, latlonbox: dict):
        self.north.text = str(latlonbox["north"])
        self.south.text = str(latlonbox["south"])
        self.east.text = str(latlonbox["east"])
        self.west.text = str(latlonbox["west"])

    def update_img_name(self, img_name: str):
        self.img_name.text = img_name

    def create_folder(self):
        # <Folder>
        # 	<name>blah</name>
        # 	<open>1</open>
        self.ground_overlay_copy = copy.deepcopy(self.ground_overlay)
        self.doc.remove(self.ground_overlay)
        self.doc.append(html.Element("folder"))
        self.folder = self.doc.cssselect("folder")[0]
        self.folder.append(html.Element("name"))
        self.folder_name = self.folder.cssselect("name")[0]
        self.folder_name.text = self.name.text + "_folder"
        self.folder.append(html.Element("open"))
        self.folder_open = self.folder.cssselect("open")[0]
        self.folder_open.text = str(1)


    def add_ground_overlay(self, name: str, image_name: str, latlonbox: dict, index: int=1):
        assert self.folder is not None, "create folder first"
        new_ground_overlay = copy.deepcopy(self.ground_overlay_copy)
        href = new_ground_overlay.cssselect("Icon href")[0]
        latlonbox_el = new_ground_overlay.cssselect("LatLonBox")[0]
        north = latlonbox_el.cssselect("north")[0]
        south = latlonbox_el.cssselect("south")[0]
        east = latlonbox_el.cssselect("east")[0]
        west = latlonbox_el.cssselect("west")[0]

        name_el = new_ground_overlay.cssselect("name")[0]
        name_el.text = name

        north.text = str(latlonbox["north"])
        south.text = str(latlonbox["south"])
        east.text = str(latlonbox["east"])
        west.text = str(latlonbox["west"])

        href.text = image_name

        # self.ground_overlay_list.append(new_ground_overlay)
        self.folder.append(new_ground_overlay)


    def to_kml_string(self):
        kml_str = html.tostring(self.doc).replace(b"groundoverlay",b"GroundOverlay")
        kml_str = kml_str.replace(b"draworder", b"drawOrder")
        kml_str = kml_str.replace(b"viewboundscale", b"viewBoundScale")
        kml_str = kml_str.replace(b"icon", b"Icon")
        kml_str = kml_str.replace(b"latlonbox", b"LatLonBox")
        kml_str = kml_str.replace(b"folder", b"Folder")
        # kml_str = kml_str.replace(b"</Folder>", b"</Folder>\n")
        kml_str = kml_str.replace(b"Folder>", b"Folder>\n")
        kml_str = kml_str.replace(b"Folder</name>", b"Folder</name>\n")
        kml_str = kml_str.replace(b"</open>", b"</open>\n")


        return kml_str

    def print(self):
        print(self.to_kml_string().decode("utf-8"))


def read_kmz(file_path: str)-> (str, Image):
    kmz = ZipFile(file_path, 'r')
    inflist = kmz.infolist()

    for inf in inflist:
        if pathlib.Path(inf.filename).suffix == ".kml":
            kml_data = kmz.open(inf).read()
        if pathlib.Path(inf.filename).suffix in [".jpg", ".jpeg", ".JPG"]:
            img = Image.open(kmz.open(inf))


    kmz.close()
    return kml_data, img, kmz.compression, kmz.compresslevel


if __name__=="__main__":
    combine = True

    file_path = "test_data/Bellingen-nsw-six-maps.kmz"
    # file_path = "test_data/test.kmz"
    kml_data, img, compression, compresslevel = read_kmz(file_path)

    kml_doc = KML_doc(kml_string=kml_data)

    orig_latlonbox = kml_doc.get_latlonbox()
    orig_image_name = kml_doc.get_image_name()
    orig_name = kml_doc.get_name()


    # kml_doc.print()

    orig_img_size = img.size
    orig_img_height = orig_img_size[1]
    orig_img_width = orig_img_size[0]

    num_maps, map_cols, map_rows = calc_map_grid(orig_img_size, max_pixels=MAX_PIXELS)

    map_height = int(np.ceil(orig_img_height / map_rows))
    map_width = int(np.ceil(orig_img_width / map_cols))

    img_heights = []
    for r in range(map_rows):
        img_heights.append(int(np.ceil(np.minimum(orig_img_height / map_rows, orig_img_height - np.sum(img_heights)))))

    img_widths = []
    for c in range(map_cols):
        img_widths.append(int(np.ceil(np.minimum(orig_img_width / map_cols, orig_img_width - np.sum(img_widths)))))

    lat_per_pixel = (orig_latlonbox["north"] - orig_latlonbox["south"]) / orig_img_height
    lon_per_pixel = (orig_latlonbox["east"] - orig_latlonbox["west"]) / orig_img_width


    maps = []
    for i in range(num_maps):
        r = i //map_cols
        c = i % map_cols

        # image top left is (0, 0)
        left = int(np.sum(img_widths[:c]))
        right = int(np.sum(img_widths[:c+1]))
        top = int(np.sum(img_heights[:r]))
        bottom = int(np.sum(img_heights[:r+1]))

        latlonbox = {
            "north":orig_latlonbox["north"]-lat_per_pixel*np.sum(img_heights[:r]),
            "south":orig_latlonbox["north"]-lat_per_pixel*np.sum(img_heights[:r+1]),
            "west": orig_latlonbox["west"]+lon_per_pixel*np.sum(img_widths[:c]),
            "east":orig_latlonbox["west"]+lon_per_pixel*np.sum(img_widths[:c+1]),
        }
        map = {"image_size":(img_widths[c], img_heights[r]),
               "img_name": str(pathlib.Path(orig_image_name).with_suffix("")) + f"_{i}" + ".jpg",
               "latlonbox":latlonbox,
               "image":img.crop((left, top, right, bottom)),
               "name":orig_name + f"_{i}"
               }
        maps.append(map)

    try:
        os.mkdir("./files")
    except FileExistsError:
        pass

    if combine:
        kml_doc.create_folder()
        for i, map in enumerate(maps):
            # if i==0:
            #     kml_doc.update_latlonbox(map["latlonbox"])
            #     kml_doc.update_img_name(map["img_name"])
            #     kml_doc.update_name(map["name"])
            # else:
            #     kml_doc.add_ground_overlay(map["name"], map["img_name"], map["latlonbox"], index=i)
            kml_doc.add_ground_overlay(map["name"], map["img_name"], map["latlonbox"])


        kml_str = kml_doc.to_kml_string()
        with zipfile.ZipFile(orig_name + ".kmz", 'w',
                             compression=compression,
                             compresslevel=compresslevel) as zf:
            with zf.open("doc.kml", 'w') as f:
                f.write(kml_str)
            for map in maps:
                map["image"].save(map["img_name"], quality=95, optimize=True, progression=False)
                zf.write(map["img_name"], map["img_name"])

    else:
        for map in maps:
            kml_doc.update_latlonbox(map["latlonbox"])
            kml_doc.update_img_name(map["img_name"])
            kml_doc.update_name(map["name"])

            kml_str = kml_doc.to_kml_string()



            with zipfile.ZipFile(map["name"]+".kmz", 'w',
                                 compression=compression,
                                 compresslevel=compresslevel) as zf:
                with zf.open("doc.kml", 'w') as f:
                    f.write(kml_str)

                map["image"].save(map["img_name"], quality=95, optimize=True, progression=False)
                zf.write(map["img_name"], map["img_name"])

        try:
            shutil.rmtree("./files")
        except FileNotFoundError:
            pass
