class EmailOrPhoneBackend(BaseBackend):
    def authenticate(self, request, username, password, **kwargs):
        print(f"Authenticating: {username}")  # Log the input
        try:
            if '@' in username:  # Check if username is email
                user = MyUser.objects.get(email=username)
                print(f"User found by email: {user.email}")
            else:
                user = MyUser.objects.get(phone_number=username)
                print(f"User found by phone number: {user.phone_number}")

        except MyUser.DoesNotExist:
            print("User not found")  # Log if user not found
            return None

        # Verify password and check if user is active
        if user.check_password(password) and user.is_active:
            print("Authentication successful")  # Log successful authentication
            return user

        print("Invalid password or inactive user")  # Log password mismatch or inactive user
        return None
