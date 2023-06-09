import hashlib
from datetime import datetime, timedelta

class TFA:
    def __init__(self, secret_key):
        # This key will be updated with a secret key before deployment
        self.SECRET_KEY = secret_key

    # This is a method that gets the time and rounds it down to the nearest three minutes
    # This time is used in generating a unique TFA code every 3 minutes
    def generate_time_based_variable(self, time = None):
        # unless a time is passed in, use the current time
        # strange bug here. I tried to set the default value of time to datetime.now()
        # however when I do this the time does not update. It is always the same time
        # as the first time it was called. I am not sure why this is happening
        # passing time as none and then setting it to datetime.now() has fixed the problem
        # this also only happened when the method was being called by the API. it did
        # not happen when I was testing the method in the python shell
        if time is None:
            time = datetime.now()
        # This line of code is rounding the current time down to the nearest 3 minutes
        time_rounded = timedelta(minutes=time.minute % 3, seconds=time.second, microseconds=time.microsecond)
        # subtract the rounded time
        rounded_time = time - time_rounded
        # This variable will be used to generate the TFA code and will generate the same TFA Code
        # for 3 minutes
        # print(rounded_time)
        return rounded_time

    def generate_tfa_code(self, username):
        # Get the rounded down time
        rounded_time = self.generate_time_based_variable()

        # Convert the rounded time to a string with only the year, month, day, hour, and minute rounded down by 3
        # this formats the string to include 4 digit year, 2 digit month, 2 digit day, 2 digit hour, and 2 digit minute
        rounded_time_str = rounded_time.strftime("%Y%m%d%H%M")
        # print(rounded_time_str)
        # Here the rounded down time is combined with a secret key before hashing
        message = f"{rounded_time_str}{self.SECRET_KEY}{username}"

        # Creating a hash
        hash_obj = hashlib.sha256(message.encode())
        # Converting hash to a string
        hash_str = hash_obj.hexdigest()

        # This will use only the first 6 characters of the hash for a code
        tfa_code = hash_str[:6]
        # print for testing
        # print(tfa_code)
        return tfa_code

    def generate_hash(self, username, tfacode=None):
        # get the rounded time
        timestamp = self.generate_time_based_variable()
        # check to see if tfa code is none, if it is, generate a new one
        # when a tfa code is passed in that means the code came from
        # the user and is being validated
        # if no tfa code is passed in, we are using the current actual tfa code
        if tfacode is None:
            tfacode = self.generate_tfa_code(username)
        # this is the string we are going to hash
        message = f"{username}{tfacode}{self.SECRET_KEY}{timestamp}"

        # hash with hashlib
        hash_obj = hashlib.sha256(message.encode())
        # get a string representation of the hash
        hash_str = hash_obj.hexdigest()
        # print for testing
        # print(hash_str)
        return hash_str

    def validate_tfa(self, username, tfacode):
        # get the hash for the provided username and tfa code
        provided_hash = self.generate_hash(username, tfacode)
        # get the actual hash for the username and the current tfa code
        actual_hash = self.generate_hash(username, self.generate_tfa_code(username))
        # compare the two hashes
        if provided_hash == actual_hash:
            return True
        else:
            return False

    def get_current_expiration(self):
        # get the current time
        current_time = datetime.now()
        # get the rounded time
        rounded_time = self.generate_time_based_variable(current_time)
        # add 3 minutes to the rounded time
        expiration = rounded_time + timedelta(minutes=3)
        # return the expiration time
        return expiration

