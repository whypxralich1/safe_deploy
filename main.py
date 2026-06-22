import os
import sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    app_secret = os.getenv('APP_SECRET')
    if not app_secret:
        print ("ERROR:APP_SECRET environment veriable is not set!")
        print ("Please create .env file with APP_SECRET-your_secret_here")
        sys.exit(1)

    secret_hash = app_secret[:3] + '*' * (len(app_secret) - 3)
    print (f"System started. Secret hash: {secret_hash}")

if __name__ == "__main__":
    main() 
