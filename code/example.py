from googleSearch import GetParagraph

if __name__ == '__main__':
    q = input("please enter your question:")
    k = int(input("please enter your k:"))

    print(GetParagraph(q, k))
