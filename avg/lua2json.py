import ujson


TARGET = "./luatable.txt"
OUTPUT = "./output/lua2json.json"



def lua2json(string):
    text = string

    # 空格处理
    count = 0
    quote_sign = -1
    while count < len(text):
        if text[count] == "\"":
            quote_sign *= -1

        if quote_sign == 1:
            count += 1
            continue

        if text[count] == " " or text[count] == "\n":
            text = text[:count] + text[count+1:]
            count -= 1
        elif text[count] == "=":
            text = text[:count] + "\":" + text[count+1:]

        count += 1


    # keyname 的加引号处理 注意引号内内容不变
    count = 0
    quote_sign = -1
    while count < len(text) - 1:
        # print(count, quote_sign, text[count - 1], text[count - 0], text[count + 1])
        if text[count] == "\"":
            quote_sign *= -1

        if quote_sign == 1:
            count += 1
            continue

        if text[count] == "{" and text[count + 1] != "{" and text[count + 1] != "\"":
            text = text[:count+1] + "\"" + text[count+1:]
        elif text[count] == "," and text[count + 1] != "{" and text[count + 1] != "\"":
            text = text[:count+1] + "\"" + text[count+1:]

        count += 1

    text = text.replace("{{", "[{")


    # 单个字符的处理 去掉大括号
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
                elif (text[count_2] == "{" or text[count_2] == "[") and stake == 1:
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


def main():
    with open(TARGET, "r", encoding="utf-8") as f_1:
        string = f_1.read()
        dict_string = lua2json(string)
        f_1.close()

    print(dict_string)

    with open(OUTPUT, "w", encoding="utf-8") as f_output:
        f_output.write(dict_string)


if __name__ == '__main__':
    main()

