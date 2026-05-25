class LinkedList:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

def cons(head, tail=None):
    return LinkedList(head, tail)

def listToString(list):
    if list is None:
        return ""
    if list.tail is None:
        return str(list.head)
    return str(list.head) + " " + listToString(list.tail)

def myMap(fn, list):
    if list is None:
        return None
    return cons(fn(list.head), myMap(fn, list.tail))

def myReduce(fn, accm, list):
    if list is None:
        return accm
    return myReduce(fn, fn(accm, list.head), list.tail)

# solution
def myReduceRight(fn, accm, list):
    if list is None:
        return accm
    return fn(list.head, myReduceRight(fn, accm, list.tail))


# 测试
if __name__ == "__main__":
    exampleList = cons(1, cons(2, cons(3, cons(4))))

    # 测试1: myReduceRight(xTimesTwoPlusY, 0, exampleList) 应该返回 20
    def xTimesTwoPlusY(x, y):
        return 2 * x + y

    result1 = myReduceRight(xTimesTwoPlusY, 0, exampleList)
    print(f"myReduceRight(xTimesTwoPlusY, 0, exampleList) = {result1}")  # 20

    # 测试2: myReduceRight(unfoldCalculation, "accm", exampleList) 应该返回 fn(1, fn(2, fn(3, fn(4, accm))))
    def unfoldCalculation(x, y):
        return f"fn({x}, {y})"

    result2 = myReduceRight(unfoldCalculation, "accm", exampleList)
    print(f"myReduceRight(unfoldCalculation, 'accm', exampleList) = {result2}")  # fn(1, fn(2, fn(3, fn(4, accm))))

    # 测试3: myReduceRight(printXAndReturnY, 0, exampleList) 应该逆序打印 4 3 2 1
    def printXAndReturnY(x, y):
        print(x)
        return y

    print("逆序打印:")
    myReduceRight(printXAndReturnY, 0, exampleList)
