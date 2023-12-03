import copy

def cpy(x):
    return copy.deepcopy(x)

chars = ['0','1','2','3','4','5','6','7','8','9','[',']',',','(',')'] #All necessary characters
nums = ['0','1','2','3','4','5','6','7','8','9'] #All the digits, I guess

class Array: #Array and separators
    def __init__(self, fentry = 0, seps = []):
        self.fentry = fentry #First entry
        self.seps = seps #Separators list
        
    def __str__(self):
        return f"{self.fentry}{''.join((',' if s.array.fentry == 0 and len(s.array.seps) == 0 else '[' + str(s.array) + ']') + str(s.entry) for s in self.seps)}"
    
    def __eq__(self, x):
        return self.compare(self, x) == 0
    def __gt__(self, x):
        return self.compare(self, x) == 1
    def __lt__(self, x):
        return self.compare(self, x) == -1
    def __ne__(self, x):
        return self.compare(self, x) != 0
    def __le__(self, x):
        return self.compare(self, x) != 1
    def __ge__(self, x):
        return self.compare(self, x) != -1
    
    @staticmethod
    def compare(a, b): #Compare arrays     
        a0 = 0
        b0 = 0
        if len(a.seps) == 0:
            a0 = 1
        if len(b.seps) == 0:
            b0 = 1
        if a0 and not b0:
            return -1
        if b0 and not a0:   
            return 1
        if a0 and b0:
            if a.fentry > b.fentry:   
                return 1
            elif a.fentry < b.fentry:  
                return -1
            else:   
                return 0
        
        i = 0
        aBig = a.seps[i]
        aBigPos = 0
        while i < len(a.seps):
            if Array.compare(a.seps[i].array, aBig.array) == 1:
                aBig = a.seps[i]
                aBigPos = i
            i += 1
            
        i = 0
        bBig = b.seps[i]
        bBigPos = 0
        while i < len(b.seps):
            if Array.compare(b.seps[i].array, bBig.array) == 1:
                bBig = b.seps[i]
                bBigPos = i
            i += 1
                  
        compBig = Array.compare(aBig.array, bBig.array)
        if compBig == 0:
            aBigRight = Array(aBig.entry, a.seps[aBigPos + 1:])
            bBigRight = Array(bBig.entry, b.seps[bBigPos + 1:])
            compRight = Array.compare(aBigRight, bBigRight)
            if compRight == 0:
                aBigLeft = Array(a.fentry, a.seps[:aBigPos])
                bBigLeft = Array(b.fentry, b.seps[:bBigPos])
                return Array.compare(aBigLeft, bBigLeft)
            else:
                return compRight
        else:
            return compBig
        
        return -2 #Error
    
    def simplify(self): #Remove leading 0s
        while len(self.seps) > 0 and self.seps[-1].entry == 0: #Remove leading 0s at the end
            self.seps.pop(-1)
        
        if len(self.seps) == 0:
            return self
        
        for i in range(len(self.seps)):
            self.seps[i].array.simplify()
        
        sepBig = self.seps[-1]
        i = -2
        while -i <= len(self.seps): #Remove leading 0s in the middle
            if self.seps[i].entry > 0:
                sepBig = cpy(self.seps[i])
                i -= 1
            elif self.seps[i].entry == 0:
                if self.seps[i].array >= sepBig.array:
                    sepBig = cpy(self.seps[i])
                    i -= 1
                else:
                    self.seps.pop(i)
        
        return self
    
    def map(self, mapper): #Map/diagonalize array
        i = 0
        while i < len(self.seps) and self.seps[i].entry == 0: #Find first non-0 entry
            i += 1
        
        if i >= len(self.seps): #Is array empty? (should never be the case, but you never know)
            return self.simplify()
        
        self.seps[i].entry -= 1
        if self.seps[i].array.fentry > 0: #Is separator's first entry greater than 0?
            new_array = cpy(self.seps[i].array)
            new_array.fentry -= 1
            self.seps[i:i] = [Separator(new_array, 0)] * (mapper - 1) + [Separator(new_array, 1)]
        elif self.seps[i].array.fentry == 0: #Does separator's first entry equal 0?
            if len(self.seps[i].array.seps) == 0: #Is it a comma?
                if i == 0:
                    self.fentry = mapper
                else:
                    self.seps[i - 1].entry = mapper
            else: #Or is it a limit separator?
                new_array = cpy(self.seps[i].array)
                new_array.map(mapper)
                self.seps.insert(i, Separator(new_array, 1))
    
        return self.simplify()

