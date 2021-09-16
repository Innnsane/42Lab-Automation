import re
import ujson
from lua2json import recognize

NAME_PATH = "./res/avg_name.txt"
TEXT_PATH = "./res/local_text.txt"
CONFIG_PATH = "./avg_config.json"
LANG_PATH = "./avg_lang.json"
OUTPUT_PATH = "./output/output.txt"


with open(NAME_PATH, "r", encoding="utf-8") as f_name:
    HERO_NAME = ujson.load(f_name)
    f_name.close()

with open(TEXT_PATH, "r", encoding="utf-8") as f_text:
    TEXT = ujson.load(f_text)
    f_text.close()


def create_mw(config, lang):
    mw_text = ""

    # 该文件调用图片的预处理
    img_dict = {"background": {}, "character": {}}
    for img in config[0]["images"]:
        if int(img["imgType"]) == 3:
            img_dict["character"][str(img["imgId"])] = img
        else:
            img_dict["background"][str(img["imgId"])] = img

    # 上次图片配置
    last_img_path = ""

    # 单元化
    for scene in config:
        print(scene)

        # 背景CG
        if "imgTween" in scene.keys():
            for img in scene["imgTween"]:
                if str(img["imgId"]) in img_dict["background"].keys():
                    mw_text += "{{剧情背景展示|" + img_dict["background"][str(img["imgId"])]["imgPath"].split("/")[-1] + "}}\n"

        if "contentType" not in scene.keys():
            continue

        # 对话框类型 2/3/4
        this_scene_text = "{{剧情对话框|类型=" + str(scene["contentType"])

        # 讲话者 2：旁白 3:人物对话框 4:沉底对话框
        if int(scene["contentType"]) == 3:
            for hero in HERO_NAME:
                if int(hero["id"]) == int(scene['speakerHeroId']):
                    if type(hero["name"]) == int:
                        speakerIndex = f"[{str(hero['name'])}]"
                        this_scene_text += f"|名称={TEXT[speakerIndex]}"
                    elif type(hero["name"]) == str:
                        this_scene_text += f"|名称={hero['name']}"
                    break

        elif int(scene["contentType"]) == 4:
            speakerName = f"[{str(scene['speakerName'])}]"
            this_scene_text += f"|名称={lang[speakerName]}"

        # 头像 源自立绘 仅contentType:3时调用
        # speakerHeroPosId 1:Left 2:Center 3:Right
        if "imgTween" in scene.keys() and int(scene["contentType"]) == 3:
            img_control = {}
            for img in scene["imgTween"]:
                if str(img["imgId"]) not in img_control.keys():
                    img_control[str(img["imgId"])] = {
                        "isDark": False,
                        "alpha": "1",
                        "imgPath": img_dict["character"][str(img["imgId"])]["imgPath"].split("/")[-1]}
                if "alpha" in img.keys():
                    img_control[str(img["imgId"])]["alpha"] = img["alpha"]

                if "isDark" in img.keys() and img["isDark"] is False:
                    img_control[str(img["imgId"])]["isDark"] = False
                elif "isDark" in img.keys() and img["isDark"] is True:
                    img_control[str(img["imgId"])]["isDark"] = True

            for img_2 in img_control.keys():
                if img_control[img_2]["isDark"] is False and str(img_control[img_2]["alpha"]) != "0":
                    this_scene_text += "|头像=" + img_control[img_2]["imgPath"]
                    last_img_path = img_control[img_2]["imgPath"]

        # 当立绘不变时采用上次的剧情立绘作为头像
        elif "imgTween" not in scene.keys() and int(scene["contentType"]) == 3:
            this_scene_text += "|头像=" + last_img_path

        # 差分
        if "heroFace" in scene.keys():
            this_scene_text += "|差分=" + scene["heroFace"]

        # 对话内容 包含颜色代码处理
        content = lang[f"[{str(scene['content'])}]"]
        content = re.sub(f"</[Cc]olor>", "}}", content)

        result = re.findall(r'<[Cc]olor=#(?P<color>[0-9a-fA-F]{8})>', content)
        for color in result:
            content = re.sub(f"<[Cc]olor=#{color}>", "{{Color|#" + color + "|", content)

        this_scene_text += f"|文本={content}" + "}}\n"

        print(this_scene_text)
        mw_text += this_scene_text

    return mw_text


def get():
    with open(LANG_PATH, "r", encoding="utf-8") as f_lang:
        lang = ujson.load(f_lang)
        f_lang.close()


    with open(CONFIG_PATH, "r", encoding="utf-8") as f_config:
        config = ujson.load(f_config)
        f_config.close()

    mw_text = create_mw(config, lang)
    print(mw_text)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f_output:
        f_output.write(mw_text)

    return


def main():
    while True:
        mode = input("-- 请选择需要执行的程序 【1：源文件处理】【2：WIKI剧情文本创建】【3：退出】")

        if mode == "1":
            recognize()
        elif mode == "2":
            get()
        elif mode == "3":
            break
        else:
            print("-- 无法识别")
            main()


if __name__ == '__main__':
    main()

