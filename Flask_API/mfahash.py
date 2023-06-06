import hashlib
from datetime import datetime, timedelta

#This key will be updated with a secret key before deployment
SECRET_KEY = "your_secret_key"

# This is a method that gets the time and rounds it down to the nearest three minutes
# This time use used in generating a unique TFA code every 3 minutes
def generate_time_based_variable(time = datetime.now()):
    # unless a time is passed in, use the current time
    
    # This line of code is rounding the current time down to the nearest 3 minutes
    time_rounded = timedelta(minutes=time.minute % 3, seconds=time.second, microseconds=time.microsecond)
    # subtract the rounded time
    rounded_time = time - time_rounded
    # This variable will be used to generate the TFA code and will generate the same TFA Code
    # for 3 minutes
    return rounded_time

def generate_tfa_code(username):
    # Get the rounded down time
    rounded_time = generate_time_based_variable()

    # Convert the rounded time to a string with only the year, month, day, hour, and minute rounded down by 3
    # this formats the string to include 4 digit year, 2 digit month, 2 digit day, 2 digit hour, and 2 digit minute
    rounded_time_str = rounded_time.strftime("%Y%m%d%H%M")

    # Here the rounded down time is combined with a secret key before hashing
    message = f"{rounded_time_str}{SECRET_KEY}{username}"

    # Creating a hash
    hash_obj = hashlib.sha256(message.encode())
    # Converting hash to a string
    hash_str = hash_obj.hexdigest()

    # This will use only the first 6 characters of the hash for a code
    tfa_code = hash_str[:6]
    # print for testing
    # print(tfa_code)
    return tfa_code

# method that generates a hash for that is used in the validate_tfa method
def generate_hash(username, tfacode = None):
    # get the rounded time
    timestamp = generate_time_based_variable()
    # check to see if tfa code is none, if it is, generate a new one
    # when a tfa code is passed in that means the code came from
    # the user and is being validated
    # if no tfa code is passed in, we are using the current actual tfa code
    if tfacode is None:
        tfacode = generate_tfa_code(username)
    # this is the string we are going to hash
    message = f"{username}{tfacode}{SECRET_KEY}{timestamp}"

    # hash with hashlib
    hash_obj = hashlib.sha256(message.encode())
    #get a string representation of the hash
    hash_str = hash_obj.hexdigest()
    # print for testing
    # print(hash_str)
    return hash_str

# method that takes a username and tfa code and validates the tfa code
# and checks it agains the current hash for that user
def validate_tfa(username, tfacode):
    # get the hash for the provided username and tfa code
    provided_hash = generate_hash(username, tfacode)
    # get the actual hash for the username and the current tfa code
    actual_hash = generate_hash(username, generate_tfa_code(username))
    # compare the two hashes
    if provided_hash == actual_hash:
        return True
    else:
        return False

# calling these for testing
# print a tfa for a user
print(generate_tfa_code("test@test.com"))
# print the result of validating a user and their tfa code. If the code
# notice that each tfa code will only be valid for 3 minutes. If you want to modify
# the time interval, you can change the (minutes=current_time.minute % 3 to a different number
# in the generate_time_based_variable method
print(validate_tfa("test@test.com", "0adf16"))