class Separator: #Separator
    def __init__(self, array = Array(0), entry = 0):
        self.array = array #Separator array
        self.entry = entry #Entry

class Expression:
    def __init__(self, parameter = 100, array = Array(), value = -1):
        self.value = value
        self.parameter = parameter
        self.array = array.simplify()
        
    def __str__(self):
        if self.value != -1:
            return str(self.value)
        return f"[{self.array}]{self.parameter}"
    
    def evaluate(self): #Evaluate expression
        if self.value != -1:
            return self
        
        while self.parameter.value == -1:
            self.parameter.evaluate()
            return self
        
        if self.array.fentry > 0:
            self.array.fentry -= 1
            oldp = self.parameter.value
            self.parameter = Expression(value = 10)
            for i in range(oldp):
                self.parameter = cpy(self)
        elif self.array.fentry == 0:
            if len(self.array.seps) == 0:
                self.value = 10 ** self.parameter.value
            else:
                self.array = self.array.map(self.parameter.value)
                self.parameter = Expression(value = 10)
        
        return self

def get_array(string): #String to array
    i = 0
    while i < len(string) and string[i] in nums:
        i += 1
    fentry = int(string[0:i]) #Get first entry
    
    seps = []
    while i < len(string):
        if string[i] == ',':
            array = Array(0)
        elif string[i] == '[':
            i += 1
            j = i
            k = 1 #Keeps count of square brackets
            while i < len(string) and k > 0:
                if string[i] == '[': 
                    k += 1
                elif string[i] == ']':
                    k -= 1
                i += 1
            i -= 1
            array = get_array(string[j:i])
        i += 1
        j = i
        while i < len(string) and string[i] in nums:
            i += 1
        entry = int(string[j:i]) #Get next entry
        seps.append(Separator(array, entry))
    
    return Array(fentry, seps)
    
def get_expression(string): #String to expression
    if string[0] in nums:
        return Expression(value = int(string))
    
    i = 1
    k = 1 #Keeps count of square brackets
    while i < len(string) and k > 0:
        if string[i] == '[': 
            k += 1
        elif string[i] == ']':
            k -= 1
        i += 1
    i -= 1
    array = get_array(string[1:i]) #Get array
    
    i += 1
    j = i
    if string[i] in nums: #Parameter is a number
        while i < len(string) and string[i] in nums:
            i += 1
    else: i = len(string) #Parameter is an expression  
    parameter = get_expression(string[j:i]) #Get parameter    
    
    return Expression(parameter, array)

def clear_expression(string):    
    output = ""
    for i in range(len(string)):
        if string[i] in chars: output += string[i] #Clear expression from unused characters
    
    return output

def clear_and_get_expression(string):
    string = clear_expression(string) #Clear expression from unused characters
    return get_expression(string)

while 1:
    expr = input("Insert expression to evaluate: ") #Ask for input
    expr = clear_and_get_expression(expr) #Turn into expression
    
    while 1: #Evaluate and ask if user wants to revaluate it
        print(f"Output: {expr.evaluate()}")
    
        if expr.value != -1:
            print("Expression evaluated to a number") #Was expression evaluated to a number?
            break
    
        rev = 0
        while 1:
            rev_input = input("Revaluate expression? (y/n) ")
            if rev_input == 'n':
                break
            if rev_input == 'y':
                rev = 1
                break
        if not rev:
            break
