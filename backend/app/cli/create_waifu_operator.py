
import getpass
from app import create_app
from app.services.operator_accounts import create_operator, has_operator_accounts

def main():
    app=create_app()
    with app.app_context():
        if has_operator_accounts():
            print("An operator account already exists. Ask a super admin to create additional accounts from the dashboard.")
            return
        username=input("Super admin username: ").strip()
        password=getpass.getpass("Password (minimum 12 characters): ")
        confirm=getpass.getpass("Confirm password: ")
        if password != confirm:
            raise SystemExit("Passwords do not match.")
        create_operator(username,password,"super_admin")
        print("Super admin account created successfully.")

if __name__ == "__main__":
    main()
