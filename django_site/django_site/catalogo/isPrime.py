# define a function 
def isPrime(num): 
	# check for factors
    if num > 1: 
        for i in range(2,num):
            if (num % i) == 0: 
                return False
            else: 
                return True	
	# if input number is less than 
	# or equal to 1, it is not prime 
    else: 
        return False; 
    