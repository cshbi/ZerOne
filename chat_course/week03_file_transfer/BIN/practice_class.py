# a= FourCal()

# a.setdata(4,2)

# print(a.add())
# print(a.mul())
# print(a.sub())
# print(a.div())

class FourCal:
    def __init__(self, first=0,second=0):
        self.first = first
        self.second = second
    def setdata(self, first, second):
        self.first = first
        self.second = second   
    def add(self):
        result = self.first + self.second
        return result
    def sub(self):
        result = self.first - self.second
        return result
    def mul(self):
        result = self.first * self.second
        return result
    def div(self):
        result = self.first / self.second
        return result
class MoreFourCal(FourCal): ##상속클래스
    def pow(self):
        result = self.first ** self.second
        return result
class SafefourCal(FourCal): #매소드 오버라이딩
    def div(self):
        if self.second ==0: #나눈값이 0이면 0으로 돌려줌
            return 0
        else:
            self.first / self.second        
a = FourCal(4,2) #a는 FouCal의 인스턴스로 선언
b = FourCal()
c = MoreFourCal(4,2)
# a.setdata(4,2) #초기값의 대입
# b.setdata(9,3)
# print(id(a.first)) #주소가 다름
# print(id(b.first))

a.setdata(4,2)
b.setdata(9,3)

print(a.add())
print(c.pow())
