import math
import random
import os
import re


class PasswordHasher():
    def __init__(self):
        self.ascii_list = [
            48+i for i in range(58-48)]+[65+i for i in range(91-65)]+[97+i for i in range(123-97)]

    def set_hash(self, pswd):

        self.ascii_str = ""
        self.a_list = []
        if pswd == '':
            pswd = '\n'
        self.pswd_list = [ord(pswd[i]) for i in range(len(pswd))]

        hash = ""

        for i in range(len(self.pswd_list)):
            self.pswd_list[i] = math.ceil(round(math.pow(round(math.log(round(
                self.pswd_list[i]*math.pi, 2), abs(round(math.tan(i+1), 2))), 2), 2), 2)*100)
            self.ascii_str += str(self.pswd_list[i])

        for x in range(len(self.ascii_str)):
            if self.ascii_str[x] == '1' and x <= (len(self.ascii_str)-3):
                self.a_list.append(int(self.ascii_str[x: x+3]))
            else:
                self.a_list.append(int(self.ascii_str[x: x+2]))

        for x in self.a_list:
            if x in self.ascii_list:
                hash += chr(x)
                if x == 92:
                    hash += '\\'
            else:
                x += 48
                if x in self.ascii_list:
                    hash += chr(x)
                    if x == 92:
                        hash += '\\'

        return hash

    def get_hash(self, pswd, check=0):

        self.check = check
        hash = self.set_hash(pswd)
        salt = self.set_hash(hash)

        final = salt+hash
        store = ""
        leftout = ""
        count = 0
        rand = random.randint(2, 10)

        if not self.check:
            self.check = rand

        while len(final) > 64:
            count += 1
            for i in range(0, len(final), self.check):
                store += final[i]
                try:
                    if count == 1:
                        leftout += final[i+1]
                except:
                    pass

            final = store
            store = ''

        while len(final) < 64:
            final += self.set_hash(leftout)[:64-len(final)]
            leftout = self.set_hash(leftout)

        return f"${self.check}${final}"


class PasswordStorer():
    def __init__(self):
        import file
        self.arr = file.arr

    def signup(self, key, hash):

        self.get_check_code(key)

        if self.key_got:
            print(
                'This email id and username is already signed up.. Try logging in instead..')
        else:
            if hash not in self.arr.values():
                self.arr[key] = hash

                with open(os.path.dirname(__file__)+"/file.py", 'w') as f:
                    f.write(f"arr= {self.arr}")
                print('You have signed up successfully..')

            else:
                print('Already logged in user..')

    def login(self, key, hash):

        self.get_check_code(key)

        if self.key_got:
            if self.arr[key] == hash:
                print('Successfully logged in..')
            else:
                print('Your password is wrong..')
        else:
            print('This email id or username is not signed up...')

    def get_check_code(self, key):
        try:
            code = int(re.findall('\$(\d+)\$', self.arr[key])[0])
        except:
            self.key_got = False
        else:
            self.key_got = True
            return code


if __name__ == '__main__':

    login = input('\n( Do you want to login(0) or signup(1) )>>> ')
    name = input('(Name)>>> ')
    email = input('(Email)>>> ')
    password = input('(Password)>>> ')

    obj = PasswordHasher()
    obj2 = PasswordStorer()

    check = obj2.get_check_code((name, email))

    if '0' in login or 'l' in login:
        obj2.login((name, email), obj.get_hash(password, check))
    else:
        obj2.signup((name, email), obj.get_hash(password))
