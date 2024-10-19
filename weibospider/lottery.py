def read_nicknames_from_file(file_path):
    """
    从文件中读取昵称，忽略序号。
    """
    nicknames = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 假设昵称位于 ". " 之后，如 "1. nickname"
            nickname = line.strip().split('. ', 1)[-1]
            nicknames.add(nickname)
    return nicknames

def write_unique_lottery(nicknames, output_file):
    """
    将重复的昵称写入新文件，重新编号。
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for index, nickname in enumerate(sorted(nicknames), start=1):
            file.write(f"{index}. {nickname}\n")

def main():
    # 读取两个文件中的昵称
    nicknames_in_names = read_nicknames_from_file('unique_nick_names.txt')
    nicknames_in_comments = read_nicknames_from_file('unique_comments.txt')

    # 找到两个集合的交集，即重复的昵称
    common_nicknames = nicknames_in_names.intersection(nicknames_in_comments)

    # 将重复的昵称写入新文件，并重新编号
    write_unique_lottery(common_nicknames, 'unique_lottery.txt')
    print(f"Completed! Found {len(common_nicknames)} common nicknames.")

if __name__ == "__main__":
    main()
