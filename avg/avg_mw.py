import os
import re
import ujson
from lua2json import recognize_all
from lua2json import check

NAME_PATH = "./res/avg_name.txt"
TEXT_PATH = "./res/local_text.txt"

LUA_PATH = "./a_lua"
JSON_PATH = "./b_json"
WIKI_PATH = "./c_wiki"


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
    if "images" in config['[1]'].keys():
        for img in config['[1]']["images"]:
            if int(img["imgType"]) == 3:
                img_dict["character"][str(img["imgId"])] = img
            else:
                img_dict["background"][str(img["imgId"])] = img

    # 上次图片配置
    last_img_path = ""

    # 单元化
    for scene in config:
        # 诡异的没加大括号
        if scene.find("[") == -1:
            continue

        # 背景CG
        if "imgTween" in config[scene].keys():
            for img in config[scene]["imgTween"]:
                if str(img["imgId"]) in img_dict["background"].keys():
                    mw_text += "{{剧情背景展示|" + img_dict["background"][str(img["imgId"])]["imgPath"].split("/")[-1] + "}}\n"

        if "contentType" not in config[scene].keys():
            continue

        # 对话框类型 2/3/4
        this_scene_text = "{{剧情对话框|类型=" + str(config[scene]["contentType"])

        # 讲话者 2：旁白 3:人物对话框 4:沉底对话框
        if int(config[scene]["contentType"]) == 3:
            for hero in HERO_NAME:
                if int(hero["id"]) == int(config[scene]['speakerHeroId']):
                    if "name" not in hero.keys():
                        this_scene_text += f"|名称= "
                    elif type(hero["name"]) == int:
                        speakerIndex = f"[{str(hero['name'])}]"
                        this_scene_text += f"|名称={TEXT[speakerIndex]}"
                    elif type(hero["name"]) == str:
                        this_scene_text += f"|名称={hero['name']}"
                    break

        elif int(config[scene]["contentType"]) == 4:
            speakerName = f"[{str(config[scene]['speakerName'])}]"
            this_scene_text += f"|名称={lang[speakerName]}"

        # 头像 源自立绘 仅contentType:3时调用
        # speakerHeroPosId 1:Left 2:Center 3:Right
        if "imgTween" in config[scene].keys() and int(config[scene]["contentType"]) == 3:
            img_control = {}
            for img in config[scene]["imgTween"]:
                # 仅处理人物立绘 若为背景CG则 continue
                if str(img["imgId"]) not in img_dict["character"].keys():
                    continue

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
        elif "imgTween" not in config[scene].keys() and int(config[scene]["contentType"]) == 3:
            this_scene_text += "|头像=" + last_img_path

        # 差分
        if "heroFace" in config[scene].keys():
            this_scene_text += "|差分=" + str(config[scene]["heroFace"][0]["faceId"])

        # 对话内容 包含颜色代码处理
        content = lang[f"[{str(config[scene]['content'])}]"]
        content = re.sub(f"</[Cc]olor>", "}}", content)

        result = re.findall(r'<[Cc]olor=#(?P<color>[0-9a-fA-F]{8})>', content)
        for color in result:
            content = re.sub(f"<[Cc]olor=#{color}>", "{{Color|#" + color + "|", content)

        this_scene_text += f"|文本={content}" + "}}\n"

        # print(this_scene_text)
        mw_text += this_scene_text

    return mw_text


def create_all():
    file_dict = {}
    for file_name in os.listdir(JSON_PATH):
        if not file_name.startswith("AvgConfig"):
            continue

        avg = file_name.split(".")[1]
        name = file_name.split(".")[2]
        if avg not in file_dict.keys():
            file_dict[avg] = {"config": "", "lang": ""}

        if name.startswith("AvgCfg"):
            file_dict[avg]["config"] = file_name
        elif name.startswith("AvgLang"):
            file_dict[avg]["lang"] = file_name

    for avg in file_dict.keys():
        if file_dict[avg]["config"] and file_dict[avg]["lang"]:

            try:
                with open(os.path.join(JSON_PATH, file_dict[avg]["config"]), "r", encoding="utf-8") as f_config:
                    config = ujson.load(f_config)
                    f_config.close()
                with open(os.path.join(JSON_PATH, file_dict[avg]["lang"]), "r", encoding="utf-8") as f_lang:
                    lang = ujson.load(f_lang)
                    f_lang.close()
            except:
                print(f"-- some {avg} file is not a json file")
                continue

            print(avg)
            wiki_text = create_mw(config, lang)
            with open(os.path.join(WIKI_PATH, avg + ".txt"), "w", encoding="utf-8") as f_output:
                f_output.write(wiki_text)
                f_output.close()
        else:
            print(f"-- can't find all {avg} files")
    return


def main():
    while True:
        mode = input("\n-- 请选择需要执行的程序 【1：源文件处理】【2：检查】【3：WIKI剧情文本创建】【4：退出】")

        if mode == "1":
            recognize_all()
        elif mode == "2":
            check()
        elif mode == "3":
            create_all()
        elif mode == "4":
            break
        else:
            print("-- 无法识别")
            main()


if __name__ == '__main__':
    main()

