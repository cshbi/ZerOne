with open("test.txt", "r", encoding="utf-8") as f: # r-읽기
    content = f.read()
    print(content)

user_input = input("저장할 문자열을 입력하세요: ")

with open("text.txt", "w", encoding="utf-8") as f: # w-쓰기
    f.write(user_input)

print("text.txt 파일에 저장했습니다.")