import os

import ujson

INPUT = "./input"
OUTPUT = "./output"

TARGET = "./luatable.txt"
TARGET_OUTPUT = "./output/lua2json.json"

LUA_PATH = "./a_lua"
JSON_PATH = "./b_json"
WIKI_PATH = "./c_wiki"


def lua2json(string):
    text = string

    # 空格处理
    count = 0
    quote_sign = -1
    while count < len(text):
        # print(count, quote_sign, text[count - 1], text[count - 0], text[count + 1])
        if text[count] == "\\" and text[count+1] == "\"":
            count += 1
        elif text[count] == "\"":
            quote_sign *= -1

        if quote_sign == 1:
            count += 1
            continue

        if text[count] == " " or text[count] == "\n":
            text = text[:count] + text[count+1:]
            count -= 1
        elif text[count] == "=":
            text = text[:count] + "\":" + text[count+1:]
        elif text[count] == ";":
            text = text[:count] + ",{\"" + text[count+1:]
            count += 2

            # ; 的处理 外加 {}
            stake = 0
            count_2 = count
            while count_2 < len(text) - 1:
                if text[count_2] == "{" or text[count_2] == "[":
                    stake += 1
                elif (text[count_2] == "}" or text[count_2] == "]") and stake >= 1:
                    stake -= 1
                if stake == 0 and (text[count:count_2].find("{") >= 0 or text[count:count_2].find("[") >= 0):
                    text = text[:count_2 + 1] + "}" + text[count_2 + 2:]
                    break
                count_2 += 1

        count += 1


    # keyname 的加引号处理 注意引号内内容不变
    count = 0
    quote_sign = -1
    while count < len(text) - 1:
        # print(count, quote_sign, text[count - 1], text[count - 0], text[count + 1])
        if text[count] == "\\" and text[count+1] == "\"":
            quote_sign *= -1
        if text[count] == "\"":
            quote_sign *= -1

        if quote_sign == 1:
            count += 1
            continue

        if text[count] == "{" and text[count + 1] not in ["{", "\"", "-"] and not text[count + 1].isdigit():
            text = text[:count+1] + "\"" + text[count+1:]
        elif text[count] == "," and text[count + 1] not in ["{", "\"", "-"] and not text[count + 1].isdigit():
            text = text[:count+1] + "\"" + text[count+1:]

        count += 1

    text = text.replace("{{", "[{")


    # 单个字符的处理 {} -> []
    count = 0
    count_a = 0
    count_b = 0
    while count < len(text):
        if text[count] == "{":
            count_a = count

        elif text[count] == "}":
            count_b = count
            text_split = text[count_a+1:count_b]
            if text_split.find(":") < 0 and text_split.find("}") < 0 and text_split.find("]") < 0:
                # print(count, text_split, text[:count_a], text_split, text[count_b+1:])
                text = text[:count_a] + "[" + text_split + "]" + text[count_b+1:]

        count += 1


    # 处理 {} -> []
    count = 0
    quote_sign = -1
    while count < len(text) - 1:
        if text[count] == "\\" and text[count+1] == "\"":
            count += 1
        if text[count] == "\"":
            quote_sign *= -1

        if quote_sign == 1:
            count += 1
            continue

        if text[count] == "}" and text[count + 1] == "}":
            stake = 0
            target = "}"
            count_2 = count
            while count_2 >= 0:
                if text[count_2] == "}" or text[count_2] == "]":
                    stake += 1
                elif (text[count_2] == "{" or text[count_2] == "[") and stake >= 1:
                    stake -= 1
                elif stake == 0 and text[count_2] == "{":
                    target = "}"
                    break
                elif stake == 0 and text[count_2] == "[":
                    target = "]"
                    break
                count_2 -= 1

            text = text[:count+1] + target + text[count+2:]
        count += 1

    return text


def convert():
    with open(TARGET, "r", encoding="utf-8") as f_1:
        string = f_1.read()
        dict_string = lua2json(string)
        f_1.close()

    print(dict_string)

    with open(TARGET_OUTPUT, "w", encoding="utf-8") as f_output:
        f_output.write(dict_string)

    return


def recognize_all():
    for file_name in os.listdir(LUA_PATH):
        print(file_name)
        with open(os.path.join(LUA_PATH, file_name), "r", encoding="utf-8") as f_input:
            string = recognize_lua_table(f_input.read())
            f_input.close()

        with open(os.path.join(JSON_PATH, file_name.replace(".lua", ".json")), "w", encoding="utf-8") as f_output:
            f_output.write(lua2json(string))
            f_output.close()
    return


def recognize_lua_table(string):
    start_local = string[string.find("local"):]
    start_equal = start_local[start_local.find("=")+1:]
    end_return = start_equal[:start_equal.find("return")-1]
    return end_return


def check():
    for file_name in os.listdir(JSON_PATH):
        try:
            with open(os.path.join(JSON_PATH, file_name), "r", encoding="utf-8") as f:
                string = ujson.load(f)
            print(f"√ {file_name}")
        except:
            print(f"× {file_name}")
    return


def main():
    while True:
        mode = input("\n-- 请选择执行的模式：【1：复制转换】【2：自动识别】【3：检查JSON】【4：模式说明】【5：退出】\n")
        if mode == "1":
            convert()
        elif mode == "2":
            recognize_all()
        elif mode == "3":
            check()
        elif mode == "4":
            print("   1.复制转换：请将local x = y 中的 y 字符串复制到 ./luatable.txt \n"
                  "   2.自动识别：请将对应剧情的 AvgLang 文件和 AvgCfg 文件粘贴到 ./input 文件夹下\n")
            main()
        elif mode == "5":
            return
        else:
            print("-- 无法识别")
            main()


if __name__ == '__main__':
    main()
